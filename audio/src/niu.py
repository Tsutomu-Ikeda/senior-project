
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


@app.route("/sin")
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


@app.route("/synthe")
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


@app.route("/np")
def get_np():
    recorded_wave = './static/2020-11-09-08-03-38_sophia.wav'
    wr = wave.open(recorded_wave, 'r')
    wave_buffer = wr.readframes(-1)
    recorded_data = list(struct.unpack(f"{len(wave_buffer)//2}h", wave_buffer))
    wr.close()
    return str(list(abs(f) for f in np.fft.fft(recorded_data)))


@app.route("/synthe_square")
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


@app.route("/synthe_smooth_square")
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


@app.route("/all_one")
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


@app.route("/ook")
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
