from util import char_to_relpos, letters_to_str
from ngram import Ngram
import random

class MonoalphabeticKey:
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    keylen = len(alphabet)
    rand = random.Random()

    def __init__(self, key=None, **kwargs):
        self.config = kwargs
        cfg = self.config # shorthand

        if key:
            self.key = key
        else:
            self.key = list(self.alphabet)
            self.rand.shuffle(self.key)

    def __str__(self):
        return "".join(self.key)

    def _decrypt_to_list(self, plaintext):
        return [
            self.key[char_to_relpos(char)]
                if char_to_relpos(char) != None
                else char
            for char in plaintext
        ]

    def decrypt(self, plaintext):
        return "".join(self._decrypt_to_list(plaintext))

    def swap(self, i, j):
        new_key = list(self.key)
        temp = new_key[i]
        new_key[i] = self.key[j]
        new_key[j] = temp
        return MonoalphabeticKey(new_key, **self.config)

    def crossover(self, other):
        # cycle crossover
        parent1 = self.key
        parent2 = other.key

        child1 = [None for _ in parent1]
        child2 = [None for _ in parent2]

        for i, v in enumerate(child1):
            if v != None:
                continue

            start_idx = i
            next_idx = None
            while next_idx == None or next_idx != start_idx:
                idx = next_idx if next_idx != None else start_idx
                elem = parent1[idx]
                mirror = parent2[idx]
                child1[idx] = elem
                child2[idx] = mirror

                next_idx = parent1.index(mirror)

            parent1, parent2 = parent2, parent1
        return (MonoalphabeticKey(child1, **self.config),
                MonoalphabeticKey(child2, **other.config))

    def mutation(self):
        mask = [self.rand.binomialvariate() for _ in self.key]
        mut = list(self.key)
        for i, v in enumerate(mask):
            if v:
                swp = char_to_relpos(mut[i])
                mut[i], mut[swp] = mut[swp], mut[i]
        return MonoalphabeticKey(mut, **self.config)

    def best_version(self, scorer):
        return self

class CyclicKey(MonoalphabeticKey):
    def __init__(self, key=None, **kwargs):
        super().__init__(key=key, **kwargs)

    def _decrypt_to_list(self, plaintext):
        out, pos = [], 0
        for char in plaintext:
            if char.isalpha():
                d = self.key[(char_to_relpos(char) + pos) % self.keylen]
                out.append(d)
                pos -= 1
            else:
                out.append(char)
        return out

    def cycle_crossover(self, other):
        p1 = MonoalphabeticKey(self.key, **self.config)
        p2 = MonoalphabeticKey(other.key, **other.config)
        c1, c2 = p1.crossover(p2)
        return (CyclicKey(c1.key, **c1.config),
                CyclicKey(c2.key, **c2.config))

    def crossover(self, other):
        return self.cycle_crossover(other)

    def mutation(self):
        x = MonoalphabeticKey(self.key, **self.config).mutation()
        return CyclicKey(x.key, **x.config)

class PolyalphabeticKey:
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    def __init__(self, keylen, key=None, **kwargs):
        self.config = kwargs
        cfg = self.config # shorthand

        self.rand = random.Random(cfg.get("seed"))
        self.keylen = keylen
        if key:
            self.key = key
        else:
            self.key = []
            for i in range(self.keylen):
                self.key.append(MonoalphabeticKey(**{
                    **self.config,
                    "seed": (self.config.get("seed") or 0) + self.keylen + i + 1
                }))

    def __str__(self):
        return "\n".join(str(x) for x in self.key)

    def _decrypt_to_list(self, cyphertext):
        return [
            k.decrypt(char) if char.isalpha() else char
            for char, k in zip(cyphertext, self.key)
        ]

    def decrypt(self, cyphertext):
        return "".join(self._decrypt_to_list(cyphertext))

    def crossover(self, other):
        child1, child2 = [], []
        for s, o in zip(self.key, other.key):
            c1, c2 = s.cycle_crossover(o)
            child1.append(c1)
            child2.append(c2)
        return (PolyalphabeticKey(self.keylen, child1, **self.config),
                PolyalphabeticKey(other.keylen, child2, **other.config))

    def mutation(self):
        new_key = []
        for k in self.key:
            new_key.append(k.mutation())
        return PolyalphabeticKey(self.keylen, new_key, **self.config)
