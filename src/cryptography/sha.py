import struct

digest_size = 20
block_size = 64

def circular_shift(bin, k):
    # Left rotate a bin by k bits.
    return ((bin << k) | (bin >> (32 - k))) & 0xffffffff

def process_chunk(chunk, v0, v1, v2, v3, v4):

    bin = [0] * 80

    # Break chunk into sixteen 4-byte big-endian words w[i]
    for i in range(16):
        bin[i] = struct.unpack(b'>I', chunk[i*4:i*4+4])[0]

    # Extend the sixteen 4-byte words into eighty 4-byte words
    for i in range(16, 80):
        bin[i] = circular_shift(bin[i-3]^bin[i-8]^bin[i-14]^bin[i-16], 1)

    # Initialize hash value for this chunk
    a = v0
    b = v1
    c = v2
    d = v3
    e = v4

    for i in range(80):
        if 0 <= i <= 19:
            # Use alternative 1 for f from FIPS PB 180-1 to avoid bitwise not
            f = d ^ (b & (c ^ d))
            k = 0x5A827999
        elif 20 <= i <= 39:
            f = b ^ c ^ d
            k = 0x6ED9EBA1
        elif 40 <= i <= 59:
            f = (b & c) | (b & d) | (c & d)
            k = 0x8F1BBCDC
        elif 60 <= i <= 79:
            f = b ^ c ^ d
            k = 0xCA62C1D6

        a, b, c, d, e = ((circular_shift(a, 5) + f + e + k + bin[i]) & 0xffffffff,
                         a, circular_shift(b, 30), c, d)

    v0 = (v0 + a) & 0xffffffff
    v1 = (v1 + b) & 0xffffffff
    v2 = (v2 + c) & 0xffffffff
    v3 = (v3 + d) & 0xffffffff
    v4 = (v4 + e) & 0xffffffff

    return v0, v1, v2, v3, v4

def __init__(self):

    # bytes object with 0 <= len < 64 used to store the end of the message
    # if the message length is not congruent to 64
    self._unprocessed = b''
    # Length in bytes of all data that has been processed so far
    self._message_byte_length = 0

def hash(data, v):

    unprocessed = b''
    byte_length = 0

    idx_end = 64 - len(unprocessed)
    chunk = unprocessed +  str.encode(data[:idx_end])
    # print(chunk)

    idx_start = idx_end
    idx_end = idx_end + 64
    # Read the rest of the data, 64 bytes at a time
    while len(chunk) == 64:
        v = process_chunk(chunk, *v)
        byte_length += 64
        chunk = chunk[idx_start:idx_end]
        # print(chunk)

    unprocessed = chunk

    return unprocessed, byte_length, v

def digest(unprocessed, byte_length, v):
    # Produce the final hash value (big-endian) in bytes object"""
    return b''.join(struct.pack(b'>I', h) for h in process_digest(unprocessed, byte_length, v))

def hexdigest(unprocessed, byte_length, v):
    # Produce the final hash value (big-endian) in hex string"""
    return '%08x%08x%08x%08x%08x' % process_digest(unprocessed, byte_length, v)

def process_digest(unprocessed, byte_length,  v):
    # Return digest variables"""
    
    message = unprocessed
    byte_length = byte_length + len(message)

    message += b'\x80'
    message += b'\x00' * ((56 - (byte_length + 1) % 64) % 64)

    bit_length = byte_length * 8
    message += struct.pack(b'>Q', bit_length)

    v = process_chunk(message[:64], *v)
    if len(message) == 64:
        return v
    return process_chunk(message[64:], *v)

def sha1(data):

    v = (
            0x67452301,
            0xEFCDAB89,
            0x98BADCFE,
            0x10325476,
            0xC3D2E1F0,
        )

    unprocessed, byte_length, v = hash(data, v)
    
    return hexdigest(unprocessed, byte_length, v)

if __name__ == '__main__':

    data = "hello"
    print('sha1-digest:', sha1(data))