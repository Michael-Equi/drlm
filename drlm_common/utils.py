def rgb_to_hex(r, g, b):
    assert r < 256 and g < 256 and b < 256
    return r << 16 | g << 8 | b


def hex_to_rgb(v):
    return (v >> 16) & 0b11111111, (v >> 8) & 0b11111111, v & 0b11111111
