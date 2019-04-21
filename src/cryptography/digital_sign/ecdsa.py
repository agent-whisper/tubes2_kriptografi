import hashlib
import secrets

from src.cryptography.sha import sha1
from src.utilities.matdis.mod_op import modinv
from src.utilities.matdis.prime_op import is_prime
from src.cryptography.elliptic_curve import EllipticCurve, EllipticCurveOp, Point

test_curve = EllipticCurve(1, 6, 11, lambda x: x**3 + x + 6, order=13)

def generate_keys(elliptic_curve, base_point=None):
    try:
        G, n = initialize(elliptic_curve, base_point=base_point)
    except ValueError as e:
        return False

    dA = 0
    while dA == 0:
        dA = secrets.randbelow(n)

    Qa = EllipticCurveOp.multiply_point(dA, G, elliptic_curve)
    return dA, str(Qa)

def sign(message, dA, elliptic_curve, base_point=None):
    try:
        G, n = initialize(elliptic_curve, base_point=base_point)
    except ValueError as e:
        return str(e)

    # Step 1
    # TODO: hash message with sha1
    e = conv_digest_to_int(gen_digest(message))

    # Step 2
    Ln = n.bit_length()
    z = e >> (e.bit_length() - Ln)

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
        s = ((modinv(k, n)) * (z + r * dA) % n) % n
    return str(Point(r, s))

def verify(message, signature, pub_point, elliptic_curve, base_point=None):
    try:
        G, n = initialize(elliptic_curve, base_point=base_point)
    except ValueError as e:
        return str(e)

    # Check Qa is a valid point
    Qa = parse_point(pub_point)
    Qa_is_valid = not elliptic_curve.is_identity(Qa) and elliptic_curve.contains_point(Qa) \
        and EllipticCurveOp.multiply_point(n, Qa, elliptic_curve)
    if not Qa_is_valid:
        return False

    # Step 1
    sign_point = parse_point(signature)
    r = sign_point.x
    s = sign_point.y
    if (r < 1 or r >= n) or (s < 1 or s >= n):
        return False
    
    # Step 2
    # TODO: hash message with sha1
    e = conv_digest_to_int(gen_digest(message))

    # Step 3
    Ln = n.bit_length()
    z = e >> (e.bit_length() - Ln)

    # Step 4
    w = modinv(s, n)

    # Step 5
    u1 = (z*w) % n
    u2 = (r*w) % n

    # Step 6
    curve_point = EllipticCurveOp.sum_point( EllipticCurveOp.multiply_point(u1, G, elliptic_curve), \
        EllipticCurveOp.multiply_point(u2, Qa, elliptic_curve), elliptic_curve )
    if elliptic_curve.is_identity(curve_point):
        return False
    
    # Step 7
    return (r % n) == (curve_point.x % n)
    
def initialize(elliptic_curve, base_point=None):
    if base_point is None:
        G = elliptic_curve.generate_base_point()
    else:
        G = base_point
    n = elliptic_curve.order
    
    if not elliptic_curve.contains_point(G):
        raise ValueError('Invalid base point')
    elif n is None or not is_prime(n):
        raise ValueError('Order of G is not prime')
    
    return G, n

def parse_point(pub_point):
    if isinstance(pub_point, Point):
        return pub_point
    elif isinstance(pub_point, str):
        coordinate = pub_point.split(',')
        try:
            return Point(int(coordinate[0]), int(coordinate[1]))
        except (ValueError, IndexError) as e:
            print(str(e))
            return None
    else:
        return None

def gen_digest(message):
    if hasattr(message, 'decode'):
        message = message.decode()
    return sha1(message)

def conv_digest_to_int(digest):
    return int(digest, 16)
