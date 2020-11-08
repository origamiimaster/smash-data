import requests
# Client to download and do all the stuff


class SmashGGConnectionTHINGY:
    def __init__(self, api_token):
        self.api = api_token
        self.url = "https://api.smash.gg/gql/alpha"
        self.id = 1386

    def get_tournaments(self, start_time, end_time):
        per_page = 60
        r = requests.post(
            self.url,
            data={
                "query": """
                    query TournamentsByVideogame($page: Int!, $perPage: Int!, $videogameId: ID!, $after: Timestamp!, $before: Timestamp!) {
                      tournaments(query: {
                        perPage: $perPage
                        page: $page
                        sortBy: "startAt asc"
                        filter: {
                          past: false
                          afterDate: $after
                          beforeDate: $before
                          videogameIds: [
                            $videogameId
                          ]
                        }
                      }) {
                        nodes {
                          id
                          name
                          startAt
                          endAt
                          events(limit: 20) {
                            id
                            name
                            videogame {
                                id
                            }
                          }
                        }
                      }
                    }
                """,
                "variables": f'{{"videogameId": {self.id}, "page": {0}, "perPage": {per_page}, "after": {start_time}, "before": {end_time} }}',
            },
            headers={
                'Authorization': f'Bearer {self.api}',
            }
        )
        return r.json()['data']['tournaments']['nodes']

    def get_tournament_by_id(self, id):
        r = requests.post(
            self.url,
            data={
                "query": """
                    query TournamentsByVideogame($id: ID!) {
                      tournament(id: $id) {
                        id
                        name
                        endAt
                        events(limit: 10) {
                            name
                            id
                            videogame {
                                id
                            }
                        }
                      }
                    }
                """,
                "variables": f'{{"id": {id} }}',
            },
            headers={
                'Authorization': f'Bearer {self.api}',
            }
        )
        return r.json()['data']['tournament']

    def get_sets(self, event_id, page=1):
        print(event_id)
        r = requests.post(
            self.url,
            data={
                "query": """
                    query SetsByEvent($eventId: ID!, $page: Int!, $perPage: Int!) {
                      event(id: $eventId) {
                        sets(page: $page, perPage: $perPage) {
                            nodes {
                                id
                                games {
                                    winnerId
                                    stage {
                                      name
                                    }
                                    selections {
                                        entrant {
                                            id
                                            name
                                        }
                                        selectionType
                                        selectionValue
                                    }
                                }
                            }
                        }
                      }
                    }
                """,
                "variables": f'{{"eventId": {event_id}, "page": {page}, "perPage": {40} }}',
            },
            headers={
                'Authorization': f'Bearer {self.api}',
            }
        )
        try:
            event = r.json()['data']['event']
            if event is None:
                return []
            sets = event['sets']['nodes']
        except Exception:
            print(r.json())
            raise
        return sets
