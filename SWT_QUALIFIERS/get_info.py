"""Gets the info from the smash world tour qualifiers
"""
import requests

from download import SmashGGClient


def get_tourney_events_req(slug):
    r = requests.post(
        "https://api.smash.gg/gql/alpha",
        data={
            "query": """
                    query TournamentQuery($slug: String) {
                      tournament(slug: $slug) {
                        id
                        name
                        events {
                            id
                            name
                        }
                      }
                    }
                """,
            "variables": f'{{"slug": "{slug}" }}',
        },
        headers={
            'Authorization': f'Bearer {"690ea7f74c5f9b331c7148ba0a7a34e3"}',
        }
    )
    return r.json()


qualifier_slugs = {"swt-na-northeast-ultimate-online-qualifier",
                   "swt-na-southeast-ultimate-online-qualifier",
                   "swt-na-northwest-ultimate-online-qualifier",
                   "swt-na-southwest-ultimate-online-qualifier",
                   "swt-east-asia-south-online-qualifier",
                   "swt-japan-ultimate-online-qualifier",
                   "swt-europe-ultimate-online-qualifier",
                   "swt-south-america-ultimate-online-qualifier",
                   "swt-central-america-south-ultimate-online-qualifier",
                   "swt-oceania-ultimate-online-qualifier",
                   "swt-mexico-ultimate-online-qualifier"}
qualifier_events = {}

event_list = []
for slug in qualifier_slugs:
    qualifier_events[slug] = {}
    res = get_tourney_events_req(slug)['data']
    print(res)
    for event in res['tournament']['events']:
        print(event)
        qualifier_events[slug][event['id']] = event['name']
        event_list.append(event['id'])

from info_type.single_elim import get_entrant_elo_from_event
elo = {}
for event_id in event_list:
    print(event_id)
    get_entrant_elo_from_event(elo, event_id)
