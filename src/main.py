import copy
import hashlib
import json
import os

import random as rnd
import time
import datetime

import numpy as np
import pandas as pd

import config
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


def sort_by_performance(league: [[Tournament, [float, []]]]):
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
    club_list = []
    for c in range(clubs_per_league * leagues):
        club_list += [Tournament(player_pool, team_amount, c)]
        np.random.shuffle(player_pool)
    club_list = sort_by_performance([[club, club.evaluate_tournament()] for club in club_list])
    league_list = [club_list[clubs_per_league * i:clubs_per_league * (i + 1)] for i in range(leagues)]
    return league_list


def check_for_last_iteration(hash_path):
    embedding_path = f"{hash_path}/solution_embedding.csv"
    embedding_solution, analysis_saved = None, None
    if os.path.exists(embedding_path):
        embedding_solution = pd.read_csv(embedding_path, index_col=0)

    analysis_path = f"{hash_path}/analysis.csv"
    if os.path.exists(analysis_path):
        analysis_saved = pd.read_csv(analysis_path, index_col=0)

    return embedding_solution, analysis_saved


def read_league(player_pool, team_amount, leagues_movements, clubs_per_league, embedding_solution):
    leagues = len(leagues_movements)
    club_list = []
    for c, embedding in enumerate(embedding_solution.values):
        club_list += [Tournament(player_pool, team_amount, tournament_id=c, embedding=embedding)]
        np.random.shuffle(player_pool)
    club_list = sort_by_performance([[club, club.evaluate_tournament()] for club in club_list])
    league_list = [club_list[clubs_per_league * i:clubs_per_league * (i + 1)] for i in range(leagues)]
    return league_list


def initialize_execution(player_pool, team_amount, leagues_movements, clubs_per_league, hash_path):
    embedding_solution, analysis_saved = check_for_last_iteration(hash_path)

    if analysis_saved is not None:
        analysis = Analysis(["League", "Club rank"], df_saved=analysis_saved)
    else:
        analysis = Analysis(["League", "Club rank"])
    if embedding_solution is not None:
        league_list = read_league(player_pool, team_amount, leagues_movements, clubs_per_league, embedding_solution)
    else:
        league_list = generate_league(player_pool, team_amount, leagues_movements, clubs_per_league)
    return analysis, league_list, embedding_solution is not None


def optimize_tournament_league_metaheuristic(player_pool, team_amount: int,
                                             leagues_movements: [int], clubs_per_league: int,
                                             hash_path=None, save_temp_reach=50,
                                             iterations: int = 10000, stop_same: int = 250,
                                             autocross: bool = False):
    global analysis

    analysis, league_list, from_saved = initialize_execution(player_pool, team_amount,
                                                             leagues_movements, clubs_per_league, hash_path)

    same_score_count = 0
    w_fact_last = [None, None, None]
    last_best = league_list[0][0][1][0]
    for i in range(iterations):
        if i == 0 and from_saved:
            i = analysis.iteration
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

        # Save temps
        if hash_path and i%save_temp_reach == 0:
            embedding_list = []
            for l, league in enumerate(reversed(league_list)):
                for c, club in enumerate(reversed(league)):
                    tournament = club[0]
                    embedding_list += [tournament.get_solution_embedding()]
            embedding_df = pd.DataFrame(embedding_list, index=["Solution "+str(x) for x in range(len(embedding_list))])
            embedding_df.to_csv(f"{hash_path}/solution_embedding.csv")
            analysis.save(hash_path)
            print("Temporal files saved")
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


def create_input_data_hash(file):
    # BUF_SIZE is totally arbitrary, change for your app!
    BUF_SIZE = 65536  # lets read stuff in 64kb chunks!

    md5 = hashlib.md5()
    sha1 = hashlib.sha1()

    with open(file, 'rb') as f:
        while True:
            data = f.read(BUF_SIZE)
            if not data:
                break
            md5.update(data)
            sha1.update(data)
    hash_value = md5.hexdigest()
    print("MD5: {0}".format(md5.hexdigest()))

    folder = f"{config.PATHS_SAVE_TEMP_FILES}/{hash_value}"
    if not os.path.exists(folder):
        os.makedirs(folder)

    return hash_value


def create_config_data_hash(config_params, hash_of_file):
    # BUF_SIZE is totally arbitrary, change for your app!
    BUF_SIZE = 65536  # lets read stuff in 64kb chunks!

    md5 = hashlib.md5()
    sha1 = hashlib.sha1()

    json_dump = json.dumps(config_params, sort_keys=True).encode()
    md5.update(json_dump)
    sha1.update(json_dump)

    hash_of_config = md5.hexdigest()
    print("MD5: {0}".format(md5.hexdigest()))

    hash_path = f"{config.PATHS_SAVE_TEMP_FILES}/{hash_of_file}/{hash_of_config}"
    if not os.path.exists(hash_path):
        os.makedirs(hash_path)

    return hash_of_config, hash_path


def save_config(save_path, **params):
    with open(f"{save_path}/config.json", "w") as f:
        json.dump(params, f, sort_keys=True)


def main():
    rnd_seed = 43
    iterations = 10000
    stop_same = 250
    leagues_movements = [1, 3, 5, 10]
    clubs_per_league = 5
    autocross = False
    # team_amount = 3
    # player_pool, df = import_export_tool.read_players("./data/form emerald.csv")
    team_amount = 9
    file_path = "../data/Guardians of Bologna - vol4 - With Irene as cap.csv"
    player_pool, df = import_export_tool.read_players(file_path)
    # player_pool, df = import_export_tool.read_players("../data/Guardians of Bologna - vol4 - Without Irene as cap.csv")
    player_amount = df.shape[0]
    hash_of_file = create_input_data_hash(file_path)
    config_params = {"hash_of_file": hash_of_file,
                     "file_path": file_path,
                     "team_amount": team_amount,
                     "leagues_movement": leagues_movements,
                     "clubs_per_league": clubs_per_league,
                     "iterations": iterations,
                     "stop_same": stop_same,
                     "autocross": autocross}
    hash_of_config, hash_path = create_config_data_hash(config_params, hash_of_file)
    save_config(hash_path, config_params=config_params)
    best_tournament_setting = optimize_tournament_league_metaheuristic(player_pool, team_amount,
                                                                       leagues_movements, clubs_per_league,
                                                                       hash_path=hash_path,
                                                                       iterations=iterations, stop_same=stop_same,
                                                                       autocross=autocross)
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
    with open(project_path + "/analysis/Analysis-tournament_league_info-" + file + ".txt",
              "w", encoding="utf-8-sig") as text_file:
        text_file.write(result)


def main_generate():
    player_amount = 75
    team_amount = 2
    rnd_seed = 100
    iterations = 1500
    stop_same = 50
    leagues_movements = [1, 5, 10]
    clubs_per_league = 4
    autocross = False
    player_pool = generate_player_pool(player_amount, rnd_seed=rnd_seed)
    best_tournament_setting = optimize_tournament_league_metaheuristic(player_pool, team_amount,
                                                                       leagues_movements, clubs_per_league,
                                                                       iterations=iterations, stop_same=stop_same,
                                                                       autocross=autocross)
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


if __name__ == "__main__":
    main()
