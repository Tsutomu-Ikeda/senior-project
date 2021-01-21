import utils

PREAMBLE = utils.bytes_to_bits(b'\xfa\xaa\xaa^_^')
STR_PREAMBLE = "".join(str(i) for i in PREAMBLE)

SAMPLING_RATE = 48000
BUFFER_SIZE = 16384
ONE_BIT_SAMPLES = 10  # 1ビットを表現するのに使用するフレーム数

LIMIT_BYTES = 65535  # 送信データの上限 65535 bytes

SHORT_MAX_VAL = 32767
