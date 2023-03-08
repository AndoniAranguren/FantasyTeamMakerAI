import math
from concurrent.futures import ThreadPoolExecutor, as_completed

import numpy as np
import random as rnd

from team import Team
from src.config import CONSTRAIN_GENDER_RULE, PLAYER_MINIMUM, MAX_PLAYERS_IN_TEAM, MAX_EXP


class Tournament:
    def __init__(self, player_pool, teams,
                 referee_constrains=[1, 2, 3, 6],
                 position_constrains=[1, 2, 3, 1],
                 factors=[0.3, 0.5, 0.1]):
        self.team_list = np.array([])
        self.player_pool = np.array(player_pool)
        self.referee_constrains = referee_constrains    # [HR, SR, AR, SC]
        self.position_constrains = position_constrains  # [seeker, beater, chaser, keeper]
        self.factors = factors

        self.moves = [self.move_do_nothing,
                      self.move_transfer_one_player,
                      self.move_trade_two_players]

        if type(teams) is int:
            self.team_amount = teams
            self.initialize_state()

        else:
            self.team_amount = len(teams)
            for team in teams:
                self.add_team(team)

            player_without_team = [player if player.team is None else None for player in player_pool]
            for player in player_without_team:
                self.team_list[self.random_team_pos()].add_player(player)

    def random_team_pos(self):
        return rnd.randint(0, len(self.team_list) - 1)

    def add_team(self, team: Team):
        self.team_list = np.append(self.team_list, team)

    def remove_team(self, team: Team):
        self.team_list = np.delete(self.team_list, np.where(self.team_list == team))

    def move_do_nothing(self):
        pass

    def move_transfer_one_player(self):
        team1 = self.random_team_pos()
        team2 = self.random_team_pos()
        while team1 == team2:
            team2 = self.random_team_pos()
        transfer_player = self.team_list[team1].get_transfer_player()
        self.team_list[team2].add_player(transfer_player)

    def move_trade_two_players(self):
        team1 = self.random_team_pos()
        team2 = self.random_team_pos()
        while team1 == team2:
            team2 = self.random_team_pos()
        transfer_player1 = self.team_list[team1].get_transfer_player()
        transfer_player2 = self.team_list[team2].get_transfer_player()
        self.team_list[team2].add_player(transfer_player1)
        self.team_list[team1].add_player(transfer_player2)

    def perform_move(self):
        self.moves[rnd.randint(0, len(self.moves) - 1)]()

    def evaluate_constrains(self):
        def neg_amount(array):
            return [x for x in array if x < 0]
        constr_list = [[team.constrains_referees(self.referee_constrains) for team in self.team_list],
                       [team.constrains_genders(CONSTRAIN_GENDER_RULE) for team in self.team_list],
                       [team.constrains_positions_naive(self.position_constrains) for team in self.team_list]]
        for i, constr in enumerate(constr_list):
            negs = neg_amount(constr)
            if len(negs) > 0:
                perc_teams_not_fulfilling = len(negs)/len(self.team_list)
                constr_left_to_fulfill = len(constr_list) - i
                return - perc_teams_not_fulfilling - constr_left_to_fulfill/len(constr_list)
        return 0

    def evaluate_tournament(self):
        # Constrain analysis
        score = self.evaluate_constrains() * 1
        if score < 0:
            return score, None

        # Multifactorial analysis
        with ThreadPoolExecutor(max_workers=len(self.team_list)) as executor:
            results = [executor.submit(team.evaluate_subcompositions, self.position_constrains)
                       for team in self.team_list]
            scores_team_comp = [f.result() for f in as_completed(results)]

        constrains_not_fullfilled = [scores[0] for scores in scores_team_comp if scores[0] != 0]
        if len(constrains_not_fullfilled) > 0:
            return np.average(constrains_not_fullfilled), None

        factors = np.array([scores[1] for scores in scores_team_comp]).T

        max_combinations = math.comb(MAX_PLAYERS_IN_TEAM, PLAYER_MINIMUM)
        f_team_amount = 1 - np.std(factors[0]/max_combinations)
        f_player_dep = 1 - max(factors[1])
        f_team_exp = 1 - np.std(factors[2]/MAX_EXP)

        weighted_factors = [f_team_amount * self.factors[0],
                            f_player_dep * self.factors[1],
                            f_team_exp * self.factors[2]]
        return sum(weighted_factors)*100, weighted_factors

    def initialize_state(self):
        for i in range(self.team_amount - len(self.team_list)):
            self.add_team(Team())

        for player in [player if player.team is None else None for player in self.player_pool]:
            self.team_list[self.random_team_pos()].add_player(player)

    def __str__(self):
        result = self.evaluate_tournament()
        text = "========= Tournament ==========\n"
        text += f"Score is {result[0]}\n" \
                f"Factor scores {result[1]}\n" \
                f"with weights {self.factors}"
        for teams in self.team_list:
            text += str(teams)
        return text
