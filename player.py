import numpy as np


class Player:

    def __init__(self, name: str, gender: str, referee_titles: [int], experience: int) -> object:
        self.name = name
        self.gender = gender
        self.referee_titles = np.array(referee_titles)
        self.experience = experience
        self.team = None
