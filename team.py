import concurrent
import itertools
from collections import Counter

import numpy as np
import random as rnd

from player import Player
import player_composition


class Team:

    def __init__(self, player_list=[]):
        self.player_list = np.array([])
        self.player_compositions = np.array([])
        for player in player_list:
            self.add_player(player)

    def add_player(self, player: Player):
        player.team = self
        self.player_list = np.append(self.player_list, player)

    def remove_player(self, player: Player):
        player.team = None
        self.player_list = np.delete(self.player_list, np.where(self.player_list == player))

    def get_transfer_player(self):
        player = self.player_list[rnd.randint(0, len(self.player_list) - 1)]
        self.remove_player(player)
        return player

    def get_referee_titles(self): return sum([player.referee_titles for player in self.player_list])

    def get_positions(self): return sum([player.positions for player in self.player_list])

    def constrains_referees(self, requisites: [int]):
        doesnt_fullfill = min(self.get_referee_titles() - np.array(requisites))
        return doesnt_fullfill

    def constrains_positions(self, requisites: [int]):
        doesnt_fullfill = min(self.get_positions() - np.array(requisites))
        list(itertools.combinations(self.player_list, 7))
        return doesnt_fullfill

    def evaluate_referees(self, requisites: [int]): return sum(self.get_referee_titles() / requisites)

    def evaluate_positions(self, requisites: [int]): return sum(self.get_positions() / requisites)

    def evaluate_positions2(self, requisites: [int]):
        player_all_compositions = [player_composition.PlayerComposition(x, requisites)
                                   for x in itertools.combinations(self.player_list, 7)]
        if not player_all_compositions:
            return -3

        with concurrent.futures.ThreadPoolExecutor() as tpe:
            results = [tpe.submit(player_composition.compute_player_composition, player_comp)
                       for player_comp in player_all_compositions]
            composition_evaluation = [f.result() for f in concurrent.futures.as_completed(results)]

        composition_without_failed = [x for x in composition_evaluation if x > 0]
        if composition_without_failed:
            return np.average(composition_without_failed)
        else:
            return max(composition_evaluation)

    def __str__(self):
        names = [player.name for player in self.player_list]
        genders = Counter([player.gender for player in self.player_list]).values()
        experience = sum([player.experience for player in self.player_list])
        positions = sum([player.positions for player in self.player_list])
        referees = self.get_referee_titles().__str__()
        text =  "\nTeam=============\n"
        text += f"\t-Genders: \t\t{genders}\n"
        text += f"\t-Total exp: \t{experience}\n"
        text += f"\t-Refs: \t\t{referees}\n"
        text += f"\t-Positions: \t{positions}\n"
        text += f"\t-Names ({len(names)}): \t{names}\n"
        return text
