import numpy as np
import pandas as pd
from matplotlib import pyplot as plt


class Analysis:
    def __init__(self, iterations):
        self.iteration = 0
        self.improvement = np.empty(iterations)
        self.execution_time = np.empty(iterations)
        self.same_score_count = np.empty(iterations)

    def add_improvement(self, improvement):
        self.improvement[self.iteration] = improvement

    def add_execution_time(self, execution_time):
        self.execution_time[self.iteration] = execution_time

    def add_same_score_count(self, same_score_count):
        self.same_score_count[self.iteration] = int(same_score_count)

    def next_iteration(self):
        self.iteration += 1

    def print_information(self):
        print(f"Iteration {self.iteration}: Score {self.improvement[self.iteration]:.6f}, "
              f"iter without improvement {int(self.same_score_count[self.iteration])} "
              f"({self.execution_time[self.iteration]:.0f} ms)")

    def plot_analysis(self, figure=None, ax=None):
        columns = ["Improvement", "Execution time", "Same score count"]
        df = pd.DataFrame(np.array([self.improvement, self.execution_time, self.same_score_count]).T, columns=columns)
        if not figure:
            figure, ax = plt.subplots(len(columns))
            plt.tight_layout(pad=2)

        for i in range(len(columns)):
            ax[i].plot(df[columns[i]])
            ax[i].set_title(columns[i])
        return figure, ax
