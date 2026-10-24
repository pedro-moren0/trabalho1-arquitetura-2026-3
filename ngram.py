from math import log10

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
