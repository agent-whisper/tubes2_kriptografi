import re
import time

def generate_base_point(a,b,p) :
    found = False
    base = (0,0)
    for x in range (0,p) :
        for y in range (0,p) :
            if (((x**3 + a*x + b)%p) == (y**2 % p)) :
                base = (x,y)
                # print(x,y)
                found = True
                break
        if (found) :
            break
    return(base)

def generate_list_point(a,b,p) :
    list_point = []
    for x in range (0,p) :
        for y in range (0,p) :
            if (((x**3 + a*x + b)%p) == (y**2 % p)) :
                point = (x,y)
                list_point.append(point)
    return(list_point)


def sum_point(p1, p2, p, a) :
    x_sum = 0
    y_sum = 0
    teta = 0
    if (p1[0] == p2[0] and p1[1] == p2[1]) :
        teta = ((3*(p1[0]**2) + a) * pow(2 * p1[1],p-2,p)) % p
        # print((3*(p1[0]**2) + a),pow(2 * p1[1],p-2,p))
        x_sum = ((teta ** 2) - 2*p1[0]) % p
        y_sum = (teta * (p1[0] - x_sum) - p1[1]) % p
        # print(teta, x_sum, y_sum)
    else :
        teta = ((p1[1] - p2[1]) * pow(p1[0]-p2[0],p-2,p)) % p
        x_sum = ((teta ** 2) - p1[0] - p2[0]) % p
        y_sum = (teta * (p1[0] - x_sum) - p1[1]) % p

    return(x_sum, y_sum)

def multiply_point(k, point, p, a) :
    current_point = point
    for i in range(1,k) :
        current_point = sum_point(point, current_point, p, a)
        # print(current_point)
    return(current_point)

def subs_point(point1, point2, p, a) :
    point2 = (point2[0], (point2[1] * -1) % p)
    return (sum_point(point1, point2, p, a))

def generate_public_key_for_testing(base, priv_key, p, a) :
    return(multiply_point(priv_key, base, p, a))

def int_to_point(int_char, a, b, p, k) :
    point = (-1,-1)
    for x in range (int_char * k + 1, int_char * k + 1 + k) :
        for y in range (0, p) :
            if (((x**3 + a*x + b)%p) == (y**2 % p)) :
                point = (x,y)
                break
        if (point[0] != -1) :
            break
    return(point)

import math
def point_to_int(point, k) :
    return(math.floor((point[0]-1)/k))


def gen_pub_key(filename, priv_key, a, b, p) :
    base = generate_base_point(a,b,p)

    if (priv_key < 1 or priv_key >= p) :
        print('private key harus lebih dari 0 dan kurang dari P')
        return(0)
    pub_key = multiply_point(priv_key, base, p, a)
    pub_key = str(pub_key[0])+','+str(pub_key[1])
    file = open(filename + '.priv', "w")
    file.write(str(priv_key))
    file.close()
    file = open(filename + '.pub', "w")
    file.write(pub_key)
    file.close()


def check_validasi_variable(a, b, p, k) :
    valid = True
    if (a >= p) :
        print('variable a harus lebih kecil dari p')
        valid = False
    if (b >= p) :
        print('variable b harus lebih kecil dari p')
        valid = False
    if (k < 0 or k >= p) :
        print('variable k harus lebih kecil dari p')
        valid = False
    if (((4*( a**3 ) + 27*( b**2 )) % p) == 0) :
        print('pilih kombinasi a dan b lain.')
        valid = False
    if (((256 * k) + k) > p) :
        print('pilih kombinasi nilai k dan p lain, nilai P harus lebih besar 258 kali')
        valid = False
    return(valid)

def read_pub_key_file(pub_key) :
    file = open(pub_key, "r")
    pub_key = file.read()
    pub_key = pub_key.split(',')
    pub_key = (int(pub_key[0]), int(pub_key[1]))
    file.close()
    return(pub_key)

def read_priv_key_file(priv_key) :
    file = open(priv_key, "r")
    priv_key = file.read()
    priv_key = int(priv_key)
    file.close()
    return(priv_key)

