"""
Client to download and do all the stuff
"""
import time
import json
import requests


# noinspection SpellCheckingInspection
class SmashGGClient:
    """
    Class to interact with the smashGG GQL database
    """

    def __init__(self, *api_tokens) -> None:
        self.curr = 0
        if len(api_tokens) == 1:
            self.api = api_tokens[0]
            self.api_list = [self.api]
        else:
            self.api_list = []
            for api_token in api_tokens:
                self.api_list.append(api_token)
            self.api = self.api_list[0]
        self.url = "https://api.smash.gg/gql/alpha"
        self.id = 1386

    def update(self) -> None:
        """
        Updates the API key after a succesful call
        """
        self.api = self.api_list[((self.curr + 1) % len(self.api_list)) % len(self.api_list)]

    def get_tournaments(self, start_time: int, end_time: int) -> dict:
        """
        Gets all tournaments between a start time and an end time
        """
        self.update()
        per_page = 60
        r = requests.post(
            self.url,
            data={
                "query": """
                    query TournamentsByVideogame($page: Int!, $perPage: Int!, $videogameId: ID!, 
                    $after: Timestamp!, $before: Timestamp!) {
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
                "variables": f'{{"videogameId": {self.id}, "page": {0}, "perPage": {per_page}, '
                             f'"after": {start_time}, "before": {end_time} }}',
            },
            headers={
                'Authorization': f'Bearer {self.api}',
            }
        )
        return r.json()['data']['tournaments']['nodes']

    def get_tournament_by_id(self, tourney_id: int) -> dict:
        """
        Returns a given tournament.
        """
        self.update()
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
                "variables": f'{{"id": {tourney_id} }}',
            },
            headers={
                'Authorization': f'Bearer {self.api}',
            }
        )
        return r.json()['data']['tournament']

    def get_sets(self, event_id: int, page: int = 1) -> (list, dict):
        """
        Returns a list of sets for a given event.
        """
        self.update()
        # print(event_id)
        r = requests.post(
            self.url,
            data={
                "query": """
                    query SetsByEvent($eventId: ID!, $page: Int!, $perPage: Int!) {
                      event(id: $eventId) {
                        tournament{
                            lat
                            lng
                        }
                        sets(page: $page, perPage: $perPage) {
                            nodes {
                                id
                                displayScore
                                fullRoundText
                                hasPlaceholder
                                winnerId
                                slots{
                                    entrant{
                                        id
                                    }
                                }
                                games {
                                    id
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
                "variables": f'{{"eventId": {event_id}, "page": {page}, "perPage": {30} }}',
            },
            headers={
                'Authorization': f'Bearer {self.api}',
            }
        )
        try:
            event = r.json()['data']['event']
            if event is None:
                return [], None
            sets = event['sets']['nodes']
        except Exception:
            print(r)
            if 'Cannot query more than the 10,000th entry' in json.dumps(r.json()):
                print("Failed")
                return [], None
            print(r.json())
            raise
        # print(event["tournament"])
        return event["tournament"], sets

    def get_entrant_to_user_info(self, event_id):
        self.update()
        r = requests.post(
            self.url,
            data={
                "query": """
                    query SetsByEvent($eventId: ID!) {
                        event(id: $eventId) {
                        entrants{
                          nodes{
                            id
                            participants{
                              user{
                                id
                                name
                                player{
                                  gamerTag
                                }
                              }
                            }
                          }
                        }
                        }
                    }
                """,
                "variables": f'{{"eventId": {event_id} }}',
            },
            headers={
                'Authorization': f'Bearer {self.api}',
            }
        )

        # time.sleep(0.2)
        return r.json()["data"]["event"]["entrants"]["nodes"]
        # except (KeyError, TypeError):
        #     raise KeyError
        # return None

    def get_user_info_by_id(self, user_id):
        self.update()
        r = requests.post(
            self.url,
            data={
                "query": """
                query User($id: ID) {
                  user(id: $id) {
                    slug,
                    name, 
                    bio,
                    location{
                      country
                    }
                    player{
                      gamerTag,
                      prefix,
                    },
                  }
                }
                """,
                "variables": f'{{"id": {user_id}}}'
            },
            headers={
                'Authorization': f'Bearer {self.api}',
            }
        )
        return r.json()
