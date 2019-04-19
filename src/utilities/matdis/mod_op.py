def modinv(a, b):
    """ Returns x such that (x * a) (mod b) == 1 
    reference: https://stackoverflow.com/questions/4798654/modular-multiplicative-inverse-function-in-python
    """
    g, x, _ = egcd(a, b)
    if g != 1:
        raise Exception('modular inverse does not exist')
    else:
        return x % b

def egcd(a, b):
    if a == 0:
        return (b, 0, 1)
    else:
        g, y, x = egcd(b % a, a)
        return (g, x - (b // a) * y, y)