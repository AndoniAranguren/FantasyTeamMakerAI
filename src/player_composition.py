import itertools

import numpy as np
import result_vault
from src.config import CONSTRAIN_GENDER_RULE, PLAYER_MINIMUM


class PlayerComposition:
    def __init__(self, player_list, position_requisites):
        player_ids = [player.player_id for player in player_list]
        player_ids.sort()
        self.player_composition_id = ",".join([str(x) for x in player_ids])
        self.player_list = player_list
        self.position_requisites = position_requisites
        self.gender_count = []
        self.team_subcompositions = []
        self.team_subcompositions_computed = False

    def get_gender_count(self):
        if not self.gender_count:
            unique_genders = set([x.gender for x in self.player_list])
            self.gender_count = [[x.gender for x in self.player_list].count(gender) for gender in unique_genders]
        return self.gender_count

    def get_team_subcompositions(self):
        """Utility players can make multiple player compositions from the same set of players"""
        if not self.team_subcompositions_computed:
            unique_pos = len(self.player_list[0].positions) # len = 4 keeper, chaser, beater, seeker
            player_per_positions = [[p for p in self.player_list if p.positions[pos]] for pos in range(unique_pos)]
            seeker = list(itertools.combinations(player_per_positions[0], self.position_requisites[0]))
            beater = list(itertools.combinations(player_per_positions[1], self.position_requisites[1]))
            chaser = list(itertools.combinations(player_per_positions[2], self.position_requisites[2]))
            keeper = list(itertools.combinations(player_per_positions[3], self.position_requisites[3]))
            team_subcomp = [[s, b, c, k] for s in seeker for b in beater for c in chaser for k in keeper]

            # Flatten array:
            team_subcomp = [[item for sub_list in list_2D for item in sub_list] for list_2D in team_subcomp]

            # Remove those with duplicates
            if team_subcomp:
                before_len = len(team_subcomp)
                team_subcomp = [team_comp for team_comp in team_subcomp if len(team_comp) == len(set(team_comp))]
                after_len = len(self.team_subcompositions)
            self.team_subcompositions = team_subcomp
            self.team_subcompositions_computed = True
        return self.team_subcompositions

    def constrains_genders(self):
        capped_genders = [x if x < CONSTRAIN_GENDER_RULE else CONSTRAIN_GENDER_RULE for x in self.get_gender_count()]
        return sum(capped_genders) > PLAYER_MINIMUM

    def constrains_team_subcompositions(self):
        return self.get_team_subcompositions() is not None and len(self.get_team_subcompositions()) > 0

    def factor_team_amount(self):
        return len(self.team_subcompositions)

    def factor_player_dependency(self):
        count_players = {player.player_id: 0 for player in self.player_list}
        total_len = len(self.team_subcompositions)
        for team_subcomp in self.team_subcompositions:
            for player in team_subcomp:
                count_players[player.player_id] += 1 / total_len
        return max(count_players.values())

    def factor_team_experience(self):
        team_experience = [[player.experience for player in team_subcomp] for team_subcomp in self.team_subcompositions]
        return np.mean(team_experience)

    def __evaluate__(self):
        if not self.constrains_genders():
            return -2000, None
        if not self.constrains_team_subcompositions():
            return -1000, None

        factor_team_amount = self.factor_team_amount()
        factor_player_dependency = self.factor_player_dependency()
        factor_team_experience = self.factor_team_experience()

        return 0, [factor_team_amount, factor_player_dependency, factor_team_experience]

    def evaluate_player_composition(self):
        return result_vault.compute_player_composition(self.player_composition_id, self.__evaluate__)
