"""
This file contains all the functions to connect to the elasticsearch server and modify it's database
"""
from elasticsearch import Elasticsearch
import datetime

es = Elasticsearch()


def get_unfinished_event_count() -> int:
    """Determines how many unprocessed events remain"""
    r = es.search(
        index="event-data",
        scroll="30s",
        size=1,
        body={"query": {
            "match": {
                "done": False
            }
        },
        }
    )
    es.clear_scroll(scroll_id=r["_scroll_id"])
    return int(r["hits"]["total"]["value"])


def get_last_timestamp() -> int or None:
    """
    Returns the most recent event timestamp from the elasticsearch server
    """
    r = es.search(
        index="event-data",
        body={
            "query": {
                "match_all": {}
            },
            "size": 1,
            # "sort": [
            #     {
            #         "timestamp": {
            #             "order": "desc"
            #         }
            #     }
            # ]
        }
    )
    try:
        return int(datetime.datetime.fromtimestamp(
            r["hits"]["hits"][0]["_source"]["timestamp"] / 1000).timestamp())
    except KeyError:
        return None


def upload_event_data(event_data) -> None:
    """
    Adds an event to the elasticsearch server
    """
    for data in event_data:
        es.index(
            index="event-data",
            id=data[2],
            body={
                "tournament_id": data[0],
                "tournament_name": data[1],
                "event_id": data[2],
                "event_name": data[3],
                "timestamp": data[4] * 1000,
                "done": False
            },
        )


def get_unfinished_event() -> (int, int):
    """
    Gets the most recent event that is not yet processed, returning it's ID and it's tournament ID
    """
    es.indices.refresh(index="event-data")
    r = es.search(
        index="event-data",
        body={
            "query": {
                "match": {
                    "done": False
                }
            },
            "size": 1,
            "sort": [
                {
                    "timestamp": {
                        "order": "desc"
                    }
                }
            ]
        }
    )["hits"]["hits"][0]
    # print(r)
    return r["_source"]["tournament_id"], r["_source"]["event_id"], r["_source"]["timestamp"]


def mark_as_done(event_id: int) -> None:
    """
    Marks the given event as done in the elasticsearch server, effectively removing it from the
    queue
    """
    es.update(
        index="event-data",
        id=event_id,
        body={
            "doc": {
                "done": True
            }
        }
    )


def mark_all_as_not_done() -> None:
    """
    Sets all events in the elasticsearch server to be unprocessed
    """
    es.update_by_query(
        index="event-data",
        body={
            "query": {
                "match_all": {}
            },
            "script": "ctx._source.done = false"
        }
    )


def add_games_to_elastic(tournament_id: int, event_id: int, event_timestamp, games_data: [object], location: dict) -> \
        tuple:
    """
    Adds an event to the elasticsearch server
    """
    total_updated = 0
    total_created = 0
    if location is None or location["lat"] is None or location["lng"] is None:
        location = None
    for data in games_data:
        r = es.index(
            index="game-time-loc-data",
            id=data["game_id"],
            body={
                "tournament_id": tournament_id,
                "event_id": event_id,
                "set_id": data['set_id'],
                "game_number": data['game_number'],
                "stage_name": data['stage_name'],
                "winner_id": data['winner_id'],
                "loser_id": data['loser_id'],
                "winner_name": data['winner_name'],
                "loser_name": data['loser_name'],
                "winner_char": data['winner_char'],
                "loser_char": data['loser_char'],
                "game_id": data["game_id"],
                "timestamp": event_timestamp,
                "location": str(location["lat"]) + "," + str(location["lng"]) if location is not None else None
            }
        )
        # total += 1
        if r['result'] == 'updated':
            total_updated += 1
        elif r['result'] == 'created':
            total_created += 1
        # print(r['result'])
        # if r['result']:
        #     print(r['result'])
    es.indices.refresh(index="game-time-loc-data")
    return (total_created, total_updated)


