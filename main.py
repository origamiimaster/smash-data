from download import SmashGGConnectionTHINGY
from elastic_client import getLastTimestamp, uploadEventData
import datetime
import formatter
import time
def fetch_tournaments(client, last_time):
    originalStart = int(datetime.datetime(
        2018, 12, 1).timestamp())
    while 1 == 1:
        start_timestamp = getLastTimestamp()
        if start_timestamp is None:
            start_timestamp = originalStart
        else: 
            start_timestamp += 100
        date = datetime.date.fromtimestamp(start_timestamp)
        tournaments = client.get_tournaments(start_timestamp, last_time)
        if tournaments is None:
            break

        events_data = formatter.get_events_data(tournaments, 1386)
        uploadEventData(events_data)

        start_timestamp = tournaments[-1]['startAt']

        date = datetime.date.fromtimestamp(start_timestamp)
        print(date)
        time.sleep(1)


client = SmashGGConnectionTHINGY("690ea7f74c5f9b331c7148ba0a7a34e3")
print(fetch_tournaments(client, 1548009000))
