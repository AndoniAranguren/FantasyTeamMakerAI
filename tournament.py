import numpy as np
import random as rnd

from team import Team


class Tournament:
    player_minimum = 7

    def __init__(self, player_pool, teams, referee_requisites=[1, 2, 3, 6]):
        self.team_list = np.array([])
        self.player_pool = np.array(player_pool)
        self.referee_requisites = referee_requisites

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

    # def random_team(self) -> Team:
    #     return self.team_list[rnd.randint(0, len(self.team_list))]
    #
    # def move_create_new_team(self):
    #     self.add_team(Team())
    #     for i in range(self.player_minimum):
    #         team = rnd.randint(0, len(self.team_list - 1))
    #         transfer_player = self.team_list[team].get_transfer_player()
    #         self.team_list[len(self.team_list)].add_player(transfer_player)
    #
    # def move_destroy_team(self):
    #     del_team = self.random_team()
    #     while len(self.team_list[del_team].player_list) > 0:
    #         transfer_player = self.team_list[del_team].get_transfer_player()
    #         team = rnd.randint(0, len(self.team_list - 1))
    #         while team == del_team:
    #             team = self.random_team()
    #         self.team_list[team].add_player(transfer_player)
    #     self.add_team(Team())

    def perform_move(self):
        self.moves[rnd.randint(0, len(self.moves) - 1)]()

    def evaluate_tournament(self):
        valid = [team.constrains_referees(self.referee_requisites) for team in self.team_list]
        if sum([True if x < 0 else False for x in valid]) > 0:
            return sum([x if x < 0 else 0 for x in valid])
        else:
            score = np.array([team.evaluate_referees() for team in self.team_list])
            return sum(score) / len(score)

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
