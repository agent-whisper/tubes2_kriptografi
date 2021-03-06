from chill import Chill
from collections import Counter
"""
fungsi _to_hex() ditambah try-catch
fungsi _plain_pad() ditambah encode
fungsi encrypt() di akhir f.write(str.encode())
di main -> str(p[i])
"""

# ORIGINAL TEST
# ch = Chill(plain_text_src='file',
# 		   plain_text_path='plain.txt',
# 		   key='itbganeshasepuluasdf',
# 		   mode='ECB',
# 		   # mode='CBC',
# 		   # mode='CFB',
# 		   # mode='OFB',
# 		#    mode='CTR',
# 		   cipher_text_path= 'cipher.txt')

# p = Counter(ch.plain_text)
# # print(p)
# # for i in range(256):
# # 	if p[i] != 0:
# # 		print(str(i) + '\t' + str(p[i]))
# ch.encrypt()
# c = Counter(ch.cipher_text)
# print(c)
# # for i in range(256):
# # 	if c[chr(i)] != 0:
# # 		print(str(i) + '\t' + str(c[chr(i)]))
# ch.decrypt()

"""========================================================"""

# NEW TEST
pt = """Kepada Yth.
Bapak Dekan 
Di Tempat

Dengan hormat.
Bersama  surat  ini  saya  ingin  mengabarkan  bahwa  nilai  skripsi  mahasiswa  yang  bernama Faisal  Saleh  dengan  NIM  13902021 adalah 86,5 atau dalam nilai indeks A. Sidang skripsi sudah dilakukan pada Hari Rabu Tanggal 21 Januari 20 Juli 2005.

Atas perhatian Bapak saya ucapkan terima kasih.

Bandung, 25 Juli 2005

Dosen Pembimbing Skripsi
Ir. Ahmad Agus
"""
# with open('test_email.txt', 'r') as f:
# 	for l in f.readlines():
# 		pt += l
ch2 = Chill(
	plain_text=pt,
	key='diki',
	cipher_text_path='aaaa.txt',
)
ch2.encrypt()
print('plain text before:\n', ch2.plain_text)
print('\ncipher text:\n', ch2.cipher_text)
ch2.decrypt()
print('\nplain text after:\n', ch2.plain_text)
print('\nciphertext after:\n', ch2.cipher_text)
print(len(ch2.plain_text))

def generate_cipher_text(plain_text, key, mode='CTR'):
	ch = Chill(plain_text=plain_text,
			key=key,
			mode=mode)
	
	
	