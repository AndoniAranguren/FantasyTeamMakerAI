import copy
import os

import random as rnd
import time
import datetime

import numpy as np
import pandas as pd

from analysis import Analysis
from player import Player
from src import import_export_tool
from tournament import Tournament

analysis = Analysis()


def generate_player_pool(player_amount, rnd_seed):
    if rnd_seed:
        rnd.seed(rnd_seed)
    print(f"Generating {player_amount} random players with seed {rnd_seed}")
    hr = [1, 1, 1, 1]
    ar = [0, 1, 1, 1]
    sr = [0, 0, 1, 1]
    sc = [0, 0, 0, 1]
    nn = [0, 0, 0, 0]
    referees = [hr, ar, ar, sr, sr, sc, sc, sc, nn, nn, nn]
    names = ["Joey", "Aurelio", "Evan", "Donny", "Foster", "Dwayne", "Grady", "Quinton", "Darin", "Mickey", "Hank",
             "Kim", "Peter", "Jeremy", "Jess", "Jimmie", "Vern", "Pasquale", "Romeo", "Chris", "Dale", "Beau", "Cliff",
             "Timothy", "Raphael", "Brain", "Mauro", "Luke", "Myron", "Omar", "Reynaldo", "Major", "Clinton", "Nolan",
             "Raymond", "Lucien", "Carey", "Winfred", "Dan", "Abel", "Elliott", "Brent", "Chuck", "Dirk", "Tod",
             "Emerson", "Dewey", "Scot", "Enrique", "Al", "Beatrice", "Brandy", "Kathy", "Jane", "Marcy", "Shelly",
             "Lucy", "Cathy", "Joanna", "Doris", "Lindsay", "Staci", "Shelia", "Rosanne", "Rebecca", "Luz", "Flora",
             "Rosalie", "Karla", "Phoebe", "Meagan", "Virginia", "Amanda", "Katy", "Karla", "Deanne", "Pearl",
             "Christi", "Victoria", "Ola", "Alexandra", "Marina", "Lorraine", "Sybil", "Adeline", "Taylor", "Anita",
             "Aurora", "Neva", "Alisha", "Maria", "Erna", "Gwendolyn", "Brenda", "Bethany", "Sybil", "Earline", "June",
             "Brandy", "Sue", "Jose", "María", "Jaime", "Inés", "Ane", "Yeray", "Aitziber", "Ro", "Andoni"]
    genders = ["M", "M", "M", "M", "F", "F", "F", "F", "NB", "NB"]
    # [seeker, beater, chaser, keeper]

    max_experiencia = 5

    player_pool = []
    for i in range(player_amount):
        amount_positions = int(np.floor(rnd.gauss(2, 1)))
        amount_positions = 4 if amount_positions >= 4 else 1 if amount_positions <= 0 else amount_positions
        positions = [0] * (4 - amount_positions) + [1] * amount_positions
        rnd.shuffle(positions)

        player_pool += [Player(i, names[rnd.randint(0, len(names) - 1)],
                               genders[rnd.randint(0, len(genders) - 1)],
                               referees[rnd.randint(0, len(referees) - 1)],
                               positions,
                               rnd.randint(0, max_experiencia))]
    return player_pool


def improve_tournament(best_evaluation, best_tournament_setting, same_score_count, moves):
    return_factors = [None, None, None]
    time1 = time.time()
    new_tournament_setting = perform_moves(best_tournament_setting[0], moves)

    evaluation, weighted_factors = new_tournament_setting.evaluate_tournament()
    if evaluation > best_evaluation[0]:
        return_factors = weighted_factors if weighted_factors else return_factors
        best_evaluation[0] = evaluation
        best_tournament_setting[0] = new_tournament_setting
        same_score_count[0] = 0
    else:
        same_score_count[0] += 1
    time2 = time.time()
    execution_time = (time2 - time1) * 1000.0
    return execution_time, return_factors


def perform_moves(solution: Tournament, moves: int) -> Tournament:
    new_solution = copy.deepcopy(solution)
    for m in range(moves):
        new_solution.perform_move()
    return new_solution


def sort_by_performance(league: [[Tournament, [float,[]]]]):
    league.sort(key=lambda x: x[1][0], reverse=True)
    return league


def get_best_solution(solutions: [[Tournament, [float, []]]]) -> [Tournament, int]:
    pos_best_sol = np.argmax([sol[1][0] for sol in solutions])
    return solutions[pos_best_sol]


def play_league(last_season: [[Tournament, [float, []]]], moves: int) -> [[Tournament, int]]:
    # Club try improving themselves this season
    new_club = [perform_moves(solution[0], moves) for solution in last_season]
    new_season_mutation = [[new_sol, new_sol.evaluate_tournament()] for new_sol in new_club]

    # Clubs check if their current playstyle is better than last years and keep with the best one
    new_season = [get_best_solution([new_season_mutation[i], last_season[i]]) for i in range(len(last_season))]

    # The league gets resolved with the better scoring clubs going up
    return sort_by_performance(new_season)


def play_crossings(new_league_list: [[[Tournament, float]]], autocross: bool = False):
    for i, league in enumerate(new_league_list[:-1]):
        upper_league_last = new_league_list[i][-1]
        lower_league_first = new_league_list[i+1][0]
        # If the club from the lower league is better promote it and demote the other one
        if autocross or (upper_league_last[1] < lower_league_first[1]):
            new_league_list[i][-1] = lower_league_first
            new_league_list[i + 1][0] = upper_league_last
    return new_league_list


