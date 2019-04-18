import numpy as np
import random

BLOCK_SIZE_IN_BYTE = 16 # bytes
BLOCK_SIZE_IN_HEX = BLOCK_SIZE_IN_BYTE*2 # hex
class Chill:
  def __init__(self, plain_text_src = 'text', plain_text = '', plain_text_path = '', key = 'key', mode = 'ECB', cipher_text_path = '', cipher_text=''):
    # constructor
    if mode.upper() in ['ECB', 'CBC', 'CFB', 'OFB', 'CTR']: self.mode = mode.upper()
    else:
      print('Error: incorrect mode of operation')
      exit(0)

    # key related
    self.original_key_length = len(key) # original key length
    self.key = self.__to_hex(key)
    self.__key_padding()
    self.round_time = 5 + (self.original_key_length % 6)
    self.arr_round_key = self.__generate_round_key()
    self.IV = self.__to_hex(open("/dev/urandom","rb").read(BLOCK_SIZE_IN_HEX))

    # plain text related
    self.plain_text = plain_text
    self.plain_text_path = plain_text_path
    self.plain_text_src = plain_text_src # ['text', 'file']
    # get plain text from file
    if self.plain_text_src == 'file':
      self.plain_text = self.__load_text('plain')

    if self.plain_text == '':
      print('Error: 0 bytes plain text')
      exit(0)

    # cipher text related
    self.cipher_text = cipher_text
    self.cipher_text_path = cipher_text_path
    # get cipher text from file
    try:
      if self.cipher_text_path != '':
        self.cipher_text = self.__load_text('cipher')
        if self.plain_text == '':
          print('Error: 0 bytes plain text')
          exit(0)
    except:
      pass

  def __to_hex(self, content):
    # convert content (string) to hex
    result = ''
    for c in content:
      try:
        result += format(ord(c), '08b')
      except TypeError as e:
        result += format(c, '08b')
    t = '%08X' % int(result, 2)
    if len(t) % 2 == 1: t = '0' + t
    return t

  def __from_hex(self, content):
    # convert content (hex) to string
    result = ''
    for idx in range (0, len(content), 2):
      c = content[idx]+content[idx+1]
      result += chr(int(c, 16))
    return result

  def __key_padding(self):
    # padding the key
    key_length = len(self.key)
    if key_length == BLOCK_SIZE_IN_HEX:
      pass
    elif key_length < BLOCK_SIZE_IN_HEX:
      seed = 0
      for idx, k in enumerate(self.key):
        if (idx % 2 == 1): seed += ord(k)
      random.seed(seed)
      while len(self.key) < BLOCK_SIZE_IN_HEX:
        pos = random.randrange(0, key_length)
        self.key += self.key[pos]
    else:
      seed = 0
      for idx, k in enumerate(self.key):
        if (idx % 2 == 0): seed += ord(k)
      random.seed(seed)
      while len(self.key) > BLOCK_SIZE_IN_HEX:
        pos = random.randrange(0, key_length)
        self.key = self.key[:pos] + self.key[(pos+1):]

  def __load_text(self, mode):
    # load file content
    # open file
    if mode == 'plain': path = self.plain_text_path
    else: path = self.cipher_text_path
    with open(path, mode='rb') as file:
      file_content = file.read()
    return file_content

  def __xor(self, hex_string1, hex_string2):
    # return xor from two strings
    t = format(int(hex(int(hex_string1, 16) ^ int(hex_string2, 16)), 0), '02X')
    while len(t) % 2 == 1 or len(t) == 30: t = '0' + t
    return t

  def __xor_matrix(self, hex_matrix1, hex_matrix2):
    # return xor from two matrix
    # matrix size are equal, return matrix
    result = []
    for idx_row, rows in enumerate(hex_matrix1):
      row_result = []
      for idx_col, cols in enumerate(rows):
        row_result.append(self.__xor(hex_matrix1[idx_row][idx_col], hex_matrix2[idx_row][idx_col]))
      result.append(row_result)
    return np.asarray(result)

  def __transform_to_matrix(self, data):
    # transform data (string) to matrix
    result = np.zeros((4, 4), 'U2')
    result[0, 0] = data[0] + data[1]
    result[0, 1] = data[4] + data[5]
    result[0, 2] = data[6] + data[7]
    result[0, 3] = data[18] + data[19]
    result[1, 0] = data[2] + data[3]
    result[1, 1] = data[8] + data[9]
    result[1, 2] = data[16] + data[17]
    result[1, 3] = data[20] + data[21]
    result[2, 0] = data[10] + data[11]
    result[2, 1] = data[14] + data[15]
    result[2, 2] = data[22] + data[23]
    result[2, 3] = data[28] + data[29]
    result[3, 0] = data[12] + data[13]
    result[3, 1] = data[24] + data[25]
    result[3, 2] = data[26] + data[27]
    result[3, 3] = data[30] + data[31]
    return result

  def __transform_to_string(self, data):
    # transform data (matrix) to string
    result = data[0, 0] + data[1, 0] + data[0, 1] + data[0, 2] + data[1, 1] + data[2, 0] + data[3, 0] + data[2, 1] + data[1, 2] + data[0, 3] + data[1, 3] + data[2, 2] + data[3, 1] + data[3, 2] + data[2, 3] + data[3, 3]
    return result

  def __subX(self, mode, input):
    # SubX method
    # input is matrix, return matrix
    result = np.copy(input)
    for idx_row, rows in enumerate(result):
      for idx_col, cols in enumerate(rows):
        int_result = abs(((int(result[idx_row][idx_col][0]+'0', 16) - 16) % 256) + (1 if mode == 'plus' else -1) * ((int(result[idx_row][idx_col][1], 16) - 1) % 16))
        result[idx_row][idx_col] = format(int(hex(int_result), 0), '02X')
    return result

  def __l_transposition(self, input):
    # L Transposition method
    # input is matrix, return matrix
    result = np.copy(input)
    result[0, 0], result[3, 1] = result[3, 1], result[0, 0]
    result[0, 1], result[3, 0] = result[3, 0], result[0, 1]
    result[0, 2], result[3, 3] = result[3, 3], result[0, 2]
    result[0, 3], result[3, 2] = result[3, 2], result[0, 3]
    result[1, 0], result[2, 3] = result[2, 3], result[1, 0]
    result[2, 0], result[1, 3] = result[1, 3], result[2, 0]
    result[1, 1], result[2, 2] = result[2, 2], result[1, 1]
    return result

  def __shift_col(self, input):
    # ShiftCol method
    # input is matrix, return matrix
    sum_col = [0, 0, 0, 0]
    for idx_row, rows in enumerate(input):
      for idx_col, cols in enumerate(rows):
        sum_col[idx_col] += int(input[idx_row][idx_col], 16)
    result_temp = np.copy(input.T)
    # shift
    result = []
    for idx_row, rows in enumerate(result_temp):
      result.append(np.roll(rows, (sum_col[idx_row] % 4) * (-1 if idx_row % 2 == 1 else 1)))
    return np.asarray(result).T

  def __rot_mod(self, key):
    # RotMod method
    # key is matrix, return matrix
    return np.rot90(key, -1 * (self.original_key_length % 4))

  def __xor_col(self, input):
    # XorCol method
    # input is matrix, return matrix
    result = np.copy(input)
    for idx_row, rows in enumerate(input):
      idx_col2 = 1
      for idx_col1, cols in enumerate(rows):
        result[idx_row][idx_col1] = self.__xor(input[idx_row][idx_col1], input[idx_row][idx_col2])
        if idx_col2 == len(rows)-1: idx_col2 = 0
        else: idx_col2 += 1
    return result

  def __round_function(self, right_block, round_key):
    # Feistel round function
    # right_block and round_key are matrix, return matrix
    # SubX+
    result = self.__subX('plus', right_block)
    # L Transposition
    result = self.__l_transposition(result)
    # ShiftCol
    result = self.__shift_col(result)
    # XOR with key
    result = self.__xor_matrix(result, round_key)
    return result

  def __generate_round_key(self):
    # Generate n matrix of round key, n = round time
    # round_key is matrix, return array of matrix
    round_key = self.__transform_to_matrix(self.key)
    result = []
    result.append(round_key)
    for i in range(1, self.round_time):
      # RotMod
      round_key_temp = self.__rot_mod(result[i-1])
      # SubX-
      round_key_temp = self.__subX('minus', round_key_temp)
      # XorCol
      round_key_temp = self.__xor_col(round_key_temp)
      result.append(round_key_temp)
    return np.asarray(result)

  def __feistel(self, mode, left_block_matrix, right_block_matrix):
    # Feistel Structure implementation
    round_idx = 0
    while round_idx < self.round_time:
      if mode == 'encrypt': round_key_matrix = self.arr_round_key[round_idx]
      else: round_key_matrix = self.arr_round_key[self.round_time - 1 - round_idx] # mode == 'decrypt'
      right_block_matrix_new = self.__xor_matrix(left_block_matrix, self.__round_function(right_block_matrix, round_key_matrix))
      left_block_matrix_new = np.copy(right_block_matrix)
      right_block_matrix = np.copy(right_block_matrix_new)
      left_block_matrix = np.copy(left_block_matrix_new)
      round_idx += 1
    
    return left_block_matrix, right_block_matrix

  def __plain_pad(self, s):
    _len = BLOCK_SIZE_IN_HEX
    if hasattr(s, 'encode'):
      # s is a string
      s = s.encode()
    return s + ((_len - len(s) % _len) * chr(_len - len(s) % _len)).encode()

  def __plain_unpad(self, s):
    return s[:-ord(s[len(s)-1:])]

  def __counter_iv(self):
    self.IV = hex(int(self.IV, 16) + 1)[2:-1].upper()

  def encrypt(self):
    # ENCRYPTION
    # preprocess
    self.plain_text = self.__plain_pad(self.plain_text)
    self.plain_text = self.__to_hex(self.plain_text)
    self.cipher_text = ''
    # feistel
    # init feistel loop
    done = False
    idx_left_block = BLOCK_SIZE_IN_HEX
    idx_right_block = 0
    processed_block = 2

    if self.mode in ['CBC', 'CFB', 'OFB', 'CTR']:
      self.cipher_text += self.IV

    while not done:
      # init round
      if self.mode in ['ECB', 'CBC']:
        right_block = self.plain_text[idx_right_block:idx_right_block+BLOCK_SIZE_IN_HEX]
        left_block = self.plain_text[idx_left_block:idx_left_block+BLOCK_SIZE_IN_HEX]
      elif self.mode in ['CFB', 'OFB', 'CTR']:
        right_block = self.IV[:BLOCK_SIZE_IN_HEX]
        left_block = self.IV[BLOCK_SIZE_IN_HEX:]

      if self.mode == 'CBC':
        right_block_IV = self.IV[:BLOCK_SIZE_IN_HEX]
        left_block_IV = self.IV[BLOCK_SIZE_IN_HEX:]

        right_block = self.__xor(right_block, right_block_IV)
        left_block = self.__xor(left_block, left_block_IV)

      right_block_matrix = self.__transform_to_matrix(right_block)
      left_block_matrix = self.__transform_to_matrix(left_block)
      left_block_matrix, right_block_matrix = self.__feistel('encrypt', left_block_matrix, right_block_matrix)
      right_block = self.__transform_to_string(right_block_matrix)
      left_block = self.__transform_to_string(left_block_matrix)

      if self.mode == 'OFB':
        self.IV = right_block + left_block

      if self.mode in ['CFB', 'OFB', 'CTR']:
        right_block_IV = self.plain_text[idx_right_block:idx_right_block+BLOCK_SIZE_IN_HEX]
        left_block_IV = self.plain_text[idx_left_block:idx_left_block+BLOCK_SIZE_IN_HEX]
        right_block = self.__xor(right_block, right_block_IV)
        left_block = self.__xor(left_block, left_block_IV)
      
      result = right_block + left_block
      if self.mode in ['CBC', 'CFB']:
        self.IV = result
      elif self.mode == 'CTR':
        self.__counter_iv()

      self.cipher_text += result

      if processed_block == (len(self.plain_text) / BLOCK_SIZE_IN_HEX): done = True
      if not done:
        idx_left_block += 2*BLOCK_SIZE_IN_HEX
        idx_right_block += 2*BLOCK_SIZE_IN_HEX
        processed_block += 2

    # convert cipher text from hex to string
    self.cipher_text = self.__from_hex(self.cipher_text)
    # result stored in self.cipher_text
    # dump cipher to file txt
    if self.cipher_text_path != '':
      f = open(self.cipher_text_path, 'wb')
      f.write(self.cipher_text.encode())
      f.close()

  def decrypt(self):
    # DECRYPTION
    # preprocess
    self.cipher_text = self.__to_hex(self.cipher_text)
    self.plain_text = ''
    # feistel
    # init feistel loop
    done = False
    idx_left_block = BLOCK_SIZE_IN_HEX
    idx_right_block = 0
    processed_block = 2

    if self.mode in ['OFB', 'CTR']:
      self.IV = self.cipher_text[:BLOCK_SIZE_IN_HEX*2]
      self.cipher_text = self.cipher_text[BLOCK_SIZE_IN_HEX*2:]

    # print self.cipher_text
    while not done:
      if self.mode in ['CBC', 'CFB']:
        self.IV = self.cipher_text[-1*(idx_left_block*2+BLOCK_SIZE_IN_HEX*2)+idx_right_block : -1*(idx_left_block*2)+idx_right_block]
        if self.IV == '': break

      # init round
      if self.mode in ['ECB', 'CBC']:
        if idx_right_block == 0:
          right_block = self.cipher_text[-1*(idx_right_block+BLOCK_SIZE_IN_HEX):]
        else:
          right_block = self.cipher_text[-1*(idx_right_block+BLOCK_SIZE_IN_HEX) : -1*idx_right_block]
        left_block = self.cipher_text[-1*(idx_left_block+BLOCK_SIZE_IN_HEX) : -1*(idx_left_block)]
      elif self.mode in ['CFB', 'OFB', 'CTR']:
        right_block = self.IV[:BLOCK_SIZE_IN_HEX]
        left_block = self.IV[BLOCK_SIZE_IN_HEX:]

      # decrypt function
      right_block_matrix = self.__transform_to_matrix(right_block)
      left_block_matrix = self.__transform_to_matrix(left_block)
      if self.mode in ['ECB', 'CBC']:
        left_block_matrix, right_block_matrix = self.__feistel('decrypt', left_block_matrix, right_block_matrix)
      elif self.mode in ['CFB', 'OFB', 'CTR']:
        left_block_matrix, right_block_matrix = self.__feistel('encrypt', left_block_matrix, right_block_matrix)
      left_block = self.__transform_to_string(left_block_matrix)
      right_block = self.__transform_to_string(right_block_matrix)

      if self.mode == 'OFB':
        self.IV = right_block + left_block
      elif self.mode == 'CTR':
        self.__counter_iv()
      elif self.mode == 'CBC':
        right_block_IV = self.IV[BLOCK_SIZE_IN_HEX:]
        left_block_IV = self.IV[:BLOCK_SIZE_IN_HEX]

        right_block = self.__xor(right_block, right_block_IV)
        left_block = self.__xor(left_block, left_block_IV)

      if self.mode in ['OFB', 'CTR']:
        right_block_IV = self.cipher_text[idx_right_block:(idx_right_block+BLOCK_SIZE_IN_HEX)]
        left_block_IV = self.cipher_text[idx_left_block:(idx_left_block+BLOCK_SIZE_IN_HEX)]

        right_block = self.__xor(right_block, right_block_IV)
        left_block = self.__xor(left_block, left_block_IV)
        right_block, left_block = left_block, right_block
      elif self.mode in ['CFB']:
        if idx_right_block == 0:
          right_block_IV = self.cipher_text[-1*(idx_right_block+BLOCK_SIZE_IN_HEX):]
        else:
          right_block_IV = self.cipher_text[-1*(idx_right_block+BLOCK_SIZE_IN_HEX) : -1*idx_right_block]
        left_block_IV = self.cipher_text[-1*(idx_left_block+BLOCK_SIZE_IN_HEX) : -1*(idx_left_block)]

        right_block_IV, left_block_IV = left_block_IV, right_block_IV
        right_block = self.__xor(right_block, right_block_IV)
        left_block = self.__xor(left_block, left_block_IV)
        right_block, left_block = left_block, right_block

      if self.mode in ['OFB', 'CTR']:
        self.plain_text = self.plain_text + left_block + right_block
      else:
        self.plain_text = left_block + right_block + self.plain_text

      if processed_block == (len(self.cipher_text) / BLOCK_SIZE_IN_HEX): done = True
      if not done:
        idx_left_block += 2*BLOCK_SIZE_IN_HEX
        idx_right_block += 2*BLOCK_SIZE_IN_HEX
        processed_block += 2

    # convert plain text from hex to string
    self.plain_text = self.__from_hex(self.plain_text)
    # remove padding from plain text
    self.plain_text = self.__plain_unpad(self.plain_text)
    self.plain_text = self.plain_text.strip('\00')
    # result stored in self.plain_text
