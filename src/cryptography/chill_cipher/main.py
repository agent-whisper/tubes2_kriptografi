from chill import Chill
from collections import Counter
"""
fungsi _to_hex() ditambah try-catch
fungsi _plain_pad() ditambah encode
fungsi encrypt() di akhir f.write(str.encode())
di main -> str(p[i])
"""

# ORIGINAL TEST
ch = Chill(plain_text_src='file',
		   plain_text_path='plain.txt',
		   key='itbganeshasepuluasdf',
		   mode='ECB',
		   # mode='CBC',
		   # mode='CFB',
		   # mode='OFB',
		#    mode='CTR',
		   cipher_text_path= 'cipher.txt')

p = Counter(ch.plain_text)
# print(p)
# for i in range(256):
# 	if p[i] != 0:
# 		print(str(i) + '\t' + str(p[i]))
ch.encrypt()
c = Counter(ch.cipher_text)
print(c)
# for i in range(256):
# 	if c[chr(i)] != 0:
# 		print(str(i) + '\t' + str(c[chr(i)]))
ch.decrypt()

# NEW TEST
ch2 = Chill(
	plain_text='this is an email',
	key='this is the key',
)
ch2.encrypt()
print('plain text before:', ch2.plain_text)
print('cipher text:', ch2.cipher_text)
ch2.decrypt()
print('plain text after:', ch2.plain_text)

def generate_cipher_text(plain_text, key, mode='CTR'):
	ch = Chil(plain_text=plain_text,
			key=key,
			mode=mode)
	
	
	