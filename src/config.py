PLAYER_MINIMUM = 7
MAX_PLAYERS_IN_TEAM = 25
MAX_EXP = 5
CONSTRAIN_GENDER_RULE = 3
POSITION_CONSTRAINS = [1, 2, 3, 1]      # This should have the same amount of items as IMPORT_HASHTAGS_POS_ORDER
REFEREE_CONSTRAINS = [1, 1, 1, 2, 3]    # This should have the same amount of items as IMPORT_HASHTAGS_REFS
FACTORS = [0.4, 0.4, 0.2]

# IMPORTING DATA FROM CSV
#  - COL NAMES
IMPORT_HASHTAG_NAME = "#NAME"
IMPORT_HASHTAG_GENDER = "#GENDER"
IMPORT_HASHTAGS_POS = "#POS"
IMPORT_HASHTAGS_EXP = ["#EXPS", "#EXPB", "#EXPC", "#EXPK"]
IMPORT_HASHTAGS_REFS = ["#REFCAPTAIN", "#REFHR", "#REFSRUN", "#REFSR", "#REFAR", "#REFTK"]
IMPORT_HASHTAGS_REFS = ["#REFCAPTAIN", "#REFHR", "#REFSRUN", "#REFSR", "#REFAR"]


IMPORT_HASHTAGS = [IMPORT_HASHTAG_NAME] + [IMPORT_HASHTAG_GENDER] + [IMPORT_HASHTAGS_POS] + \
                  IMPORT_HASHTAGS_EXP + IMPORT_HASHTAGS_REFS

#  - VALUES
IMPORT_HASHTAGS_POS_ORDER = ["#POSS", "#POSB", "#POSC", "#POSK"]
IMPORT_HASHTAGS_EXP_VALUES = {"#EXP1": 1,
                              "#EXP2": 2,
                              "#EXP3": 3,
                              "#EXP4": 4,
                              "#EXP5": 5}
IMPORT_HASHTAG_REF_OK = "#REFOK"