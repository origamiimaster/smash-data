"""
Get games from a tournament and calculate elo scores for each participant?
"""
import time
from elo import rate_1vs1
import requests

event_id = 553068  # NA Southwest ultimate qualifiers online
phase_id = 908846
phase_group_id = 1449589
api_keys = ["690ea7f74c5f9b331c7148ba0a7a34e3", "baeb4acfe9b8dabf103931a5e46463e3",
            "3371d61c8013075a7e6be7677baad497"]
api_counter = 0


def get_api_key():
    global api_counter
    api_counter += 1
    if api_counter > len(api_keys) - 1:
        api_counter = 0
    return api_keys[api_counter]


def get_set_info(set_id):
    query = f"""
    query SetInfo{{
        set(id: {set_id}){{
            winnerId
            id
            event{{
                name
            }}
            slots{{
                entrant{{
                    id
                    participants{{
                        user{{
                            slug
                        }}
                    }}
                }}
            }}
        }}
    }}
    """
    r = requests.post(
        "https://api.smash.gg/gql/alpha",
        data={
            "query": query,
            "variables": f'{{}}',
        },
        headers={
            'Authorization': f'Bearer {get_api_key()}',
        }
    )
    r = r.json()
    # r['data']
    winner_entrant_id = r['data']['set']['winnerId']
    loser_entrant_id = r['data']['set']['slots'][0]['entrant']['id'] if winner_entrant_id == \
                                                                        r['data']['set']['slots'][1][
                                                                            'entrant']['id'] \
        else r['data']['set']['slots'][1]['entrant']['id']
    # print(r)
    participant_ids = {r['data']['set']['slots'][0]['entrant']['id']: r['data']['set']['slots'][0]['entrant'][
        'participants'][0]['user']['slug'],
                       r['data']['set']['slots'][1]['entrant']['id']: r['data']['set']['slots'][1]['entrant'][
                           'participants'][0]['user']['slug']
                       }
    return (participant_ids[winner_entrant_id], participant_ids[loser_entrant_id])


def get_all_sets_to_do_stuff(phase_id, phase_group_id):
    # event_id = 553068  # NA Southwest ultimate qualifiers online
    # phase_id = 908846
    # phase_group_id = 1449589
    page_number = 1
    per_page = 100
    ql_req = f"""
    query PhaseQuery{{
      phase(id: {phase_id}){{
        name
        phaseOrder
        phaseGroups(query:{{
          filter: {{
            id:{phase_group_id}
          }}
        }}){{
          nodes{{
            sets(page:{page_number}, perPage:{per_page}){{
              pageInfo{{
                page
                perPage
                totalPages
              }}
              nodes{{
                id
                round
                startedAt
              }}
            }}
          }}
        }}
      }}
    }}
    """
    r = requests.post(
        "https://api.smash.gg/gql/alpha",
        data={
            "query": ql_req,
            "variables": f'{{}}',
        },
        headers={
            'Authorization': f'Bearer {"690ea7f74c5f9b331c7148ba0a7a34e3"}',
        }
    )
    r = r.json()
    print(r['data']['phase']['phaseGroups']['nodes'][0]['sets']['pageInfo']['totalPages'])
    if r['data']['phase']['phaseGroups']['nodes'][0]['sets']['pageInfo']['totalPages'] not in (1, 0):
        raise ValueError
    sets_in_response: list = r['data']['phase']['phaseGroups']['nodes'][0]['sets']['nodes']
    sets_in_response = [item for item in sets_in_response if item['startedAt'] is not None]
    sets_in_response.sort(key=lambda x: x['startedAt'])
    return [x['id'] for x in sets_in_response]

    # # dict will essentially be results[round] = {id1, id2, ...}
    # rounds_to_add = {val['round'] for val in sets_in_response}
    # results = {key: set() for key in rounds_to_add}
    # for sett in sets_in_response:
    #     results[sett['round']].add(sett['id'])


# Pools are the first set of rounds, labeled as OQ Phase 1 (Online qualifiers phase 1)

# OQ phase 1 (OQA#) where # in (1, ..., 32)
# Winners -> OQ Phase 2
# Losers -> LCQ Phase 1
# OQ phase 2 (OQB#) where # in (1,2,3,4)
# Winners -> OQ - Top Cut
# Losers -> LCQ Phase 2 (various different stages)
# OQ Top Cut (OQC1)
# Winners -> OQ Finals
# Losers -> LCQ Top Cut
# OQ Finals (OQD1)
# Winners -> N/A
# Losers -> N/A

# LCQ Phase 1:
# Winners -> LCQ Phase 2
# Losers -> N/A
# LCQ Phase 2:
# Winners -> LCQ Phase 3
# Losers -> N/A
# LCQ Phase 3
# Winners -> LCQ Top Cut
# Losers -> N/A
# LCQ Top Cut
# Winners -> LCQ Finals
# Loser -> N/A
# LCQ Finals
# Winners -> N/A
# Losers -> N/A


# LCQ Top


def get_entrant_elo_from_event(elo, event_id):
    get_phase_ids = f"""
    query TournamentQuery{{
        event(id: {event_id}){{
            name
            phases{{
                id
                phaseOrder
                phaseGroups{{
                    nodes{{
                        id
                        displayIdentifier
                    }}
                }}
            }}
        }}
    }}
    """
    r = requests.post(
        "https://api.smash.gg/gql/alpha",
        data={
            "query": get_phase_ids,
            "variables": f'{{}}',
        },
        headers={
            'Authorization': f'Bearer {"690ea7f74c5f9b331c7148ba0a7a34e3"}',
        }
    )
    r = r.json()
    phases: list = r['data']['event']['phases']
    phases.sort(key=lambda x: x['phaseOrder'])
    entrant_info = elo
    for phase in phases:
        phase_id = phase['id']
        # Loop over the phases in order, doing all the things
        for phase_group in phase['phaseGroups']['nodes']:
            phase_group_id = phase_group['id']
            sets_to_do_stuff = get_all_sets_to_do_stuff(phase_id, phase_group_id)
            time.sleep(1)
            for sett in sets_to_do_stuff:
                print(f"Processing set {sett}")
                winner, loser = get_set_info(sett)
                if winner not in entrant_info:
                    entrant_info[winner] = 1200
                if loser not in entrant_info:
                    entrant_info[loser] = 1200
                entrant_info[winner], entrant_info[loser] = rate_1vs1(entrant_info[winner], entrant_info[loser])
                time.sleep(0.5)
