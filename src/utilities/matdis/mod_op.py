def modinv(e, m):
    """ Returns the d that fulfills e*d == 1 (mod p)
    reference: https://stackoverflow.com/questions/4798654/modular-multiplicative-inverse-function-in-python
    """
    g, x, y = egcd(e, m)
    if g != 1:
        raise Exception('modular inverse does not exist')
    else:
        return x % m

def egcd(a, b):
    if a == 0:
        return (b, 0, 1)
    else:
        g, y, x = egcd(b % a, a)
        return (g, x - (b // a) * y, y)