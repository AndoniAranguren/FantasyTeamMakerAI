PLAYER_MINIMUM = 7
MAX_PLAYERS_IN_TEAM = 25
MAX_EXP = 5
CONSTRAIN_GENDER_RULE = 4

# IMPORTING DATA FROM CSV
IMPORT_HASHTAGS_REFS = ["#REFHR", "#REFAR", "#REFSR", "#REFSRUN"]
IMPORT_HASHTAGS_EXP = ["#EXPC", "#EXPK", "#EXPB", "#EXPS"]
IMPORT_HASHTAGS_POS = "#POS"
IMPORT_HASHTAG_GENDER = "#GENDER"
IMPORT_HASHTAG_NAME = "#NAME"

IMPORT_HASHTAGS = [IMPORT_HASHTAG_NAME] + [IMPORT_HASHTAG_GENDER] + [IMPORT_HASHTAGS_POS] + \
                  IMPORT_HASHTAGS_EXP + IMPORT_HASHTAGS_REFS

IMPORT_HASHTAG_REF_OK = "#REFOK"
IMPORT_HASHTAGS_REFS = ["#REFHR", "#REFAR", "#REFSR", "#REFSRUN"]
IMPORT_HASHTAGS_EXP_VALUES = {"#EXP1": 1,
                              "#EXP2": 2,
                              "#EXP3": 3,
                              "#EXP4": 4,
                              "#EXP5": 5}
