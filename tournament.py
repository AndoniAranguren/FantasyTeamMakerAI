from concurrent.futures import ThreadPoolExecutor, as_completed

import numpy as np
import random as rnd

from team import Team


class Tournament:
    player_minimum = 7

    def __init__(self, player_pool, teams, referee_constrains=[1, 2, 3, 6], position_constrains=[1, 2, 3, 1]):
        self.team_list = np.array([])
        self.player_pool = np.array(player_pool)
        self.referee_constrains = referee_constrains    # [HR, SR, AR, SC]
        self.position_constrains = position_constrains  # [seeker, beater, chaser, keeper]

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

    def evaluate_referees(self):
        valid = [team.constrains_referees(self.referee_constrains) for team in self.team_list]
        if sum([True if x < 0 else False for x in valid]) > 0:
            return sum([x if x < 0 else 0 for x in valid])
        else:
            score = np.array([team.evaluate_referees(self.referee_constrains) for team in self.team_list])
            return min(score)

    def evaluate_team_composition(self):
        with ThreadPoolExecutor(max_workers=len(self.team_list)) as executor:
            results = [executor.submit(team.evaluate_positions2, self.position_constrains) for team in self.team_list]
            score = [f.result() for f in as_completed(results)]
        return min(score)

    def evaluate_tournament(self):
        score = np.array([])
        score = np.append(score, self.evaluate_referees())
        score = np.append(score, self.evaluate_team_composition())
        if sum([True if x < 0 else False for x in score]) > 0:
            return sum([x if x < 0 else 0 for x in score])
        else:
            return sum(score) / len(score)
        return score

    def initialize_state(self):
        for i in range(self.team_amount - len(self.team_list)):
            self.add_team(Team())

        for player in [player if player.team is None else None for player in self.player_pool]:
            self.team_list[self.random_team_pos()].add_player(player)

    def __str__(self):
        text = "========= Tournament ==========\n"
        text += f"Score is {self.evaluate_tournament()}\n"
        for teams in self.team_list:
            text += str(teams)
        return text


