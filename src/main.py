import copy
import os

import random as rnd
import time
import datetime

import numpy as np

from analysis import Analysis
from player import Player
from tournament import Tournament

analysis = None


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
    time1 = time.time()
    new_tournament_setting = copy.deepcopy(best_tournament_setting[0])
    for m in range(moves):
        new_tournament_setting.perform_move()

    evaluation = new_tournament_setting.evaluate_tournament()
    if evaluation > best_evaluation[0]:
        best_evaluation[0] = evaluation
        best_tournament_setting[0] = new_tournament_setting
        same_score_count[0] = 0
    else:
        same_score_count[0] += 1
    time2 = time.time()
    execution_time = (time2-time1)*1000.0
    return execution_time


def optimize_tournament(player_pool: int, team_amount: int, iterations: int = 10000, moves: int = 5, stop_same: int = 100):
    print(f"Optimizing tournament with {team_amount} teams. Max iterations {iterations}.")
    global analysis
    analysis = Analysis(iterations)
    best_tournament_setting = [Tournament(player_pool, team_amount)]
    best_evaluation = [best_tournament_setting[0].evaluate_tournament()]

    same_score_count = [0]
    for i in range(iterations):
        # Break the loop if we already have a valid score but haven't improved in a long while
        if best_evaluation[0] >= 0 and same_score_count[0] >= stop_same:
            break

        execution_time = improve_tournament(best_evaluation, best_tournament_setting, same_score_count, moves)

        analysis.add_execution_time(execution_time)
        analysis.add_same_score_count(same_score_count[0])
        analysis.add_improvement(best_evaluation[0])
        analysis.print_information()
        analysis.next_iteration()
    return best_tournament_setting


def main():
    player_amount = 75
    team_amount = 5
    rnd_seed = 100
    iterations = 15
    player_pool = generate_player_pool(player_amount, rnd_seed=rnd_seed)
    best_tournament_setting = optimize_tournament(player_pool, team_amount, iterations=iterations)
    figure, ax = analysis.plot_analysis()
    project_path = os.path.dirname(__file__)[:-len("src/")]
    file = "_".join([f"Analysis",
                     f"{datetime.date.today()}",
                     f"{player_amount}players",
                     f"{team_amount}teams",
                     f"{rnd_seed}seed",
                     f"{iterations}iterations"])
    figure.savefig(project_path+"/analysis/"+file+".png")
    result = best_tournament_setting[0].__str__()
    with open(project_path+"/analysis/"+file+".txt", "w") as text_file:
        text_file.write(result)


main()
