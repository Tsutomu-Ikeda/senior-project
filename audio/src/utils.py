
def bytes_to_bits(bytes_value):
    return list(map(int,
                    format(
                        int.from_bytes(bytes_value, byteorder="big"),
                        f'0{len(bytes_value) * 4}b')))
