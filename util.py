def char_to_relpos(letter):
    ascii_num = ord(letter)
    if ascii_num >= 65 and ascii_num < 91:
        return ascii_num - 65
    else:
        return None

def relpos_to_char(pos):
    if pos >= 65 and pos < 91:
        return chr(pos + 65)
    else:
        return None

def parse(file):
    with open(file) as f:
        raw = f.read()
        cypher = list(map(
            lambda x: chr(int(x, 2)),
            filter(lambda x: x != '', raw.split(" "))))
        cypher_char_only = list(filter(lambda x: x.isalpha(), cypher))
    return cypher , cypher_char_only

def letters_to_str(ls):
    return "".join(ls)
