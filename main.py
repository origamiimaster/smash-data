"""
Contains the functions for getting tournaments and games, and then does it for all games
"""
from download import SmashGGClient
import elastic_client
import datetime
import formatter
import time
import json


def fetch_tournaments(client: SmashGGClient, last_time: int, api_key="690ea7f74c5f9b331c7148ba0a7a34e3") -> None:
    """
    Adds all tournament events to the elasticsearch client
    """
    # my_client = SmashGGClient(api_key)
    # client.api = api_key
    original_start = int(datetime.datetime(2018, 12, 1).timestamp())
    while True:
        start_timestamp = elastic_client.get_last_timestamp()
        if start_timestamp is None:
            start_timestamp = original_start
        else:
            start_timestamp += 100

        tournaments = client.get_tournaments(start_timestamp, last_time)
        if tournaments is None:
            break

        events_data = formatter.get_events_data(tournaments, 1386)
        elastic_client.upload_event_data(events_data)

        start_timestamp = tournaments[-1]['startAt']

        date = datetime.date.fromtimestamp(start_timestamp)
        print(date)
        time.sleep(1)


def fetch_events(client: SmashGGClient, api_key="690ea7f74c5f9b331c7148ba0a7a34e3") -> None:
    """
    Processes each event and then adds all games to elasticsearch
    """
    # client.api = api_key
    with open('characters.json') as f:
        char_data = {}
        for char in json.load(f)["entities"]["character"]:
            char_data[char["id"]] = char["name"]
    tourney_id, event_id, event_timestamp = elastic_client.get_unfinished_event()

    while event_id is not None:
        sets = []
        page = 1
        actual_sets = []
        print(event_id)
        while True:
            loc, sets_to_add = client.get_sets(event_id, page)
            if not sets_to_add:
                break
            for cur_set in sets_to_add:
                if not cur_set['hasPlaceholder']:
                    actual_sets.append(cur_set)
                    if cur_set["games"]:
                        sets.append(cur_set)
            page += 1
            # time.sleep(1)
        games = formatter.get_games(sets)
        games_data = formatter.extract_games_data(games, char_data)

        if not len(games_data) <= 0:
            elastic_client.add_games_to_elastic(tourney_id, event_id, event_timestamp, games_data, loc)

        sets_succesfully_added = elastic_client.add_sets_to_elastic(actual_sets, event_id, tourney_id, event_timestamp)
        elastic_client.mark_as_done(event_id)
        print("Recorded " + str(len(games_data)) + " games")
        print("Recorded " + str(sets_succesfully_added) + " sets")
        tourney_id, event_id, event_timestamp = elastic_client.get_unfinished_event()
        time.sleep(1)


if __name__ == "__main__":
    my_client = SmashGGClient("690ea7f74c5f9b331c7148ba0a7a34e3", "baeb4acfe9b8dabf103931a5e46463e3")
    fetch_tournaments(my_client, int(time.time()))
    fetch_events(my_client)
