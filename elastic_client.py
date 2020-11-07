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
    # try:
    return int(datetime.datetime.fromtimestamp(r["hits"]["hits"][0]["_source"]["timestamp"]/1000).timestamp())
    # except:
    # return None


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
        print(res["result"])
