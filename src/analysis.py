import numpy as np
import pandas as pd
from matplotlib import pyplot as plt


class Analysis:
    col_control = ["Score", "Execution time", "Same score count"]
    col_factors = ["Factor team amounts", "Factor player dependency", "Factor team exp"]

    def __init__(self, columns=None):
        self.col_added = columns
        self.cols = set(["Iteration"]+self.col_control+self.col_factors+(columns if columns else []))
        self.rows = []
        self.iteration = 0

    def add_row(self, row: dict):
        row.update({"Iteration": self.iteration})
        self.rows += [row]
        # self.df_evolution.append(row.update({"Iteration": self.iteration}))

    def next_iteration(self):
        self.iteration += 1

    def print_information(self):
        print(f"Iteration {self.rows[-1]['Iteration']}: Score {self.rows[-1]['Score']:.6f}, "
              f"iter without improvement {int(self.rows[-1]['Same score count'])} "
              f"({self.rows[-1]['Execution time']:.0f} ms)")

    def plot_analysis_club(self):
        df_evolution = pd.DataFrame(self.rows)
        best_5 = df_evolution.set_index("Iteration").groupby("Tournament id")["Score"].describe()["max"].sort_values()[-5:]
        fig1, ax = plt.subplots(2, sharex=True)
        grouped = df_evolution.set_index("Iteration").groupby("Tournament id")
        for i, col in enumerate(["League", "Score"]):
            ax[i].set_title(col)
            grouped[col].plot(ax=ax[i], legend=True)

        fig2, ax = plt.subplots(2, sharex=True)
        filter = df_evolution["Tournament id"].isin(best_5.index.values)
        grouped = df_evolution[filter].set_index("Iteration").groupby("Tournament id")
        for i, col in enumerate(["League", "Score"]):
            ax[i].set_title(col)
            grouped[col].plot(ax=ax[i], legend=True)
        return fig1, fig2

    def plot_analysis(self, figure=None, ax=None):
        df_evolution = pd.DataFrame(self.rows)
        col_amount = len(self.col_control) + 1
        best = df_evolution.set_index("Iteration").groupby("Tournament id")["Score"].describe()["max"].sort_values()[-1:]
        filter = df_evolution["Tournament id"].isin(best.index.values)
        grouped = df_evolution[filter].set_index("Iteration").groupby("Tournament id")
        if not figure:
            figure, ax = plt.subplots(col_amount,
                                      gridspec_kw={'height_ratios': [1]*len(self.col_control) + [len(self.col_control)]},
                                      sharex=True)
            plt.tight_layout(pad=2)

        for i in range(len(self.col_control)):
            grouped[self.col_control[i]].plot(ax=ax[i])
            ax[i].set_title(self.col_control[i])

        grouped[self.col_factors].plot(ax=ax[-1], label=self.col_factors)
        ax[-1].set_title("Factors")
        ax[-1].set_xlim([0, self.iteration])
        ax[-1].legend()
        return figure, ax