def generate_league(player_pool, team_amount, leagues_movements, clubs_per_league):
    leagues = len(leagues_movements)
    club_list = [Tournament(player_pool, team_amount, c) for c in range(clubs_per_league * leagues)]
    club_list = sort_by_performance([[club, club.evaluate_tournament()] for club in club_list])
    league_list = [club_list[clubs_per_league * i:clubs_per_league * (i + 1)] for i in range(clubs_per_league - 1)]
    return league_list


def optimize_tournament_league_metaheuristic(player_pool, team_amount: int,
                                             leagues_movements: [int], clubs_per_league: int,
                                             iterations: int = 1000, stop_same: int = 500,
                                             autocross: bool =False):
    global analysis
    analysis = Analysis(["League", "Club rank"])
    league_list = generate_league(player_pool, team_amount, leagues_movements, clubs_per_league)
    same_score_count = 0
    w_fact_last = [None, None, None]
    last_best = league_list[0][0][1][0]
    for i in range(iterations):
        time1 = time.time()
        # Play this season
        new_league_list = [play_league(league, leagues_movements[i]) for i, league in enumerate(league_list)]
        # Play the crossings to get to the upper leagues
        league_list = play_crossings(new_league_list, autocross)

        first_club = league_list[0][0]

        if first_club[1][0] >= 0 and same_score_count >= stop_same:
            break
        same_score_count += 1
        if last_best < first_club[1][0]:
            same_score_count = 0
            last_best = first_club[1][0]

        # Store information to analyse the algorithm
        best_evaluation = first_club[1][0]
        w_fact_last = first_club[1][1] if first_club[1][1] is not None else w_fact_last
        time2 = time.time()
        execution_time = (time2 - time1) * 1000.0
        for l, league in enumerate(reversed(league_list)):
            for c, club in enumerate(reversed(league)):
                w_fact = first_club[1][1] if first_club[1][1] is not None else [None, None, None]
                row = {"League": len(league_list)-l, "Club rank": len(league)-c, "Score": club[1][0],
                       "Characterization": club[0].characterize_tournament(),
                       "Tournament id": club[0].tournament_id,
                       "Factor team amounts": w_fact[0],
                       "Factor player dependency": w_fact[1],
                       "Factor team exp": w_fact[2],
                       "Execution time": execution_time, "Same score count": same_score_count}
                analysis.add_row(row)
        analysis.print_information()
        analysis.next_iteration()
    return league_list[0][0][0]


def optimize_tournament(player_pool, team_amount: int, iterations: int = 1000, moves: int = 5,
                        stop_same: int = 500):
    print(f"Optimizing tournament with {team_amount} teams. Max iterations {iterations}.")
    global analysis
    analysis = Analysis()
    best_tournament_setting = [Tournament(player_pool, team_amount)]
    best_evaluation = [best_tournament_setting[0].evaluate_tournament()[0]]

    same_score_count = [0]
    w_fact_last = [None, None, None]
    for i in range(iterations):
        # Break the loop if we already have a valid score but haven't improved in a long while
        if best_evaluation[0] >= 0 and same_score_count[0] >= stop_same:
            break

        execution_time, w_fact = improve_tournament(best_evaluation, best_tournament_setting, same_score_count, moves)
        w_fact_last = w_fact if w_fact[0] is not None else w_fact_last
        row = {"Score": best_evaluation[0],
               "Factor team amounts": w_fact[0],
               "Factor player dependency": w_fact[1],
               "Factor team exp": w_fact[2],
               "Execution time": execution_time, "Same score count": same_score_count[0]}
        analysis.add_row(row)
        analysis.print_information()
        analysis.next_iteration()
    return best_tournament_setting


def main():
    player_amount = 75
    team_amount = 5
    rnd_seed = 100
    iterations = 150
    stop_same = 50
    leagues_movements = [1, 5, 10]
    clubs_per_league = 4
    autocross = False
    player_pool = import_export_tool.read_players("../data/form emerald.csv")
    # player_pool = generate_player_pool(player_amount, rnd_seed=rnd_seed)
    # best_tournament_setting = optimize_tournament(player_pool, team_amount, iterations=iterations)
    best_tournament_setting = optimize_tournament_league_metaheuristic(player_pool, team_amount,
                                                                       leagues_movements, clubs_per_league,
                                                                       iterations, stop_same, autocross)
    fig, ax = analysis.plot_analysis()
    fig1, fig2 = analysis.plot_analysis_club()
    project_path = os.path.dirname(__file__)[:-len("src/")]
    file = "-".join(["autocross" if autocross else "",
                     f"{datetime.date.today()}",
                     f"{player_amount}players",
                     f"{team_amount}teams",
                     f"{len(leagues_movements)}leagues",
                     f"{'_'.join([str(x) for x in leagues_movements])}movement",
                     f"{rnd_seed}seed",
                     f"{iterations}iterations"])
    fig.savefig(project_path + "/analysis/Analysis-tournament_league_info-autocross-" + file + ".png")
    fig1.savefig(project_path + "/analysis/Analysis-tournament_league-autocross-" + file + ".png")
    fig2.savefig(project_path + "/analysis/Analysis-tournament_league_top-autocross-" + file + ".png")
    result = best_tournament_setting.__str__()
    with open(project_path + "/analysis/Analysis-tournament_league_info-" + file + ".txt", "w") as text_file:
        text_file.write(result)


main()
