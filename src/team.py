import concurrent
import itertools
from collections import Counter

import numpy as np
import random as rnd

from player import Player
import player_composition
from src.config import PLAYER_MINIMUM, CONSTRAIN_GENDER_RULE


class Team:

    def __init__(self, player_list=[]):
        self.player_list = np.array([])
        self.player_compositions = np.array([])
        for player in player_list:
            self.add_player(player)

    def add_player(self, player: Player):
        self.player_list = np.append(self.player_list, player)

    def remove_player(self, player: Player):
        self.player_list = np.delete(self.player_list, np.where(self.player_list == player))

    def get_transfer_player(self):
        player = self.player_list[rnd.randint(0, len(self.player_list) - 1)]
        self.remove_player(player)
        return player

    def get_referee_titles(self): return sum([player.referee_titles for player in self.player_list])

    def get_positions(self): return sum([player.positions for player in self.player_list])

    def constrains_genders(self, max_gender: int = CONSTRAIN_GENDER_RULE):
        unique_genders = set([x.gender for x in self.player_list])
        gender_count = [[x.gender for x in self.player_list].count(gender) for gender in unique_genders]
        max_gender_count = [gender if gender <= max_gender else max_gender for gender in gender_count]
        max_combinations = sum(max_gender_count)
        if max_combinations < PLAYER_MINIMUM:
            return -1
        return max_combinations

    def constrains_referees(self, requisites: [int]):
        return min(self.get_referee_titles() - np.array(requisites))

    def constrains_positions_naive(self, requisites: [int]):
        try:
            return min(self.get_positions() - requisites)
        except:
            return -1

    def constrains_positions(self, requisites: [int]):
        doesnt_fullfill = min(self.get_positions() - np.array(requisites))
        list(itertools.combinations(self.player_list, PLAYER_MINIMUM))
        return doesnt_fullfill

    def evaluate_referees(self, requisites: [int]):
        return sum(self.get_referee_titles() / requisites)

    def evaluate_subcompositions(self, requisites: [int]):
        return player_composition.PlayerComposition(self.player_list, requisites).evaluate_player_composition()

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
