import flask
from geventwebsocket.handler import WebSocketHandler
from gevent.pywsgi import WSGIServer
import werkzeug.serving

import datetime
import io
import itertools
import logging
import functools
import math
import pathlib
import struct
import wave

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
    print(len(body))

    fs = constants.SAMPLING_RATE

    arr_bits = utils.bytes_to_bits(body)

    def get_fragment(prev_val, curr_val, next_val):
        if curr_val is None:
            return []

        val = constants.SHORT_MAX_VAL * (curr_val * 2 - 1)

        if prev_val == curr_val or prev_val is None:
            yield from itertools.repeat(val, 3)
        else:
            # 立ち上がり/立ち下がりの部分
            yield from [int(val * 0.4), int(val * 0.8), val]

        # 真ん中の部分
        yield from itertools.repeat(val, 4)

        if next_val == curr_val or next_val is None:
            yield from itertools.repeat(val, 3)
        else:
            # 立ち上がり/立ち下がりの部分
            yield from [val, int(val * 0.8), int(val * 0.4)]

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

    wave_val = list(itertools.chain.from_iterable(
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


@app.route('/pipe')
def pipe():
    ws = flask.request.environ['wsgi.websocket']
    if ws:
        png_image = pathlib.Path('image.jpg')
        data = png_image.read_bytes()
        chunk_size = 1002
        i = 0
        audio_data = []

        while True:
            if (message := ws.receive()) is None:
                print('websocket connetion closed')
                if audio_data:
                    with open(f'static/{datetime.datetime.now():%Y-%m-%d-%H-%M-%S}.wav', 'wb') as f:
                        wf = wave.Wave_write(f)
                        print(len(audio_data))
                        bin_wave = struct.pack(f"{len(audio_data)}h", *audio_data)
                        wf.setparams((1, 2, constants.SAMPLING_RATE, len(bin_wave), 'NONE', 'not compressed'))
                        wf.writeframes(bin_wave)
                        wf.close()
                break

            if i < len(data):
                ws.send(data[i:i + chunk_size])
                i += chunk_size

            if message:
                arr = [int(val * constants.SHORT_MAX_VAL) for val in struct.unpack(f"{constants.BUFFER_SIZE}f", message)]
                audio_data.extend(arr)

    return ""


@app.route("/app")
def app_top():
    return flask.render_template('index.html')


@app.route("/app/sender")
def app_sender():
    return flask.render_template('sender.html')


@app.route("/app/receiver")
def app_receiver():
    return flask.render_template('receiver.html')


@werkzeug.serving.run_with_reloader
def runServer():
    app.debug = True
    http_server = WSGIServer(('', 8080), app, handler_class=WebSocketHandler)
    http_server.serve_forever()


if __name__ == "__main__":
    runServer()
