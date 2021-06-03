"""This will try and calculate elo scores for the past years tournaments.  Hopefully."""
import time
import datetime

import requests
from single_elim import get_api_key


def get_all_tourneys_in_year():
    now = time.time()
    then = now - datetime.timedelta(days=365).total_seconds()  # Rip leap year
    page = 1
    query = f"""
    query GetPastEvents{{
        tournaments(
            query:{{
                page: {page}
                perPage:500
                filter:{{
                    afterDate: {round(then)}
                    beforeDate: {round(now)}
                    videogameIds:[1386]
                }}
                sortBy:"time"
            }}
        ){{
            pageInfo{{
                totalPages
            }}
            nodes{{
                id
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
    ).json()
    total_pages = r['data']['tournaments']['pageInfo']['totalPages']
    tournament_ids = []
    while page <= total_pages:
        # Process the stuff
        for tourney_id in r['data']['tournaments']['nodes']:
            tournament_ids.append(tourney_id['id'])
        # Determine if need to break
        if page == total_pages:
            break
        # If not, get next data and loop again.
        page += 1
        query = f"""
        query GetPastEvents{{
            tournaments(
                query:{{
                    page: {page}
                    perPage:500
                    filter:{{
                        afterDate: {round(then)}
                        beforeDate: {round(now)}
                        videogameIds:[1386]
                    }}
                    sortBy:"time"
                }}
            ){{
                pageInfo{{
                    totalPages
                }}
                nodes{{
                    id
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
        ).json()
        print(len(tournament_ids))
        time.sleep(5)
    return tournament_ids


# Iteration plan:
# 1. Get all tournaments, incrementing startedAt to prevent 10,000 error in pagination.
# 2. For each tournament, get all events that are SSBU (prob don't need the 10,000 error fix, maybe not even pagination)
# 3. Loop over each event, getting all phase
# 4. Loop over each phase, getting all phase groups
# 5. Loop over each phase group, getting each set.
# 6. For each set, do Elo calculations.


# 1. Get all tournaments:
def get_all_tourneys(output, start_time=time.time() - datetime.timedelta(days=365).total_seconds()):
    tournaments = output
    start = start_time
    end = time.time()
    while start < end:
        query = build_query(start, end)
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
        try:
            j = r.json()
            if len(j['data']['tournaments']['nodes']) == 0:
                break
            for tournament in j['data']['tournaments']['nodes']:
                tournament_id = tournament['id']
                tournament_time = tournament['startAt']
                if tournament_time > start:
                    start = tournament_time
                tournaments.append(tournament_id)
            print(len(tournaments))
            time.sleep(0.8)
        except Exception as e:
            print(e)
            time.sleep(1)

    # return tournaments


def build_query(start_time, end_time):
    query = f"""
    query GetTournaments{{
        tournaments(
            query:{{
                page: 1
                perPage:500
                filter:{{
                    afterDate: {int(start_time)}
                    beforeDate: {int(end_time)}
                    videogameIds:[1386]
                }}
                sortBy:"time"
            }}
        ){{
            pageInfo{{
                totalPages
            }}
            nodes{{
                id
                startAt
            }}
        }}
    }}
    """
    return query


if __name__ == "__main__":
    test = []
    get_all_tourneys(test)