def add_sets_to_elastic(sets_to_add, event_id, tournament_id, event_timestamp):
    total_updated = 0
    total_created = 0
    # print("thing y = ")
    # print(sets_to_add)
    # sets = sets
    for game_set in sets_to_add:
        if not game_set["hasPlaceholder"]:
            try:
                if "preview" in str(game_set['id']):
                    print("preview game")
                    continue
                if game_set['displayScore'] is None:
                    continue

                ids = [game_set["slots"][0]["entrant"]["id"], game_set["slots"][1]["entrant"]["id"]]
                winner_id = game_set['winnerId']
                loser_id = ids[0] if game_set["winnerId"] == ids[1] else ids[1]
                if game_set["slots"] is None or game_set["slots"][0]["entrant"] is None:
                    continue
                if "participants" not in game_set["slots"][0]["entrant"] or \
                        game_set["slots"][0]["entrant"]["participants"] is None:
                    print("something went wrong")
                    # print(game_set)
                    continue

                if game_set["slots"][0]["entrant"]["participants"][0]["user"] is None:
                    user_id_0 = None
                    user_slug_0 = None
                else:
                    user_id_0 = game_set["slots"][0]["entrant"]["participants"][0]["user"]["id"]
                    user_slug_0 = game_set["slots"][0]["entrant"]["participants"][0]["user"]["slug"]
                if game_set["slots"][0]["entrant"]["participants"][0]["user"] is None:
                    user_id_1 = None
                    user_slug_1 = None
                else:
                    user_id_1 = game_set["slots"][0]["entrant"]["participants"][0]["user"]["id"]
                    user_slug_1 = game_set["slots"][0]["entrant"]["participants"][0]["user"]["slug"]

                user_ids = {game_set["slots"][0]["entrant"]["id"]: (user_id_0, user_slug_0),
                            game_set["slots"][1]["entrant"]["id"]: (user_id_1, user_slug_1),
                            None: None}
                winner_user_id = user_ids[winner_id][0]
                winner_slug = user_ids[winner_id][1]
                loser_user_id = user_ids[loser_id][0]
                loser_slug = user_ids[loser_id][1]
                full_text = game_set["displayScore"]
                if full_text == "DQ" or full_text is None:
                    continue
                score_1 = full_text[full_text.index(" - ") - 1: full_text.index(" - ")]
                score_2 = full_text[-1]
                scores = {game_set['slots'][0]['entrant']['id']: score_1,
                          game_set['slots'][1]['entrant']['id']: score_2}
                # slugs = {game_set['slots'][0]['entrant']['id']: score_1,
                #          game_set['slots'][1]['entrant']['id']: score_2}
                winner_score = scores[winner_id]
                loser_score = scores[loser_id]

                # print(winner_score)
                # print(loser_score)
                r = es.index(
                    index="set-data",
                    id=game_set["id"],
                    body={
                        "tournament_id": tournament_id,
                        "event_id": event_id,
                        "set_id": game_set['id'],
                        "game_ids": [game["id"] for game in game_set["games"]] if game_set["games"] is not None else
                        None,
                        "winner_id": winner_id,
                        "loser_id": loser_id,
                        "round_text": game_set['fullRoundText'],
                        "timestamp": event_timestamp,
                        "winner_score": winner_score,
                        "loser_score": loser_score,
                        "winner_user_id": winner_user_id,
                        "loser_user_id": loser_user_id,
                        "winner_slug":  winner_slug,
                        "loser_slug": loser_slug
                        # "game_number": data['game_number'],
                        # "stage_name": data['stage_name'],
                        # "winner_id": data['winner_id'],
                        # "loser_id": data['loser_id'],
                        # "winner_name": data['winner_name'],
                        # "loser_name": data['loser_name'],
                        # "winner_char": data['winner_char'],
                        # "loser_char": data['loser_char'],
                        # "game_id": data["game_id"],
                        # "location":str(location["lat"]) + "," + str(location["lng"]) if location is not None else None
                    }
                )
                # total += 1
                if r['result'] == 'updated':
                    total_updated += 1
                elif r['result'] == 'created':
                    total_created += 1
            # except IndexError as e:
            #     print(e)
            #     continue
            # except TypeError:
            #     print(game_set)
            except (ValueError, AttributeError, TypeError, IndexError) as e:
                print(e)
                continue
    return (total_created, total_updated)


def get_set_by_set_id(set_id):
    r = es.search(
        index="set-data",
        scroll="30s",
        size=1,
        body={"query": {
            "match": {
                "set_id": set_id
            }
        },
        }
    )
    try:
        es.clear_scroll(scroll_id=r["_scroll_id"])
        return r["hits"]["hits"][0]
    except IndexError:
        return None


def get_event_by_event_id(event_id):
    r = es.search(
        index="event-data",
        scroll="30s",
        size=1,
        body={"query": {
            "match": {
                "event_id": event_id
            }
        },
        }
    )
    try:
        es.clear_scroll(scroll_id=r["_scroll_id"])
        return r["hits"]["hits"][0]
    except IndexError:
        return None
