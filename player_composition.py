import itertools

player_composition_results = {}


class PlayerComposition:
    def __init__(self, player_list, position_requisites):
        player_ids = [player.player_id for player in player_list]
        player_ids.sort()
        self.player_composition_id = ",".join([str(x) for x in player_ids])
        self.player_list = player_list
        self.position_requisites = position_requisites
        self.gender_count = []
        self.team_subcompositions = []

        self.count_genders()
        self.count_team_subcompositions()

    def count_genders(self):
        unique_genders = set([x.gender for x in self.player_list])
        self.gender_count = [[x.gender for x in self.player_list].count(gender) for gender in unique_genders]

    def constrains_genders(self):
        for gender_count in self.gender_count:
            if gender_count > 4:
                return False
        return True

    def count_team_subcompositions(self):
        """Utility players can make multiple player compositions from the same set of players"""
        unique_pos = len(self.player_list[0].positions) # len = 4 keeper, chaser, beater, seeker
        player_per_positions = [[p for p in self.player_list if p.positions[pos]] for pos in range(unique_pos)]
        seeker = list(itertools.combinations(player_per_positions[0], self.position_requisites[0]))
        beater = list(itertools.combinations(player_per_positions[1], self.position_requisites[1]))
        chaser = list(itertools.combinations(player_per_positions[2], self.position_requisites[2]))
        keeper = list(itertools.combinations(player_per_positions[3], self.position_requisites[3]))
        team_subcomp = [[s, b, c, k] for s in seeker for b in beater for c in chaser for k in keeper]

        # Flatten array:
        team_subcomp = [[item for sub_list in list_2D for item in sub_list] for list_2D in team_subcomp]

        # Remove those with duplicates
        if team_subcomp:
            before_len = len(team_subcomp)
            team_subcomp = [team_comp for team_comp in team_subcomp if len(team_comp) == len(set(team_comp))]
            after_len = len(self.team_subcompositions)
        self.team_subcompositions = team_subcomp

    def amount_subcompositions(self):
        if self.team_subcompositions:
            return len(self.team_subcompositions)
        else:
            return -1

    def evaluate(self):
        if self.constrains_genders():
            return self.amount_subcompositions()
        else:
            return -2


def compute_player_composition(player_composition: PlayerComposition):
    if player_composition.player_composition_id in player_composition_results:
        return player_composition_results[player_composition.player_composition_id]
    else:
        result = player_composition.evaluate()
        player_composition_results[player_composition.player_composition_id] = result
        return result