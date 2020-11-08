from download import SmashGGConnectionTHINGY
# from elastic_client import getLastTimestamp, uploadEventData
import elastic_client
import datetime
import formatter
import time
import json


def fetch_tournaments(client, last_time):
    originalStart = int(datetime.datetime(
        2018, 12, 1).timestamp())
    while 1 == 1:
        start_timestamp = elastic_client.getLastTimestamp()
        if start_timestamp is None:
            start_timestamp = originalStart
        else:
            start_timestamp += 100
        date = datetime.date.fromtimestamp(start_timestamp)
        tournaments = client.get_tournaments(start_timestamp, last_time)
        if tournaments is None:
            break

        events_data = formatter.get_events_data(tournaments, 1386)
        elastic_client.uploadEventData(events_data)

        start_timestamp = tournaments[-1]['startAt']

        date = datetime.date.fromtimestamp(start_timestamp)
        print(date)
        time.sleep(1)


def fetchEvents(client):
    with open('characters.json') as f:
        charData = {}
        for char in json.load(f)["entities"]["character"]:
            charData[char["id"]] = char["name"]
    tourneyID, eventID = elastic_client.getUnfinishedEvent()

    while not eventID is None:
        sets = []
        page = 1
        while 1 == 1:
            setsToAdd = client.get_sets(eventID, page)
            if not setsToAdd:
                break
            for curSet in setsToAdd:
                if curSet["games"]:
                    sets.append(curSet)
            page += 1
            time.sleep(1)
        games = formatter.get_games(sets)
        games_data = formatter.extract_games_data(games, charData)

        if not len(games_data) <= 0:
            elastic_client.addGamesToElastic(tourneyID, eventID, games_data)
        
        print("Recorded "+str(len(games_data))+" games")
        elastic_client.markAsDone(eventID)

        tourneyID, eventID = elastic_client.getUnfinishedEvent()
        time.sleep(1)

client = SmashGGConnectionTHINGY("Insert your token")
# fetch_tournaments(client, int(time.time()))
fetchEvents(client)
