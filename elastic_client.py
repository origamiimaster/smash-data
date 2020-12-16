"""
This file contains all the functions to connect to the elasticsearch server and modify it's database
"""
from elasticsearch import Elasticsearch
import datetime

es = Elasticsearch()


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
            "sort": [
                {
                    "timestamp": {
                        "order": "desc"
                    }
                }
            ]
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
    es.indices.refresh("event-data")
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
        None:
    """
    Adds an event to the elasticsearch server
    """
    if location["lat"] is None or location["lng"] is None:
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

        # if r['result']:
        #     print(r['result'])
    es.indices.refresh("game-time-loc-data")
