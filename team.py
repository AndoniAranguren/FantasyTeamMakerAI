from collections import Counter

import numpy as np
import random as rnd

from player import Player


class Team:

    def __init__(self, player_list=[]):
        self.player_list = np.array([])
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

    def get_referee_titles(self):
        return sum([player.referee_titles for player in self.player_list])

    def constrains_referees(self, requisites: [int]):
        doesnt_fullfill = min(self.get_referee_titles() - np.array(requisites))
        return doesnt_fullfill

    def evaluate_referees(self):
        ref_types = len(self.get_referee_titles())
        # Importance HR > SR > AR > SC
        return sum(self.get_referee_titles() * [ref_types / (pos + 1) for pos in range(ref_types)])

    def __str__(self):
        names = [player.name for player in self.player_list]
        genders = Counter([player.gender for player in self.player_list]).values()
        experience = sum([player.experience for player in self.player_list])
        referees = self.get_referee_titles().__str__()
        text =  "\nTeam=============\n"
        text += f"-Genders: {genders}\n"
        text += f"-Total exp:{experience}\n"
        text += f"-Refs: {referees}\n"
        text += f"-Names ({len(names)}):{names}\n"
        return text
