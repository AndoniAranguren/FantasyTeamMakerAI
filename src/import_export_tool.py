import random

import numpy as np
import pandas as pd

from player import Player
from src import config


def cleanup_multilanguage_hashtags(df):
    # Unify all hashtags into one. This is useful when the form was done with multiple languages
    hashtag_cols = [col for col in df.columns if "#" in col]

    df_nulls = df.isnull()
    for index, row in df[hashtag_cols].iterrows():
        for required_col in config.IMPORT_HASHTAGS:
            try:
                not_empty_col = [col for col in row.keys() if not df_nulls.loc[index, col] and required_col in col][0]
                df.loc[index, required_col] = row[not_empty_col]
            except:
                df.loc[index, required_col] = None

    df = df[config.IMPORT_HASHTAGS]
    return df


def cleanup_genders(df):
    # Cleanup genders and censor them
    df[config.IMPORT_HASHTAG_GENDER] = df[config.IMPORT_HASHTAG_GENDER].str.lower()
    remove_stuff = ["(", ")", "cisgender", "cis", "  "]
    for remove in remove_stuff:
        df[config.IMPORT_HASHTAG_GENDER] = df[config.IMPORT_HASHTAG_GENDER].str.strip().replace(remove, "")

    mapping_genders = {"NB": ["non-binary", "no binary", "non binary", "no binario", "nb"],
                       "Male": ["male", "hombre", "masculino"],
                       "Female": ["female", "fem", "mujer", "femenino", "femme"]}
    inv_map = {value: k for k, v in mapping_genders.items() for value in v}

    def function_lambda(x): return inv_map.get(x) if inv_map.get(x) is not None else x

    df[config.IMPORT_HASHTAG_GENDER] = df[config.IMPORT_HASHTAG_GENDER].apply(lambda x: function_lambda(x))

    unique_genders_shuffled = df[config.IMPORT_HASHTAG_GENDER].unique()
    random.shuffle(unique_genders_shuffled)
    anonymate_genders = {gender: num for num, gender in enumerate(unique_genders_shuffled)}
    df[config.IMPORT_HASHTAG_GENDER] = df[config.IMPORT_HASHTAG_GENDER].apply(lambda x: anonymate_genders.get(x))
    return df


def cleanup_experience(df):
    def function_map(x, column_value):
        try:
            return config.IMPORT_HASHTAGS_EXP_VALUES.get(column_value) if column_value in x else x
        except TypeError as e:
            return x

    for col_exp in config.IMPORT_HASHTAGS_EXP:
        for col_value in config.IMPORT_HASHTAGS_EXP_VALUES:
            df[col_exp] = df[col_exp].apply(lambda x: function_map(x, col_value))
        df[col_exp] = df[col_exp].apply(lambda x: 0 if type(x) == str else x)

    return df


def cleanup_positions(df):
    for hashtag_pos in config.IMPORT_HASHTAGS_POS_ORDER:
        def function_map(x, hashtag_pos):
            return 1 if hashtag_pos in x else 0
        df[hashtag_pos] = df[config.IMPORT_HASHTAGS_POS].apply(lambda x: function_map(x, hashtag_pos))
    df.drop(columns=[config.IMPORT_HASHTAGS_POS], inplace=True)
    return df


def validate_referees(df):
    # Validate referee titles
    def function_map(x):
        try:
            return 1 if config.IMPORT_HASHTAG_REF_OK in x else 0
        except TypeError as e:
            return 0
    for ref_col in config.IMPORT_HASHTAGS_REFS:
        df[ref_col] = df[ref_col].apply(lambda x: function_map(x))
    return df


def cleanup_empties(df):
    return df.dropna(subset=[config.IMPORT_HASHTAG_NAME, config.IMPORT_HASHTAG_GENDER])


def read_players(csv_path):
    try:
        df = pd.read_csv(csv_path, sep=";")
    except:
        df = pd.read_csv(csv_path, sep=";", encoding="latin1")
    for required_col in config.IMPORT_HASHTAGS:
        df[required_col] = None

    df = cleanup_multilanguage_hashtags(df)
    df = cleanup_empties(df)
    df = cleanup_genders(df)
    df = cleanup_experience(df)
    df = cleanup_positions(df)
    df = validate_referees(df)
    df = df.sort_values(by=config.IMPORT_HASHTAGS_REFS, ascending=False)

    player_pool = []
    for index, row in df.iterrows():
        player = Player(index,
                        row[config.IMPORT_HASHTAG_NAME],
                        str(row[config.IMPORT_HASHTAG_GENDER]),
                        row[config.IMPORT_HASHTAGS_REFS],
                        row[config.IMPORT_HASHTAGS_POS_ORDER].values,
                        np.average(row[config.IMPORT_HASHTAGS_EXP]))
        player_pool += [player]

    return player_pool, df
