
from math import gcd

def is_prime(n):
    """ Checks if input is a prime number """
    if n <= 3:
        return n > 1
    elif n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    while (i*i <= n):
        if n % i == 0 or n % (i+2) == 0:
            return False
        i += 6
    return True

def is_coprime(a, b):
    """ Checks if a and b is a coprime (relatively primes)"""
    return gcd(a, b) == 1

def get_prime_factors(num):
    """Returns a list containing prime factor of a number 
    Reference: https://www.sanfoundry.com/python-program-compute-prime-factors-integer/
    """
    factors = []
    for i in range(1, num+1):
        k = 0
        if (num % i == 0):
            j = 1
            while (j <= i):
                if (i % j == 0):
                    k += 1
                j += 1
            if (k == 2):
                factors.append(i)
        i += 1

def get_list_of_coprime(num, descending=True):
    coprimes = []
    if descending:
        i = num - 1
        while (len(coprimes) < 100 and i >= 2):
            if (is_coprime(i, num)):
                coprimes.append(i)
            i -= 1
    else:
        i = 2
        while (len(coprimes) < 100 and i < num):
            if (is_coprime(i, num)):
                coprimes.append(i)
            i += 1
    return coprimes
