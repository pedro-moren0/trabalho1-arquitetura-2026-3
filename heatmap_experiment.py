from sys import argv, exit

from ga import GeneticAlgorithm
from keys import CyclicKey, MonoalphabeticKey
from ngram import Ngram
from prog import config, files   # prog.py só roda main() se for executado direto
from util import parse

N_RUNS = 10
POPS = [10, 50, 100, 500]
RATES = [0.1, 0.4, 0.7, 1.0]
BASE_MUT = config["mutation_rate"]   # valor fixo no mapa população x crossover
BASE_CX = config["crossover_rate"]   # valor fixo no mapa população x mutação


def build_grid():
    """Combinações (população, mutação, crossover) dos dois mapas de calor."""
    grid = []
    for pop in POPS:
        for mut in RATES:
            grid.append((pop, mut, BASE_CX))    # mapa população x mutação
    for pop in POPS:
        for cx in RATES:
            grid.append((pop, BASE_MUT, cx))    # mapa população x crossover
    return list(dict.fromkeys(grid))            # remove repetidas, mantendo a ordem


def run_experiment(mode, n_runs=N_RUNS):
    scorer = Ngram(4)
    scorer.from_file("english_quadgrams.txt")
    _, ct_chars = parse(files[mode])
    constructor = MonoalphabeticKey if mode == "simple" else CyclicKey

    grid = build_grid()
    for i, (pop, mut, cx) in enumerate(grid):
        for run in range(n_runs):
            # cópia do config: o dicionário global do prog.py não é alterado
            cfg = {
                **config,
                "pop_size": pop,
                "mutation_rate": mut,
                "crossover_rate": cx,
                "run": run,
                "csv": True,
                "csv_path": f"{mode}_heatmap.csv",
                "csv_extra": {"pop_size": pop, "mutation_rate": mut, "crossover_rate": cx},
                "csv_reset": i == 0 and run == 0,   # só a primeira execução recria o arquivo
            }
            print(
                f"\n##### {mode}: combinação {i + 1}/{len(grid)} "
                f"(pop={pop} mut={mut} cx={cx}), execução {run + 1}/{n_runs} #####"
            )

            ga = GeneticAlgorithm(constructor, scorer, ct_chars, **cfg)  # GA novo a cada execução
            ga.evolve()   # o evolve já chama _write_csv a cada geração

    print(f"\n##### {mode}: EXPERIMENTO CONCLUÍDO #####")


if __name__ == "__main__":
    if len(argv) != 2 or argv[1] not in files:
        print(f"uso: python heatmap_experiment.py [{'|'.join(files)}]")
        exit(1)
    run_experiment(argv[1])
