from elasticsearch import Elasticsearch
import datetime
es = Elasticsearch()


def getLastTimestamp():
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
        return int(datetime.datetime.fromtimestamp(r["hits"]["hits"][0]["_source"]["timestamp"]/1000).timestamp())
    except:
        return None


def uploadEventData(event_data):

    for data in event_data:
        # try:
        res = es.index(
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


def getUnfinishedEvent():
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
    )
    return r["hits"]["hits"][0]["_source"]["tournament_id"], r["hits"]["hits"][0]["_source"]["event_id"]


def markAsDone(eventId):
    r = es.update(
        index="event-data",
        id=eventId,
        body={
            "doc": {
                "done": True
            }
        }
    )
def markAllAsNotDone():
    r = es.update_by_query(
        index = "event-data",
        body = {
            "query": {
                "match_all":{}
            },
            "script":"ctx._source.done = false"
        }
    )
    print(r)

def addGamesToElastic(tournament_id, event_id, games_data):
    for data in games_data:
        r = es.index(
            index="game-data",
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
                "game_id": data["game_id"]
            }
        )
        # print(r["result"])
