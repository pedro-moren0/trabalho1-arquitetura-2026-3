from math import log10
from random import shuffle
from abc import ABC, abstractmethod

class Key(ABC):
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    
    @abstractmethod
    def decrypt(self, text):
        """Decrypts an encrypted text"""
class SubstitutionKey(Key):
    def __init__(self):
        pass
    def decrypt(self, text):
        pass
class Letter:
    def __init__(self, **kwargs):
        if "bin" in kwargs or "abs" in kwargs:
            bin = kwargs.get("bin")
            abs = kwargs.get("abs")

            if bin:
                self.ascii = int(kwargs["bin"], 2)
            elif abs:
                self.ascii = abs if type(abs is int) else int(abs)

            self.char = chr(self.ascii)

            if self.ascii >= 65 and self.ascii < 91:
                self.relpos = self.ascii - 65
                self.isChar = True
            else:
                self.relpos = None
                self.isChar = False
        else:
            raise Exception("Invalid inicialization")

class Ngram:
    def __init__(self, gram_size):
        self.ngrams, self.scores = {}, {}
        self.size = 0
        self.gram_size = gram_size
    def _calc_scores(self):
        for k, c in self.ngrams.items():
            self.scores[k] = log10(float(c) / self.size)
    def _calc_floor(self):
        self.floor = log10(float(0.01) / self.size)
    def from_file(self, path):
        with open(path) as f:
            for line in f.readlines():
                key, count = line.split(" ")
                self.ngrams[key] = int(count)
                self.size += self.ngrams[key]
        self._calc_scores()
        self._calc_floor()
    def from_text(self, text):
        for i, _ in enumerate(text):
            if i + self.gram_size > len(text):
                break
            key = str(text[i:i+self.gram_size])
            self.ngrams.setdefault(key, 0)
            self.ngrams[key] += 1
            self.size += 1
        self._calc_scores()
        self._calc_floor()
    def score(self, text):
        score = 0
        for i, _ in enumerate(text):
            if i + self.gram_size > len(text):
                break
            key = str(text[i:i+self.gram_size])
            if key in self.scores:
                score += self.scores[key]
            else:
                score += self.floor
        return score


def letter_relpos(letter):
    ascii_num = ord(letter)
    if ascii_num >= 65 and ascii_num < 91:
        return ascii_num - 65
    else:
        return None

def parse(file):
    with open(file) as f:
        raw = f.read()
        cypher = list(map(lambda x: Letter(bin=x), filter(lambda x: x != '', raw.split(" "))))
        cypher_char_only = list(filter(lambda x: x.isChar, cypher))
    return cypher , cypher_char_only

def letters_to_str(ls):
    return "".join(letter.char for letter in ls)

def decrypt(letters, key):
    return [Letter(abs=key[l.relpos].ascii) if l.relpos else l for l in letters]


circ = "encoded-simple.txt"
cyphertext, ct_chars = parse(circ)
quadgram_file = Ngram(4)
quadgram_file.from_file("english_quadgrams.txt")

alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
key = list(map(lambda x: Letter(abs=ord(x)), alphabet))
shuffle(key)
score = quadgram_file.score(letters_to_str(decrypt(ct_chars, key)))
for i in range(0, 26):
    for j in range(0, 26):
        if i == j: continue
        new_key = list(key)
        temp = new_key[i]
        new_key[i] = new_key[j]
        new_key[j] = temp
        new_score = quadgram_file.score(letters_to_str(decrypt(ct_chars, new_key)))
        if new_score > score:
            score = new_score
            key = new_key

print("cypher")
print(letters_to_str(cyphertext))
print("key:", letters_to_str(key))
print("plain")
print(letters_to_str(decrypt(cyphertext, key)))

