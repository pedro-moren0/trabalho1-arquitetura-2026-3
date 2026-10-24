from sys import argv, exit

from ga import GeneticAlgorithm
from keys import CyclicKey, MonoalphabeticKey
from ngram import Ngram
from prog import config, files   # prog.py só roda main() se for executado direto
from util import parse

N_RUNS = 10


def run_experiment(mode, n_runs=N_RUNS):
    scorer = Ngram(4)
    scorer.from_file("english_quadgrams.txt")
    _, ct_chars = parse(files[mode])
    constructor = MonoalphabeticKey if mode == "simple" else CyclicKey

    for run in range(n_runs):
        # cópia do config: o dicionário global do prog.py não é alterado
        cfg = {**config, "run": run, "csv_path": f"{mode}_experiment.csv"}
        print(f"\n##### {mode}: execução {run + 1}/{n_runs} #####")

        ga = GeneticAlgorithm(constructor, scorer, ct_chars, **cfg)  # GA novo a cada execução
        ga.evolve()   # o evolve já chama _write_csv a cada geração
    print(f"\n##### {mode}: EXPERIMENTO CONCLUÍDO #####")


if __name__ == "__main__":
    if len(argv) != 2 or argv[1] not in files:
        print(f"uso: python experiment.py [{'|'.join(files)}]")
        exit(1)
    run_experiment(argv[1])
