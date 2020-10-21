import flask
import PIL

import io
import functools
import math
import struct
import wave

app = flask.Flask(__name__)


@app.route("/")
def top():
    return "hoge"


@functools.lru_cache(maxsize=44100 * 3)
def synthe(x, freq, fs=44100):
    val = sum(
        0.2 * math.exp(-2 * i) * math.sin(x * 2 * math.pi * freq * (i + 1) / fs) * 32767
        for i in range(50)
    )
    return val


@app.route("/sin")
def gen_sin_wave():
    mod_freq = flask.request.args.get("mod_freq", default=100, type=int)
    fs = 44100
    t = 10

    sin_wave = [int(math.sin(x * 2 * math.pi * mod_freq / fs) * 32767) for x in range(fs * t)]
    bin_wave = struct.pack("h" * (fs * t), *sin_wave)

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
    fs = 44100
    t = 10

    sin_wave = [int(synthe(x % fs, 261) + synthe(x % fs, 329) + synthe(x % fs, 391)) for x in range(fs * t)]
    bin_wave = struct.pack("h" * (fs * t), *sin_wave)

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

    fs = 44100
    t = 10

    sin_wave = [int(32767 if ((x * mod_freq) % 44100 < 20000) else -32768) for x in range(fs * t)]
    bin_wave = struct.pack("h" * (fs * t), *sin_wave)

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

    fs = 44100
    t = 10

    sin_wave = [int(math.sin(x * 2 * math.pi * 8000 / fs) * 32767 if ((x * mod_freq) % 44100 < 20000) else 0) for x in range(fs * t)]
    bin_wave = struct.pack("h" * (fs * t), *sin_wave)

    temp = io.BytesIO()
    w = wave.Wave_write(temp)
    w.setparams((1, 2, fs, len(bin_wave), 'NONE', 'not compressed'))
    w.writeframes(bin_wave)
    w.close()

    resp = flask.make_response(temp.getvalue())
    resp.headers['Content-Type'] = "audio/wav"

    return resp
