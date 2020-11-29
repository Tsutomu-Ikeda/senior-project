import datetime
import functools
import io
import itertools
import logging
import math
import pathlib
import struct
import wave

import flask
import werkzeug.serving
from gevent.pywsgi import WSGIServer
from geventwebsocket.handler import WebSocketHandler
from PIL import Image

import constants
import utils

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)-8s %(message)s'
)


app = flask.Flask(__name__)


@app.route("/")
def top():
    return flask.redirect("/app")


@functools.lru_cache(maxsize=constants.SAMPLING_RATE * 3)
def synthe(x, freq, fs=constants.SAMPLING_RATE):
    val = sum(
        0.2 * math.exp(-2 * i) * math.sin(x * 2 * math.pi * freq * (i + 1) / fs) * constants.SHORT_MAX_VAL
        for i in range(50)
    )
    return val


@functools.lru_cache(maxsize=constants.SAMPLING_RATE + 1)
def sigmoid(x):
    return (2 / (1 + math.e ** -x) - 1)


@functools.lru_cache(maxsize=constants.SAMPLING_RATE + 1)
def synthe_smooth_square(x, freq, fs=constants.SAMPLING_RATE):
    smooth_const = freq / 2
    smoothing_range = freq * 3
    if x < smoothing_range:
        return int(constants.SHORT_MAX_VAL * sigmoid(x / smooth_const))
    elif abs(x - 22050) < smoothing_range:
        return int(constants.SHORT_MAX_VAL * sigmoid((22050 - x) / smooth_const))
    elif x < 22050:
        return constants.SHORT_MAX_VAL
    elif x > constants.SAMPLING_RATE - smoothing_range:
        return int(-constants.SHORT_MAX_VAL * sigmoid((constants.SAMPLING_RATE - x) / smooth_const))
    else:
        return -32768


@ app.route("/sin")
def gen_wave_val():
    mod_freq = flask.request.args.get("mod_freq", default=100, type=int)
    fs = constants.SAMPLING_RATE
    t = 10

    wave_val = [int(math.sin(x * 2 * math.pi * mod_freq / fs) * constants.SHORT_MAX_VAL) for x in range(fs * t)]
    bin_wave = struct.pack(f"{fs * t}h", *wave_val)

    temp = io.BytesIO()
    w = wave.Wave_write(temp)
    w.setparams((1, 2, fs, len(bin_wave), 'NONE', 'not compressed'))
    w.writeframes(bin_wave)
    w.close()

    resp = flask.make_response(temp.getvalue())
    resp.headers['Content-Type'] = "audio/wav"

    return resp


@ app.route("/synthe")
def gen_wave():
    fs = constants.SAMPLING_RATE
    t = 10

    wave_val = [int(synthe(x % fs, 261) + synthe(x % fs, 329) + synthe(x % fs, 391)) for x in range(fs * t)]
    bin_wave = struct.pack(f"{fs * t}h", *wave_val)

    temp = io.BytesIO()
    w = wave.Wave_write(temp)
    w.setparams((1, 2, fs, len(bin_wave), 'NONE', 'not compressed'))
    w.writeframes(bin_wave)
    w.close()

    resp = flask.make_response(temp.getvalue())
    resp.headers['Content-Type'] = "audio/wav"

    return resp


@ app.route("/synthe_square")
def gen_square_wave():
    mod_freq = flask.request.args.get("mod_freq", default=2, type=int)

    fs = constants.SAMPLING_RATE
    t = 10

    wave_val = [int(constants.SHORT_MAX_VAL if ((x * mod_freq) % constants.SAMPLING_RATE < 20000) else -32768) for x in range(fs * t)]
    bin_wave = struct.pack(f"{fs * t}h", *wave_val)

    temp = io.BytesIO()
    w = wave.Wave_write(temp)
    w.setparams((1, 2, fs, len(bin_wave), 'NONE', 'not compressed'))
    w.writeframes(bin_wave)
    w.close()

    resp = flask.make_response(temp.getvalue())
    resp.headers['Content-Type'] = "audio/wav"

    return resp


@ app.route("/synthe_smooth_square")
def gen_smooth_square_wave():
    mod_freq = flask.request.args.get("mod_freq", default=10, type=int)

    fs = constants.SAMPLING_RATE
    t = 10

    wave_val = [synthe_smooth_square((x * mod_freq) % constants.SAMPLING_RATE, mod_freq) for x in range(fs * t)]
    bin_wave = struct.pack(f"{fs * t}h", *wave_val)

    temp = io.BytesIO()
    w = wave.Wave_write(temp)
    w.setparams((1, 2, fs, len(bin_wave), 'NONE', 'not compressed'))
    w.writeframes(bin_wave)
    w.close()

    resp = flask.make_response(temp.getvalue())
    resp.headers['Content-Type'] = "audio/wav"

    return resp


