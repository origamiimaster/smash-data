from elasticsearch import Elasticsearch
import datetime
es = Elasticsearch()


def getLastTimestamp():
    r = es.search(
        index="smash-dates-with-loc",
        body={
            "query": {
                "match_all": {}
            },
            "size": 1,
            "sort": [
                {
                    "date": {
                        "order": "desc"
                    }
                }
            ]
        }
    )
    return int(datetime.datetime.strptime(r["hits"]["hits"][0]["_source"]["date"],"%Y-%m-%dT%H:%M:%S.%fZ").timestamp())