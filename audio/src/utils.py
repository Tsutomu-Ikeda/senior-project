import pathlib
import os


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
