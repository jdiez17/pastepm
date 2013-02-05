BASE = 24

def encode_id(num):
    def encode_digit(d):
        if d < 10:
            return chr(ord('0') + d)
        else:
            return chr(ord('a') + d - 10)

    (d, m) = divmod(num, BASE)
    if d:
        return encode_id(d) + encode_digit(m)
    else:
        return encode_digit(m)

decode_id = lambda id: int(id, BASE)
