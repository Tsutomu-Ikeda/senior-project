import utils

PREAMBLE = utils.bytes_to_bits(b'\xaa\xaa\xaa^_^')
STR_PREAMBLE = "".join(str(i) for i in PREAMBLE)

SAMPLING_RATE = 48000
BUFFER_SIZE = 16384

SHORT_MAX_VAL = 32767
