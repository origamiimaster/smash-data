from json import JSONDecodeError

import requests


def get_game_results(set_id, api):
    try:
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
                'Authorization': f'Bearer {api}',
            }
        )
        r = r.json()
        winner_entrant_id = r['data']['set']['winnerId']
        loser_entrant_id = r['data']['set']['slots'][0]['entrant']['id'] if winner_entrant_id == \
                                                                            r['data']['set']['slots'][1][
                                                                                'entrant']['id'] \
            else r['data']['set']['slots'][1]['entrant']['id']

        participant_ids = {r['data']['set']['slots'][0]['entrant']['id']: r['data']['set']['slots'][0]['entrant'][
            'participants'][0]['user']['slug'],
                           r['data']['set']['slots'][1]['entrant']['id']: r['data']['set']['slots'][1]['entrant'][
                               'participants'][0]['user']['slug']
                           }
        return (participant_ids[winner_entrant_id], participant_ids[loser_entrant_id])
    except JSONDecodeError:
        return False