def enkripsi_string(a, b, p, k, pubkey_point, plaintext):
    if hasattr(plaintext, 'encode'):
        plaintext = plaintext.encode()

    valid = check_validasi_variable(a,b,p,k)
    if not valid:
        raise ValueError('One or more parameter is invalid')
    base = generate_base_point(a, b, p)
    kB = multiply_point(k, base, p, a)
    temp_ciphertext = []

    for char in (plaintext) :
        pM = int_to_point(char, a, b, p, k)
        if(pM[0] == -1) :
            print('gagal int to point')
            break
        cipher = (kB,  sum_point(pM, multiply_point(k, pubkey_point, p, a), p, a))
        temp_ciphertext.append(cipher)
    
    ciphertext = ''
    for tc in temp_ciphertext:
        ciphertext += str(tc) + '#'
    return ciphertext
    

def enkripsi(a, b, p, k, pub_key_receiver, plain_file, outdir) :
    file = open(plain_file, "rb")
    message = file.read()
    file.close()
    valid = check_validasi_variable(a,b,p,k)
    if not valid :
        return(0)
    
    if (type(pub_key_receiver) is str) :
        pub_key_receiver = read_pub_key_file(pub_key_receiver)

    time_start = time.time()
    base = generate_base_point(a,b,p)

    kB = multiply_point(k, base, p, a)
    ciper_message = []
    for char in (message) :
        pM = int_to_point(char, a, b, p, k)
        if(pM[0] == -1) :
            print('gagal int to point')
            break
        cipher = (kB,  sum_point(pM, multiply_point(k, pub_key_receiver, p, a), p, a))
        ciper_message.append(cipher)
    time_end = time.time()

    file = open(outdir, "w")
    for cipher in ciper_message :
        file.write(str(cipher)+'#')
    file.close()
    return(time_end - time_start)

def dekripsi_string(a, b, p, k, priv_key_val, ciphertext):
    valid = check_validasi_variable(a, b, p, k)
    if not valid:
        raise ValueError('One or more parameter is invalid')
    cipher_message = ciphertext.split('#')
    cipher_point = []
    for cipher in cipher_message :
        cipher = re.split('[^0-9]', cipher)
        cipher = [x for x in cipher if x != '']
        if (len(cipher) == 4) :
            cipher = ((int(cipher[0]),int(cipher[1])),(int(cipher[2]),int(cipher[3])))
            cipher_point.append(cipher)
    bKb = multiply_point(priv_key_val,cipher_point[0][0], p, a)
    plain_teks = []
    for cipher_char in cipher_point :
        plain_point = subs_point(cipher_char[1], bKb, p, a)
        plain = point_to_int(plain_point, k)
        plain_teks.append(plain)
    result = bytes(plain_teks)
    return result.decode()

def dekripsi(a, b, p, k, priv_key_receiver, cipher_file, outdir) :
    file = open(cipher_file, "r")
    cipher_message = file.read()
    file.close()

    valid = check_validasi_variable(a,b,p,k)
    if not valid :
        return(0)

    if (type(priv_key_receiver) is str) :
        priv_key_receiver = read_priv_key_file(priv_key_receiver)

    if (priv_key_receiver < 1 or priv_key_receiver >= p) :
        print('private key harus lebih dari 0 dan kurang dari P')
        return(0)

    time_start = time.time()
    cipher_message = cipher_message.split('#')
    cipher_point = []
    for cipher in cipher_message :
        cipher = re.split('[^0-9]', cipher)
        cipher = [x for x in cipher if x != '']
        if (len(cipher) == 4) :
            cipher = ((int(cipher[0]),int(cipher[1])),(int(cipher[2]),int(cipher[3])))
            cipher_point.append(cipher)
    bKb = multiply_point(priv_key_receiver,cipher_point[0][0], p, a)
    plain_teks = []
    for cipher_char in cipher_point :
        plain_point = subs_point(cipher_char[1], bKb, p, a)
        plain = point_to_int(plain_point, k)
        plain_teks.append(plain)
    time_end = time.time()
    
    file = open(outdir, "wb")
    file.write(bytes(plain_teks))
    file.close()
    return(time_end - time_start)