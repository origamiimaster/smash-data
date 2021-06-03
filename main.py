"""
Contains the functions for getting tournaments and games, and then does it for all games
"""
from download import SmashGGClient
import elastic_client
import datetime
import formatter
import time
import json
from loading import Timer


def fetch_tournaments(client: SmashGGClient, last_time: int, api_key="690ea7f74c5f9b331c7148ba0a7a34e3") -> None:
    """
    Adds all tournament events to the elasticsearch client
    """
    my_timer = Timer()
    my_timer.total_event = 1
    original_start = int(datetime.datetime(2018, 12, 1).timestamp())
    while True:
        print("Average Time: " + str(my_timer.get_avg()))
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
        # time.sleep(1)
        my_timer.update()


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
    total_to_be_added = elastic_client.get_unfinished_event_count()
    my_timer = Timer()
    my_timer.total_event = 1
    while event_id is not None:
        print("Average: " + str(my_timer.get_avg()))
        print("ETA: " + str(my_timer.predict(total_to_be_added)))
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
            time.sleep(0.5)
        games = formatter.get_games(sets)
        games_data = formatter.extract_games_data(games, char_data)

        if not len(games_data) <= 0:
            (games_created, games_updated) = elastic_client.add_games_to_elastic(tourney_id,
                                                                                 event_id,
                                                                                 event_timestamp,
                                                                                 games_data,
                                                                                 loc)
        else:
            (games_created, games_updated) = (0, 0)
        (sets_created, sets_updated) = elastic_client.add_sets_to_elastic(actual_sets, event_id, tourney_id,
                                                                          event_timestamp)
        elastic_client.mark_as_done(event_id)
        print("Created " + str(games_created) + " games, updated " + str(games_updated))
        print("Created " + str(sets_created) + " sets, updated " + str(sets_updated))
        tourney_id, event_id, event_timestamp = elastic_client.get_unfinished_event()
        # time.sleep(10)
        my_timer.update()


def update_set_info(client: SmashGGClient, set_id):
    """Fixes old set info:"""
    existing_set = elastic_client.get_set_by_set_id(set_id)["_source"]
    if 'loser_user_id' not in existing_set.keys():
        loc, sets_to_add = client.get_sets(event_id=existing_set['event_id'])
        added, updated = elastic_client.add_sets_to_elastic(sets_to_add, existing_set["event_id"], existing_set[
            'tournament_id'],
                                           existing_set['timestamp'])
        print("updated " + str(updated))
    else:
        # print("skipped")
        pass


if __name__ == "__main__":
    my_client = SmashGGClient("690ea7f74c5f9b331c7148ba0a7a34e3", "baeb4acfe9b8dabf103931a5e46463e3",
                              "3371d61c8013075a7e6be7677baad497")
    # fetch_tournaments(my_client, int(time.time()))
    # fetch_events(my_client)
    from interpret_data import set_scroll
    from loading import LoadingBar
    my_sets = set_scroll()
    print(len(my_sets))
    my_bar = LoadingBar(len(my_sets))
    for my_set in my_sets:
        my_bar.print()
        my_bar.increment()
        set_id = my_set['_id']
        # print(set_id)
        update_set_info(my_client, set_id)
