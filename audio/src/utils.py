import os
import pathlib
import struct
import wave

import constants


def bytes_to_bits(bytes_value):
    return list(
        map(
            int,
            format(int.from_bytes(bytes_value, byteorder="big"), f'0{len(bytes_value) * 4}b')
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
                tree['children'].append(dict(name=str(item)))
    return tree


def save_audio_data(path, audio_data):
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
