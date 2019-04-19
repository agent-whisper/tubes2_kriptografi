import hashlib
import secrets

from src.utilities.matdis.mod_op import modinv
from src.utilities.matdis.prime_op import is_prime
from src.cryptography.elliptic_curve import EllipticCurve, EllipticCurveOp, Point

test_curve = EllipticCurve(1, 6, 11, lambda x: x**3 + x + 6, order=13)

def sign(message, priv_key, elliptic_curve, base_point=None):
    if base_point is None:
        G = elliptic_curve.generate_base_point()
    else:
        G = base_point
    n = elliptic_curve.order
    
    if not elliptic_curve.contains_point(G):
        return 'Invalid base point'
    elif n is None or not is_prime(n):
        return 'Order of G is not prime'

    # Step 1
    # TODO: hash message with sha1
    e = conv_digest_to_int(gen_digest(message))

    # Step 2
    Ln = n.bit_length()
    z = e >> (e.bit_length() - n)

    r = 0
    s = 0
    while r == 0 or s == 0:
        # Step 3
        k = 0
        while k == 0:
            k = secrets.randbelow(n)
        
        # Step 4
        curve_point = EllipticCurveOp.multiply_point(k, G, elliptic_curve)

        # Step 5
        r = curve_point.x % n
        if r == 0:
            continue
        
        # Step 6
        s = ((modinv(k, n)) * (z + r * priv_key) % n) % n
    return Point(r, s)

def verify(a, b, p, k, pubkey_point, message, signature):
    pass

def gen_digest(message):
    sha1 = hashlib.sha1()
    if hasattr(message, 'encode'):
        message = message.encode()
    sha1.update(message)
    return sha1.digest()

def conv_digest_to_int(digest):
    hex_string = digest.hex()
    return int(hex_string, 16)