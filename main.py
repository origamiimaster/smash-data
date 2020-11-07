from download import SmashGGConnectionTHINGY
from elastic_client import getLastTimestamp
import datetime
import formatter

def fetch_tournaments(client, last_time):
    originalStart = int(datetime.datetime(
        2018, 12, 1).timestamp())  # The release of SSBU

    while 1 == 1:
        start_timestamp = getLastTimestamp()
        if start_timestamp is None:
            start_timestamp = default_start_timestamp - 100
        tournaments = client.get_tournaments(start_timestamp, last_time)
        if tournaments is None:
            break
        
        events_data = formatter.get_events_data(tournaments,1386)
        return events_data

