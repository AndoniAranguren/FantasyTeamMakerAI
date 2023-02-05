import copy

import random as rnd
from player import Player
from tournament import Tournament


def generate_player_pool(player_amount):
    hr = [1, 1, 1, 1]
    ar = [0, 1, 1, 1]
    sr = [0, 0, 1, 1]
    sc = [0, 0, 0, 1]
    nn = [0, 0, 0, 0]
    names = ["Joey", "Aurelio", "Evan", "Donny", "Foster", "Dwayne", "Grady", "Quinton", "Darin", "Mickey", "Hank",
             "Kim", "Peter", "Jeremy", "Jess", "Jimmie", "Vern", "Pasquale", "Romeo", "Chris", "Dale", "Beau", "Cliff",
             "Timothy", "Raphael", "Brain", "Mauro", "Luke", "Myron", "Omar", "Reynaldo", "Major", "Clinton", "Nolan",
             "Raymond", "Lucien", "Carey", "Winfred", "Dan", "Abel", "Elliott", "Brent", "Chuck", "Dirk", "Tod",
             "Emerson", "Dewey", "Scot", "Enrique", "Al", "Beatrice", "Brandy", "Kathy", "Jane", "Marcy", "Shelly",
             "Lucy", "Cathy", "Joanna", "Doris", "Lindsay", "Staci", "Shelia", "Rosanne", "Rebecca", "Luz", "Flora",
             "Rosalie", "Karla", "Phoebe", "Meagan", "Virginia", "Amanda", "Katy", "Karla", "Deanne", "Pearl",
             "Christi", "Victoria", "Ola", "Alexandra", "Marina", "Lorraine", "Sybil", "Adeline", "Taylor", "Anita",
             "Aurora", "Neva", "Alisha", "Maria", "Erna", "Gwendolyn", "Brenda", "Bethany", "Sybil", "Earline", "June",
             "Brandy", "Sue", "Jose", "María", "Jaime"]
    genders = ["M", "M", "M", "M", "F", "F", "F", "F", "NB", "NB"]
    referees = [hr, ar, ar, sr, sr, sc, sc, sc, nn, nn, nn]
    max_experiencia = 5

    player_pool = []
    for i in range(player_amount):
        player_pool += [Player(names[rnd.randint(0, len(names)-1)],
                               genders[rnd.randint(0, len(genders)-1)],
                               referees[rnd.randint(0, len(referees)-1)],
                               rnd.randint(0, max_experiencia))]
    return player_pool


def main():
    player_amount = 120
    team_amount = 8
    player_pool = generate_player_pool(player_amount)
    best_tournament_setting = Tournament(player_pool, team_amount)
    best_evaluation = best_tournament_setting.evaluate_tournament()
    epoch = 1000
    moves = 5
    for i in range(epoch):
        new_tournament_setting = copy.deepcopy(best_tournament_setting)
        for m in range(moves):
            new_tournament_setting.perform_move()
        evaluation = new_tournament_setting.evaluate_tournament()
        if evaluation > best_evaluation:
            best_evaluation = evaluation
            best_tournament_setting = new_tournament_setting
    return best_tournament_setting

print(main())
