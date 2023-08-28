import json

import import_export_tool
from main import initialize_execution


def main():
    folder_path = "../data/tmp/70862037e28593d282e726406c6956ae/e05102da63fed012e7c20ff817f7f8ea"
    with open(f"{folder_path}/config.json", "r") as f:
        config_params = json.load(f)["config_params"]
    player_pool, df = import_export_tool.read_players(config_params["file_path"])

    analysis, league_list, from_saved = initialize_execution(player_pool, config_params["team_amount"],
                                                             config_params["leagues_movement"],
                                                             config_params["clubs_per_league"],
                                                             folder_path)
    fig, ax = analysis.plot_analysis()
    fig1, fig2 = analysis.plot_analysis_club()
    fig.savefig(folder_path + "/Analysis-tournament_league_info.png")
    fig1.savefig(folder_path + "/Analysis-tournament_league.png")
    fig2.savefig(folder_path + "/Analysis-tournament_league_top.png")
    best_tournament_setting = league_list[0][0][0]
    result = best_tournament_setting.__str__()
    with open(folder_path + "/Analysis-tournament_league_info.txt",
              "w", encoding="utf-8-sig") as text_file:
        text_file.write(result)


if __name__ == "__main__":
    main()