@ app.route("/all_one")
def get_all_one_wave():
    fs = constants.SAMPLING_RATE
    t = 10

    wave_val = [constants.SHORT_MAX_VAL for x in range(fs * t)]
    bin_wave = struct.pack(f"{fs * t}h", *wave_val)

    temp = io.BytesIO()
    w = wave.Wave_write(temp)
    w.setparams((1, 2, fs, len(bin_wave), 'NONE', 'not compressed'))
    w.writeframes(bin_wave)
    w.close()

    resp = flask.make_response(temp.getvalue())
    resp.headers['Content-Type'] = "audio/wav"

    return resp


@ app.route("/ook")
def gen_on_off_keying():
    mod_freq = flask.request.args.get("mod_freq", default=2, type=int)

    fs = constants.SAMPLING_RATE
    t = 10

    wave_val = [int(math.sin(x * 2 * math.pi * 8000 / fs) * constants.SHORT_MAX_VAL if ((x * mod_freq) % constants.SAMPLING_RATE < 20000) else 0) for x in range(fs * t)]
    bin_wave = struct.pack(f"{fs * t}h", *wave_val)

    temp = io.BytesIO()
    w = wave.Wave_write(temp)
    w.setparams((1, 2, fs, len(bin_wave), 'NONE', 'not compressed'))
    w.writeframes(bin_wave)
    w.close()

    resp = flask.make_response(temp.getvalue())
    resp.headers['Content-Type'] = "audio/wav"

    return resp


@app.route('/gen_audio_signal', methods=['POST'])
def gen_audio_signal():
    if not (file := flask.request.files.get('file')):
        return "Bad Request", 400

    body = file.stream.read()

    temp = io.BytesIO()
    image = Image.open(io.BytesIO(body))
    image.save(temp, dpi=(350, 350), format="jpeg")

    fs = constants.SAMPLING_RATE

    arr_bits = utils.bytes_to_bits(temp.getvalue())

    def get_fragment(prev_val, curr_val, next_val):
        if curr_val is None:
            return []

        val = constants.SHORT_MAX_VAL * (curr_val * 2 - 1)

        if prev_val == curr_val or prev_val is None:
            yield from itertools.repeat(val, 2)
        else:
            # 立ち上がり/立ち下がりの部分
            yield from [int(val * 0.6), val]

        # 真ん中の部分
        yield from itertools.repeat(val, 1)

        if next_val == curr_val or next_val is None:
            yield from itertools.repeat(val, 2)
        else:
            # 立ち上がり/立ち下がりの部分
            yield from [val, int(val * 0.6)]

    def prev_arr():
        yield None
        yield None
        yield from constants.PREAMBLE
        yield from arr_bits

    def curr_arr():
        yield None
        yield from constants.PREAMBLE
        yield from arr_bits
        yield None

    def next_arr():
        yield from constants.PREAMBLE
        yield from arr_bits
        yield None
        yield None

    wave_val = list(itertools.repeat(0, 100)) + list(itertools.chain.from_iterable(
        get_fragment(prev_val, curr_val, next_val)
        for prev_val, curr_val, next_val
        in zip(prev_arr(), curr_arr(), next_arr())
    ))
    bin_wave = struct.pack(f"{len(wave_val)}h", *wave_val)

    temp = io.BytesIO()
    w = wave.Wave_write(temp)
    w.setparams((1, 2, fs, len(bin_wave), 'NONE', 'not compressed'))
    w.writeframes(bin_wave)
    w.close()

    resp = flask.make_response(temp.getvalue())
    resp.headers['Content-Type'] = "audio/wav"

    return resp


@app.route('/gen_audio_ook', methods=['POST'])
def gen_audio_ook():
    if not (file := flask.request.files.get('file')):
        return "Bad Request", 400

    body = file.stream.read()
    print(len(body))

    fs = constants.SAMPLING_RATE

    arr_bits = utils.bytes_to_bits(body)
    one_bit_length = 8

    def get_fragment(val):
        if val == 1:
            yield from (int(math.sin(2 * math.pi * x / one_bit_length) * constants.SHORT_MAX_VAL) for x in range(one_bit_length))
        else:
            yield from itertools.repeat(0, one_bit_length)

    def get_array():
        yield from constants.PREAMBLE
        yield from arr_bits

    wave_val = list(itertools.chain.from_iterable(
        get_fragment(val)
        for val
        in get_array()
    ))
    bin_wave = struct.pack(f"{len(wave_val)}h", *wave_val)

    temp = io.BytesIO()
    w = wave.Wave_write(temp)
    w.setparams((1, 2, fs, len(bin_wave), 'NONE', 'not compressed'))
    w.writeframes(bin_wave)
    w.close()

    resp = flask.make_response(temp.getvalue())
    resp.headers['Content-Type'] = "audio/wav"

    return resp


@app.route("/upload", methods=["POST"])
def handle_upload():
    file = flask.request.files['file']
    if file and file.filename.lower().endswith(".wav"):
        filename = file.filename
        file.save(pathlib.Path("./static") / filename)
    return "OK"


