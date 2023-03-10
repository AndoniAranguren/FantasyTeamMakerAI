import numpy as np


class Player:

    def __init__(self, player_id, name: str, gender: str, referee_titles: [int],
                 positions: [int], experience: int) -> object:
        self.player_id = player_id
        self.name = name
        self.gender = gender
        self.referee_titles = np.array(referee_titles)
        self.positions = np.array(positions)
        self.experience = experience
