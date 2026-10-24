from random import Random
from statistics import mean, stdev
from util import letters_to_str
import math
import csv

class GeneticAlgorithm:

    rand = Random()

    def __init__(self, ind_builder, scorer, cyphertext, **kwargs):
        self.population = []
        self.fitness = []
        self.best_individual = None
        self.best_fitness = -100000 # arbitrary
        self.fitness_increase = [-100000 for _ in range(15)] # last 15 increases

        self.config = kwargs
        cfg = self.config # shorthand
        self.pop_size = cfg["pop_size"]
        self.ind_config = cfg["ind_config"]
        self.ind_builder = ind_builder
        self.cyphertext = cyphertext
        self.scorer = scorer

    def _log(self, generation):
        """Prints the formatted log for the current generation."""
        line = "=" * 50
        unique = len({tuple(ind.key) for ind in self.population})
        print(line)
        print(f" Current generation : {generation}")
        print(f" Best individual    : {self.best_individual}")
        print(f" Best fitness       : {self.best_fitness:.6f}")
        print(f" Fitness change     : {self.fitness_increase[-1]:+.6f}")
        print(f" Unique individuals : {unique}/{self.pop_size}")
        print(line)

    def _print_population(self):
        for x in self.population:
            print(letters_to_str(x.key))

    def _calc_fitness_increase(self, new_fitness):
        delta = new_fitness - self.best_fitness
        return [*self.fitness_increase[1:], delta]

    def _update_best_individual(self):
        print("Updating best individual")
        indexed_fitness = list(enumerate(self.fitness))
        sorted_fitness = sorted(indexed_fitness, key=lambda t: t[1])
        best_fit_idx, best_fitness = sorted_fitness[-1]
        best_ind_idx = best_fit_idx

        self.best_individual = self.population[best_ind_idx]
        self.fitness_increase = self._calc_fitness_increase(best_fitness)
        self.best_fitness = best_fitness

    def _evaluate_population(self):
        print("Evaluating population")
        self.fitness = list(map(
            lambda x: self.scorer.score(x.decrypt(self.cyphertext)),
            self.population
        ))
        self._count_unique()
        self._update_best_individual()

    def _count_unique(self):
        self.unique = len({tuple(ind.key) for ind in self.population})
        self.unique_rate = self.unique / self.pop_size

    def _start_population(self):
        print("Initializing population")
        for i in range(self.pop_size):
            # print(f"Individual {i + 1}/{self.pop_size}")
            ind = self.ind_builder(**self.ind_config)
            self.population.append(ind)
        # self._print_population()
        self._evaluate_population()

    def _tournament(self):
        indexed_fitness = list(enumerate(self.fitness))
        contestants = self.rand.sample(indexed_fitness, k=self.config["tournament_size"])
        best_ind_idx, _ = sorted(contestants, key=lambda t: t[1])[-1]
        return self.population[best_ind_idx]

    def _stop_condition(self, current_gen):
        did_exceed_generations = current_gen > self.config["max_gen"]
        history_mean = abs(mean(self.fitness_increase))
        history_stdev = abs(stdev(self.fitness_increase))
        is_hist_mean_small = history_mean < self.config["fit_threshold"]
        is_hist_stdev_small = history_stdev < self.config["fit_threshold"]
        had_little_fit_increase = is_hist_mean_small and is_hist_stdev_small
        return did_exceed_generations or had_little_fit_increase

    def _write_csv(self, generation):
        """Grava uma linha por geração no CSV de histórico."""
        path = self.config.get("csv_path", "history.csv")
        run = self.config.get("run", 0)
        extra = self.config.get("csv_extra", {})        # colunas extras fixas (ex.: pop_size)
        reset = self.config.get("csv_reset", run == 0)  # recria o arquivo na geração 0?
        is_first = generation == 0 and reset
        with open(path, "w" if is_first else "a", newline="") as f:
            writer = csv.writer(f)
            if is_first:
                writer.writerow(["run", *extra.keys(), "generation",
                                "best_fitness", "worst_fitness", "mean_fitness"])
            writer.writerow([run, *extra.values(), generation,
                            max(self.fitness), min(self.fitness), mean(self.fitness)])

    def evolve(self):
        print("Starting evolution...")
        self._start_population()
        gen = 0
        self._log(gen)
        if self.config.get("csv"):
            self._write_csv(gen)
        while not self._stop_condition(gen):
            new_pop = []
            while len(new_pop) < self.pop_size:
                parent1 = self._tournament()
                parent2 = self._tournament()

                child1, child2 = None, None
                if self.rand.binomialvariate(n=1, p=self.config["crossover_rate"]):
                    child1, child2 = parent1.crossover(parent2)
                else:
                    child1, child2 = parent1, parent2

                if self.rand.binomialvariate(n=1, p=self.config["mutation_rate"]):
                    child1 = child1.mutation()
                if self.rand.binomialvariate(n=1, p=self.config["mutation_rate"]):
                    child2 = child2.mutation()

                new_pop.append(child1)
                new_pop.append(child2)

                # adjust possible exceeding individuals
                if len(new_pop) > self.pop_size:
                    while len(new_pop) != self.pop_size:
                        new_pop.pop()


            self.population = new_pop
            self._evaluate_population()
            gen += 1
            # self._print_population()
            self._log(gen)
            if self.config.get("csv"):
                self._write_csv(gen)
