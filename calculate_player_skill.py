"""
Goes through and calculates player win percentages by averages, for a measure of player "skill"
"""
import datetime


def get_player_ids_and_names(data):
    player_ids_and_names = set()
    for game in data:
        id1 = game["_source"]['winner_id']
        name1 = game["_source"]['winner_name']
        id2 = game["_source"]['loser_id']
        name2 = game["_source"]['loser_name']
        player_ids_and_names.add((id1, name1))
        player_ids_and_names.add((id2, name2))
    return player_ids_and_names


def get_player_win_percentage_and_games(data):
    winners = [game["_source"]["winner_id"] for game in data]
    losers = [game["_source"]["loser_id"] for game in data]
    print(len(winners))
    print(len(losers))
    player_ids_and_names = get_player_ids_and_names(data)
    results = {}
    for id, _ in player_ids_and_names:
        print(datetime.datetime.now())
        results[id] = {
            "win_percentage": winners.count(id) / (winners.count(id) + losers.count(id)),
            "games_played": winners.count(id)+losers.count(id),
            # "sequence_of_games": []
        }
    return results

def get_player_game_history(data):
    player_ids_and_names = get_player_ids_and_names(data)
    output = {}
    for id, _ in player_ids_and_names:
        output[id] = []
    for game in data:
        output[game["_source"]["winner_id"]].append(1)
        output[game["_source"]["loser_id"]].append(0)
    return output

def calculate_weighted_average(data):
    wins_and_games = get_player_win_percentage_and_games(data)
    for id in wins_and_games:
        win_percentage = wins_and_games[id]["win_percentage"]
        games_played = wins_and_games[id]["games_played"]
        # wins_and_games[id]["weighted_average"]

if __name__ == "__main__":
    import interpret_data
    my_data = interpret_data.start_scroll()
    # ids_and_names = get_player_ids_and_names(my_data)
    # print(ids_and_names)
    # results = get_player_win_percentage(my_data)
    # print(results)

    # BETTER WAY
    # winner_list = [game["_source"]["winner_id"] for game in my_data]
    # loser_list = [game["_source"]["loser_id"] for game in data]
    # loser_dict = {}
    # for loser in loser_list:
    #     if loser not in loser_dict:
    #         loser_dict[loser] = 0
    #     loser_dict[loser] += 1
    # winner_dict = {}
    # for winner in winner_list:
    #     if winner not in winner_dict:
    #         winner_dict[winner] = 0
    #     winner_dict[winner] += 1
    # player_skill_dict = {}
    # for id, _ in get_player_ids_and_names(my_data):
    #     if id not in winner_dict:
    #         wins = 0
    #     else:
    #         wins = winner_dict[id]
    #     if id not in loser_dict:
    #         losses = 0
    #     else:
    #         losses = loser_dict[id]
    #     player_skill_dict[id] = (wins / (wins + losses))
    #
    # for game in my_data:
    #     game["_source"]["winner_skill"] = player_skill_dict[game["_source"]["winner_id"]]
    #     game["_source"]["loser_skill"] = player_skill_dict[game["_source"]["loser_id"]]
