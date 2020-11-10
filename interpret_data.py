"""
Gets data from elasticsearch server, and processes it for viewing and interpretation
"""

from elasticsearch import Elasticsearch
import plotly.graph_objects as go
es = Elasticsearch()


def start_scroll() -> list:
    """
    Uses elasticsearch scroll API to get all the games from the server.
    """
    body = es.search(
        index="game-data",
        scroll="30s",
        size=100,
        body={
            "query": {
                "match_all": {}
            }
        }
    )
    results = []
    while len(results) < body["hits"]["total"]["value"]:
        for hit in body["hits"]["hits"]:
            results.append(hit)
        body = es.scroll(
            scroll_id=body["_scroll_id"],
            scroll="30s"
        )
    return results


def graph_win_vs_play_rate(data) -> None:
    """
    Calculates play rates and win rates, and graphs with plotly.
    """
    char_w_l = {}
    for game in data:
        key = game["_source"]["winner_char"]
        if key not in char_w_l:
            char_w_l[key] = [0, 0]
        key2 = game["_source"]["loser_char"]
        if key2 not in char_w_l:
            char_w_l[key2] = [0, 0]
        char_w_l[key][0] += 1
        char_w_l[key2][1] += 1

    percents = [(k, char_w_l[k][0] / (char_w_l[k][0] + char_w_l[k][1]))
                for k in char_w_l]
    totals = [(k, (char_w_l[k][0] + char_w_l[k][1])) for k in char_w_l]
    x = []
    y = []
    text = []
    for val in percents:
        x.append(val[1])
        text.append(val[0])
    for val in totals:
        y.append(val[1])

    fig = go.Figure()

    fig.add_trace(go.Scatter(x=x, y=y, text=text, mode="markers+text"))

    fig.show()


def get_chars_match_up(data: list) -> dict:
    """
    Gets the relevant match ups for a given character
    """
    match_up = {}
    for game in data:
        win_char = game["_source"]["winner_char"]
        lose_char = game["_source"]["loser_char"]
        if win_char not in match_up:
            match_up[win_char] = {}
        if lose_char not in match_up[win_char]:
            match_up[win_char][lose_char] = [0, 0]
        if lose_char not in match_up:
            match_up[lose_char] = {}
        if win_char not in match_up[lose_char]:
            match_up[lose_char][win_char] = [0, 0]
        match_up[win_char][lose_char][0] += 1
        match_up[lose_char][win_char][1] += 1

    for key1 in match_up:
        for key2 in match_up[key1]:
            percent = match_up[key1][key2][0] / (match_up[key1][key2][0] + match_up[key1][key2][1])
            match_up[key1][key2] = int(percent*100) / 100
    for key in match_up:
        match_up[key] = {k: v for k, v in sorted(match_up[key].items(), key=lambda item: item[1])}
    return {k: v for k, v in sorted(match_up.items())}


def get_relative_stage_values(data) -> dict:
    """
    Gets the data for each different stage.
    """
    stages = set()
    for game in data:
        stages.add(game['_source']["stage_name"])
    data2 = {}
    for stage in stages:
        if stage != "":
            data2[stage] = [a for a in data if a["_source"]["stage_name"] == stage]
    return data2


def get_best_stage(char, data) -> str:
    """
    Returns the stage that character has the highest win rate for.
    """
    legal_stages = {"Battlefield", "Final Destination", "Pokémon Stadium 2", "Smashville",
                    "Town and City", "Yoshi's Story", "Yoshi's Island", "Kalos Pokémon League",
                    "Lylat Cruise"}
    stage_data = get_relative_stage_values(data)
    new_data = {}
    for stage in stage_data:
        temp_data = stage_data[stage]
        char_info = get_chars_match_up(temp_data)
        if char in char_info:
            new_data[stage] = char_info[char]
    maximum = ("", 0)
    for thing in new_data:
        total_win_percents = sum([new_data[thing][key] for key in new_data[thing]])
        total_numbers = len([a for a in new_data[thing]])
        average = total_win_percents / total_numbers
        if thing in legal_stages and total_numbers > 50 and average > maximum[1]:
            maximum = (thing, average)
    return maximum[0]


if __name__ == "__main__":
    my_data = start_scroll()
    graph_win_vs_play_rate(my_data)