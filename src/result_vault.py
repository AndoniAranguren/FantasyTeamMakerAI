player_composition_results = {}


def compute_player_composition(player_composition_id: str, evaluation_function):
    if player_composition_id in player_composition_results:
        return player_composition_results[player_composition_id]
    else:
        player_composition_results[player_composition_id] = evaluation_function()
        return player_composition_results[player_composition_id]

#ALSO STORE TEAM SCORES