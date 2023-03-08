import numpy as np
import pandas as pd
from matplotlib import pyplot as plt


class Analysis:
    def __init__(self, iterations):
        self.iteration = 0
        self.improvement = np.empty(iterations)
        self.execution_time = np.empty(iterations)
        self.same_score_count = np.empty(iterations)
        self.factors = np.empty(iterations)

    def add_improvement(self, improvement):
        self.improvement[self.iteration] = improvement

    def add_execution_time(self, execution_time):
        self.execution_time[self.iteration] = execution_time

    def add_same_score_count(self, same_score_count):
        self.same_score_count[self.iteration] = int(same_score_count)

    def add_factors(self, w_fact):
        if len(w_fact) != len(self.factors):
            self.factors = [np.empty(len(self.factors)) for x in w_fact]
        for i, w_f in enumerate(w_fact):
            self.factors[i][self.iteration] = w_f

    def next_iteration(self):
        self.iteration += 1

    def print_information(self):
        print(f"Iteration {self.iteration}: Score {self.improvement[self.iteration]:.6f}, "
              f"iter without improvement {int(self.same_score_count[self.iteration])} "
              f"({self.execution_time[self.iteration]:.0f} ms)")

    def plot_analysis(self, figure=None, ax=None):
        columns = ["Improvement", "Execution time", "Same score count"]
        col_factors = ["Factor team amounts", "Factor player dependency", "Factor team exp"]
        df = pd.DataFrame(np.array([self.improvement, self.execution_time, self.same_score_count]+self.factors).T,
                          columns=columns+col_factors)
        if not figure:
            figure, ax = plt.subplots(len(columns)+1, sharex=True)
            plt.tight_layout(pad=2)

        for i in range(len(columns)):
            ax[i].plot(df[columns[i]])
            ax[i].set_title(columns[i])

        ax[-1].plot(df[col_factors], label=col_factors)
        ax[-1].set_title("Factors")
        ax[-1].set_xlim([0, self.iteration])
        ax[-1].legend()
        return figure, ax