@app.route('/pipe')
def pipe():
    ws = flask.request.environ['wsgi.websocket']
    if ws:
        # recorded_wave = './static/2020-10-28-08-19-44.wav'
        # recorded_wave = './static/doraemon2.wav'
        # wr = wave.open(recorded_wave, 'r')
        # wave_buffer = wr.readframes(-1)
        # data = struct.unpack(f"{len(wave_buffer)//2}h", wave_buffer)
        # wr.close()

        audio_data = []
        VAL_THRESHOLD = int(constants.SHORT_MAX_VAL * 0.4)
        last_edge = -1
        decoded_values = ""
        last_decoded_seek = 0
        last_send_seek = -1
        image_buffer_size = 24 * 15
        last_seek = 1

        printed = False

        while True:
            if (message := ws.receive()) is None:
                print('websocket connetion closed')
                if audio_data:
                    with open(f'static/{datetime.datetime.now():%Y-%m-%d-%H-%M-%S}.wav', 'wb') as f:
                        wf = wave.Wave_write(f)
                        max_amp = max(max(audio_data), -min(audio_data))
                        if max_amp > constants.SHORT_MAX_VAL:
                            audio_data = list(map(lambda x: int(x / max_amp * constants.SHORT_MAX_VAL), audio_data))
                        bin_wave = struct.pack(f"{len(audio_data)}h", *audio_data)
                        wf.setparams((1, 2, constants.SAMPLING_RATE, len(bin_wave), 'NONE', 'not compressed'))
                        wf.writeframes(bin_wave)
                        wf.close()
                break

            if message:
                receveied = [int(val * constants.SHORT_MAX_VAL) for val in struct.unpack(f"{len(message)//4}f", message)]
                len_received = len(receveied)
                audio_data.extend(receveied)

                if len_received > 0:
                    for j in range(last_seek, len(audio_data)):
                        if (last_edge == -1 or decoded_values[-1] == '0') and audio_data[j] > VAL_THRESHOLD:
                            if last_edge > -1:
                                if j - last_edge >= (5 + 1) * 2 - 1:
                                    decoded_values += '0' * (math.floor((j - last_edge - (5 + 1) * 2) / 5) + 1)
                            last_edge = j
                            decoded_values += '1'
                            continue

                        if (last_edge == -1 or decoded_values[-1] == '1') and audio_data[j] < -VAL_THRESHOLD:
                            if last_edge > -1:
                                if j - last_edge >= (5 - 1) * 2 - 1:
                                    decoded_values += '1' * (math.floor((j - last_edge - ((5 - 1) * 2 - 1)) / 5) + 1)
                            last_edge = j
                            decoded_values += '0'
                            continue

                    if not printed and decoded_values:
                        print(constants.STR_PREAMBLE, len(constants.STR_PREAMBLE))
                        print(decoded_values[:100])
                        print(audio_data[last_seek:last_seek + 512])
                        printed = True
                    last_seek = len(audio_data)

                    PREAMBLE_LEN = 36
                    index = decoded_values.find(constants.STR_PREAMBLE[-PREAMBLE_LEN:], max(0, last_decoded_seek - PREAMBLE_LEN))

                    if index > -1:
                        print("PREAMBLE detected")
                        print(decoded_values[index:index + 100])
                        last_send_seek = index + PREAMBLE_LEN

                    last_decoded_seek = len(decoded_values)

                    if last_send_seek > -1:
                        length = ((len(decoded_values) - last_send_seek) // image_buffer_size) * image_buffer_size
                        if length > 0:
                            bits = decoded_values[last_send_seek:last_send_seek + length]
                            last_send_seek += length
                            ws.send(bytes(list(int(bits, 2).to_bytes(len(bits) // 8, 'big'))))
                # else:
                #     if last_send_seek > -1:
                #         length = (len(decoded_values) - last_send_seek)
                #         if length > 0:
                #             bits = decoded_values[last_send_seek:last_send_seek + length]
                #             padded = bits + '0' * (8 - len(bits) % 8)
                #             last_send_seek += length
                #             ws.send(bytes(list(int(padded, 2).to_bytes(len(padded) // 8, 'big'))))

                #     if ws:
                #         ws.close()
                #         break

    return ""


@app.route("/app")
def app_top():
    return flask.render_template('index.html')


@app.route("/app/sender")
def app_sender():
    return flask.render_template('sender.html')


@ app.route("/app/receiver")
def app_receiver():
    return flask.render_template('receiver.html')


@app.route("/app/dir")
def dirtree():
    path = pathlib.Path("./static/")
    return flask.render_template('dirtree.html', tree=utils.make_tree(path))


@werkzeug.serving.run_with_reloader
def runServer():
    app.debug = True
    http_server = WSGIServer(('', 8080), app, handler_class=WebSocketHandler)
    http_server.serve_forever()


if __name__ == "__main__":
    runServer()
