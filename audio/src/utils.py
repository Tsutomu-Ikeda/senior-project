import datetime
import io
import itertools
import math
import os
import pathlib
import struct
from typing import Callable, Generator, Iterable, List, Literal
import wave
import numpy as np

import constants


def bytes_to_bits(bytes_value):
    return list(
        map(
            int,
            format(int.from_bytes(bytes_value, byteorder="big"), f'0{len(bytes_value) * 8}b')
        )
    )


def make_tree(path):
    tree = dict(name=os.path.basename(path), children=[])
    try:
        lst = sorted(pathlib.Path(path).iterdir(), key=lambda item: str(item), reverse=True)
    except OSError:
        pass  # ignore errors
    else:
        for item in lst:
            if ".DS_Store" in str(item):
                continue
            if item.is_file():
                tree['children'].append(dict(name=str(item), short_name=str(item).replace('static/audio/', '')))

    return tree


def save_audio_data(audio_data):
    path = f'static/audio/{datetime.datetime.now():%Y-%m-%d-%H-%M-%S}.wav'
    if not audio_data:
        return

    with open(path, 'wb') as f:
        wf = wave.Wave_write(f)
        max_amp = max(max(audio_data), -min(audio_data))
        if max_amp > constants.SHORT_MAX_VAL:
            audio_data = list(map(lambda x: int(x / max_amp * constants.SHORT_MAX_VAL), audio_data))
        bin_wave = struct.pack(f"{len(audio_data)}h", *audio_data)
        wf.setparams((1, 2, constants.SAMPLING_RATE, len(bin_wave), 'NONE', 'not compressed'))
        wf.writeframes(bin_wave)
        wf.close()


def create_wavedata(image_bytes):
    """
    サブキャリアによる変調
    """
    fs = constants.SAMPLING_RATE  # サンプリング周波数 48,000Hz
    sub_career_freq = constants.SAMPLING_RATE // 10  # 搬送波周波数 4,800Hz

    def get_fragment(val):
        if val == 1:
            yield from (
                int(math.sin(
                    2 * math.pi * x / (fs // sub_career_freq)
                ) * constants.SHORT_MAX_VAL)
                for x
                in range(constants.ONE_BIT_SAMPLES)
            )
        else:
            yield from itertools.repeat(0, constants.ONE_BIT_SAMPLES)

    def get_bits():
        size_info_bytes = len(image_bytes).to_bytes(2, 'big')

        yield from constants.PREAMBLE
        yield from bytes_to_bits(size_info_bytes)
        # 画像のバイト列を1と0のビット列へ変換する
        yield from bytes_to_bits(image_bytes)

    def get_bytes():
        yield from [0] * (constants.ONE_BIT_SAMPLES // 2)
        yield from itertools.chain.from_iterable(
            get_fragment(val)
            for val
            in get_bits()
        )

    wave_val = list(get_bytes())
    bin_wave = struct.pack(f"{len(wave_val)}h", *wave_val)

    temp = io.BytesIO()
    w = wave.Wave_write(temp)
    w.setparams((1, 2, fs, len(bin_wave), 'NONE', 'not compressed'))
    w.writeframes(bin_wave)
    w.close()

    return temp.getvalue()


def make_chunks(iterator, size, fillvalue=None):
    return itertools.zip_longest(*[iterator] * size, fillvalue=fillvalue)


def find_continuous_zero(array: List[float]):
    threshold = 20

    j = 0

    for i in range(len(array)):
        if array[i] == 0:
            j += 1
            if j >= threshold:
                count = threshold
                while i + 1 < len(array) and array[i + 1] == 0:
                    i += 1
                    count += 1
                return i - count + 1, count
        else:
            j = 0

    return False, 0


def receive(ws, is_mock, data_type, callback):
    if is_mock:
        if data_type == "image":
            recorded_wave = './static/audio/doraemon-ook2.wav'
        else:
            recorded_wave = './static/audio/吾輩は猫である.wav'
        wr = wave.open(recorded_wave, 'r')
        wave_buffer = wr.readframes(-1)
        recorded_data = list(struct.unpack(f"{len(wave_buffer)//2}h", wave_buffer))
        wr.close()
        while True:
            if (message := ws.receive()) is None:
                return

            if recorded_data[:len(message) // 4]:
                data = recorded_data[:len(message) // 4]
                yield from data

                del recorded_data[:len(message) // 4]
            else:
                return
    else:
        while True:
            if (message := ws.receive()) is None:
                print('websocket connetion closed')
                return

            received = [int(val * constants.SHORT_MAX_VAL) for val in struct.unpack(f"{len(message)//4}f", message)]
            (index, count) = find_continuous_zero(received)
            while index:
                del received[index:index + count]
                (index, count) = find_continuous_zero(received)
            callback(received)
            yield from received


def get_bits(receive: Generator[float, None, None], power_threshold: int) -> Generator[Literal["1", "0"], None, None]:
    audio_data = []
    Lf = constants.ONE_BIT_SAMPLES * 2
    half_sample = constants.ONE_BIT_SAMPLES // 2
    overlap = constants.ONE_BIT_SAMPLES
    win_func = np.hanning(Lf)

    last_j = overlap
    is_receiving = False
    phase_adjust = None
    target_band = 2

    for (j, data) in enumerate(receive):
        audio_data.append(data)
        if j - last_j >= overlap and (not phase_adjust or j + phase_adjust <= len(audio_data)):
            def get_target():
                if phase_adjust:
                    return audio_data[j - Lf + phase_adjust:j + phase_adjust] * win_func
                else:
                    return audio_data[j - Lf:j] * win_func

            spectrogram = np.fft.rfft(get_target(), n=Lf, axis=0)
            a = np.abs(spectrogram)

            if a[target_band] > power_threshold:
                phase_diff = np.angle(spectrogram[target_band])
                center_width = 3.14 / half_sample
                if is_receiving and phase_diff >= center_width / 2:
                    last_j = j - 1
                elif is_receiving and phase_diff <= -center_width / 2:
                    last_j = j + 1
                else:
                    last_j = j
                if not is_receiving:
                    phase_adjust = -int(np.angle(spectrogram[target_band]) * half_sample / 3.14)
                is_receiving = True
                yield "1"
            elif is_receiving:
                last_j = j
                yield "0"


def bits_iter(audio_data: Iterable, power_threshold: int) -> Generator[Literal["1", "0"], None, None]:
    is_preamble_detected = False
    bits = ""
    for bit in get_bits(audio_data, power_threshold):
        bits += bit
        if is_preamble_detected:
            yield bit
        elif bits.find(constants.STR_PREAMBLE[3:], len(bits) - len(constants.STR_PREAMBLE[3:])) > -1:
            is_preamble_detected = True


def get_bytes(audio_data: Iterable, power_threshold: int, set_size: Callable[[int], None]) -> Generator[bytes, None, None]:
    entire_bytes = b""
    bytes_count = 0
    data_size = None
    header_size = 2

    for c in make_chunks(bits_iter(audio_data, power_threshold), 8, ""):
        bytes_count += 1
        bits = "".join(c)
        data_bytes = bytes(list(int(bits, 2).to_bytes(1, 'big')))
        entire_bytes += data_bytes

        if (bytes_count == header_size):
            data_size = int.from_bytes(entire_bytes, 'big')
            set_size(data_size)
        elif (bytes_count > header_size):
            yield data_bytes

        if data_size is not None and (bytes_count - header_size) >= data_size:
            break
