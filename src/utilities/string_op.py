def split_into_decimal(text, split_size):
    ascii_text =''
    for c in text:
        ascii_text += str(ord(c))
    
    for idx in range(0, len(ascii_text), split_size):
        text_slice = ascii_text[idx:idx+split_size]
        yield int(text_slice)
        