import os
  
def write_as_string(arr_of_decimals, output_dir, delimiter='', slice_len=0):
    with open(output_dir, 'w+') as fp:
        for num in arr_of_decimals:
            h = hex(num).upper()
            i = 2
            while i < len(h):
                fp.write('{}{}'.format(h[i:i+slice_len], (' ' if (slice_len>0 and i+slice_len<len(h)) else '')))
                i += slice_len
            fp.write(delimiter)

def read_hex_string(filedir, delimiter=''):
    with open(filedir, 'r') as fp:
        hex_str = fp.read()
        hex_str = hex_str.replace(' ', '')
        try:
            hex_str = hex_str.split(delimiter)[:-1]
        except ValueError:
            pass
    return hex_str