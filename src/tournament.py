import itertools
import math
from concurrent.futures import ThreadPoolExecutor, as_completed

import numpy as np
import random as rnd

from team import Team
from src.config import CONSTRAIN_GENDER_RULE, PLAYER_MINIMUM, MAX_PLAYERS_IN_TEAM, MAX_EXP, REFEREE_CONSTRAINS, POSITION_CONSTRAINS, FACTORS


class Tournament:
    def __init__(self, player_pool, teams: int, tournament_id=0,
                 referee_constrains=REFEREE_CONSTRAINS,
                 position_constrains=POSITION_CONSTRAINS,
                 factors=FACTORS):
        self.tournament_id = tournament_id
        self.team_list = np.array([])
        self.player_pool = np.array(player_pool)
        self.referee_constrains = referee_constrains    # [HR, SR, AR, SC]
        self.position_constrains = position_constrains  # [seeker, beater, chaser, keeper]
        self.factors = factors

        self.moves = [self.move_do_nothing,
                      self.move_transfer_one_player,
                      self.move_trade_two_players]

        self.team_amount = teams
        self.initialize_state()

    def random_team_pos(self):
        return rnd.randint(0, len(self.team_list) - 1)

    def add_team(self, team: Team):
        self.team_list = np.append(self.team_list, team)

    def remove_team(self, team: Team):
        self.team_list = np.delete(self.team_list, np.where(self.team_list == team))

    def move_do_nothing(self):
        pass

    def move_transfer_one_player(self, count=0):
        if count < 10:
            pick_team = list(range(len(self.team_list)))
            rnd.shuffle(pick_team)
            team1 = pick_team[0]
            team2 = pick_team[1]
            try:
                transfer_player = self.team_list[team1].get_transfer_player()
                if transfer_player is None:
                    raise Exception
                self.team_list[team2].add_player(transfer_player)
            except:
                # This might happen when trying to get a player from an empty team
                self.move_transfer_one_player(count+1)

    def move_trade_two_players(self, count=0):
        if count < 10:
            pick_team = list(range(len(self.team_list)))
            rnd.shuffle(pick_team)
            team1 = pick_team[0]
            team2 = pick_team[1]
            try:
                transfer_player1 = self.team_list[team1].get_transfer_player()
                if transfer_player1 is None:
                    raise Exception

                transfer_player2 = self.team_list[team2].get_transfer_player()
                if transfer_player2 is None:
                    self.team_list[team1].add_player(transfer_player1)
                    raise Exception

                self.team_list[team2].add_player(transfer_player1)
                self.team_list[team1].add_player(transfer_player2)
            except:
                # This might happen when trying to get a player from an empty team
                self.move_trade_two_players(count+1)

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
        players_per_team = round(len(self.player_pool)/self.team_amount)
        for i in range(self.team_amount - len(self.team_list)):
            low = players_per_team*i
            up = players_per_team*(i+1)
            self.add_team(Team(self.player_pool[low:up]))

    def characterize_tournament(self):
        characterization = [0]*len(self.player_pool)
        for t, team in enumerate(self.team_list):
            for player in team.player_list:
                characterization[player.player_id] = t
        return characterization

    def __str__(self):
        result = self.evaluate_tournament()
        text = f"========= Tournament({self.tournament_id}) ==========\n"
        text += f"Score is {result[0]}\n" \
                f"Factor scores {result[1]}\n" \
                f"with weights {self.factors}"
        for teams in self.team_list:
            text += str(teams)
        return text
