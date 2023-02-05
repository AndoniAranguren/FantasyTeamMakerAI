import copy

import random as rnd

import matplotlib.pyplot as plt
import numpy as np

from player import Player
from tournament import Tournament


def generate_player_pool(player_amount):
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


def optimize_tournament(player_pool: int, team_amount: int, epoch: int = 10000, moves: int = 5, stop_same: int = 100):
    best_tournament_setting = Tournament(player_pool, team_amount)
    best_evaluation = best_tournament_setting.evaluate_tournament()

    improvement = np.array([])
    same_score_count = 0
    for i in range(epoch):
        # Break the loop if we already have a valid score but haven't improved in a long while
        if best_evaluation >= 0 and same_score_count >= stop_same:
            break

        new_tournament_setting = copy.deepcopy(best_tournament_setting)
        for m in range(moves):
            new_tournament_setting.perform_move()

        evaluation = new_tournament_setting.evaluate_tournament()
        if evaluation > best_evaluation:
            best_evaluation = evaluation
            best_tournament_setting = new_tournament_setting
            same_score_count = 0
        else:
            same_score_count += 1

        improvement = np.append(improvement, best_evaluation)
        print(f"Try number {i}, best evaluation {best_evaluation}, "
              f"current tries before improvement {same_score_count}")
    return best_tournament_setting, improvement


def improve_tournament(best_tournament_setting, best_evaluation, same_score_count, moves):
    new_tournament_setting = copy.deepcopy(best_tournament_setting)
    for m in range(moves):
        new_tournament_setting.perform_move()

    evaluation = new_tournament_setting.evaluate_tournament()
    if evaluation > best_evaluation:
        best_evaluation = evaluation
        best_tournament_setting = new_tournament_setting
        same_score_count = 0
    else:
        same_score_count += 1
    return best_evaluation, best_tournament_setting, same_score_count


def optimize_tournament_population(player_pool: int, team_amount: int, epoch: int = 10000, moves: int = 5,
                        population: int = 5, stop_same: int = 100):
    best_tournament_setting = [Tournament(copy.deepcopy(player_pool), team_amount) for x in range(population)]
    best_evaluation = [t.evaluate_tournament() for t in best_tournament_setting]
    same_score_count = [0 for t in best_tournament_setting]
    improvement = [[] for t in best_tournament_setting]
    for i in range(epoch):
        # Break the loop if we already have a valid score but haven't improved in a long while
        for t in range(len(best_tournament_setting)):
            if best_evaluation[t] >= 0 and same_score_count[t] >= stop_same:
                break
            impr_e, impr_t, impr_count = improve_tournament(best_tournament_setting[t], best_evaluation[t],
                                                            same_score_count[t], moves)
            best_evaluation[t] = impr_e
            best_tournament_setting[t] = impr_t
            same_score_count[t] = impr_count
            improvement[t] = np.append(improvement[t], impr_e)
        print(f"Try number {i}, best evaluation {best_evaluation}, "
              f"current tries before improvement {same_score_count}")
    return best_tournament_setting, improvement


def main():
    player_amount = 75
    team_amount = 5
    player_pool = generate_player_pool(player_amount)

    best_tournament_setting, improvement = optimize_tournament(player_pool, team_amount)

    print(best_tournament_setting)
    plt.plot(improvement)
    plt.show()

main()