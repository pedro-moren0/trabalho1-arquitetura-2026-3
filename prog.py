import random
from ga import GeneticAlgorithm
from util import parse, letters_to_str
from ngram import Ngram
from keys import CyclicKey, MonoalphabeticKey, PolyalphabeticKey
from sys import argv, exit

config = {
    "seed": 42,
    "pop_size": 3000,
    "max_gen": 300,
    "tournament_size": 5,
    "fit_threshold": 0.001,
    "mutation_rate": 0.1,
    "crossover_rate": 0.7,
    "survivor_rate": 0.1,
    "extinction_rate": 0.1,
    "ind_config": {
        "ngram_size": 4,
        "ngram_file": "english_quadgrams.txt"
    }
}

files = {
    "circ": "encoded-circular.txt",
    "simple": "encoded-simple.txt"
}

def main():
    if len(argv) != 2:
        print("Mismatched argument numbers!!")
        exit(1)

    mode = argv[1]
    scorer = Ngram(4)
    scorer.from_file("english_quadgrams.txt")

    cyphertext, ct_chars = parse(files[mode])
    constructor = MonoalphabeticKey if mode == "simple" else CyclicKey
    ga = GeneticAlgorithm(constructor, scorer, ct_chars, **config)
    ga.evolve()

    print("cypher")
    print(letters_to_str(cyphertext))
    print("key:", ga.best_individual, sep="\n")
    print("plain")
    print(ga.best_individual.decrypt(cyphertext))
    print("best fitness:", ga.best_fitness)
if __name__ == "__main__":
    main()
