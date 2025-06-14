"""An ELO calculator"""
from interpret_data import event_scroll
from download import SmashGGClient
from interpret_data import get_event_sets
import datetime
import json
from time import sleep
from json import JSONDecodeError
from loading import LoadingBar
# import matplotlib.pyplot as plt

def calculate_ratings(r_1, r_2, s_1, s_2, k=32) -> tuple:
    """
    Calculate new ratings from the results of a match.
    """
    e_1 = 10 ** (r_1 / 400)
    e_2 = 10 ** (r_2 / 400)
    r_1m = r_1 + k * (s_1 - (e_1 / (e_1 + e_2)))
    r_2m = r_2 + k * (s_2 - (e_2 / (e_2 + e_1)))
    return (max(0, r_1m), max(0, r_2m))


def expected_probability(r_a, r_b) -> float:
    """Returns the probability of a or b winning based on ratings
    """
    return 1 / (1 + 10 ** ((r_a - r_b) / 400))


def rating_change(r_a, r_b, score, k=32) -> float:
    """Resulting rating change based on a score from 0 to 1"""
    return r_a + k * (score - expected_probability(r_a, r_b))

def do_stuff_with_data(raw_data):
    """Gets top 100 highest Elo slugs and prefix | gamerTag"""
    # from download import SmashGGClient
    mySmashGGClient = SmashGGClient("3371d61c8013075a7e6be7677baad497")
    # with open("data.txt", "r") as f:
        # raw_data = eval(f.read())
    my_data = dict(sorted(raw_data.items(), key=lambda item: item[1]))
    for i in list(reversed(my_data))[:100]:
        data = mySmashGGClient.get_user_info_by_id(i)['data']
        print(str(data['user']['slug']) + " " + str(i) + " " + str(data['user']['player']['gamerTag']) + " " + str(
            my_data[i]))

if __name__ == "__main__":
    # Initialize dict for players. It will be in the format of [user_id]->elo_score
    player_score_info = dict()
    # Get list of all the events
    event_data = event_scroll()
    # Sort tournaments by date, from oldest to newest.
    event_data.sort(key=lambda x: x['_source']['timestamp'])
    mySmashGGClient = SmashGGClient("baeb4acfe9b8dabf103931a5e46463e3")  # "3371d61c8013075a7e6be7677baad497"
    my_loader = LoadingBar(len([x for x in event_data if x["_source"]["done"]]))

    my_loader.print()
    # my_loader.set(-1)
    # mega_conversion_info = {}

    # Loop over every event
    # print (event_data)

    for event in [x for x in event_data if x["_source"]["done"]]:

        # if event["_source"]["done"]:
        my_loader.increment()
        my_loader.print()
        sets = get_event_sets(event['_id'])
        if len(sets) <= 100:
            continue
        try:
            user_id_info = mySmashGGClient.get_entrant_to_user_info(event["_source"]["event_id"])
        except KeyError:
            # print("could not get general user info")
            my_loader.add_error("could not get general user info")
            my_loader.print()
            sleep(30)
            continue
        except TypeError:
            # print("could not get general user info 2")
            my_loader.add_error("could not get general user info 2")
            my_loader.print()
            continue
        except JSONDecodeError:
            # print("JSON ERROR:")
            my_loader.add_error("JSON decode error")
            my_loader.print()
            continue
        except Exception as a:
            print(a)
            continue
        my_loader.add_error("")
        # if user_id_info is None:
        #     print("could not get general user info")
        #     sleep(60)
        #     continue

        conversion_info1 = {}
        conversion_info2 = {}
        new_participants = {}
        if user_id_info is not None:
            for entrant in user_id_info:
                if len(entrant['participants']) > 1:
                    # Team / Crew tournament, not including in ELO calculations.  Disqualify event.
                    # new_participants = {}
                    # print("team event: " + str(event["_source"]["event_id"]))
                    break
                else:
                    for participant in entrant["participants"]:
                        if participant["user"] is not None:
                            # if entrant["participants"][0]["user"] is not None:
                            new_participants[entrant["id"]] = entrant["participants"][0]
                            conversion_info1[entrant["id"]] = entrant["participants"][0]["user"]["id"]
                            # conversion_info2[entrant["participants"][0]["user"]["id"]] = entrant["id"]
                        else:
                            new_participants[entrant["id"]] = None
            # conversion_info1[None] = None
            for new_key in new_participants:
                if new_participants[new_key] is None:
                    player_score_info[None] = 1000
                else:
                    player_score_info[conversion_info1[new_key]] = 1000  # Default player score at start

            # print(player_score_info)
            # print("event_id " + event['_id'])
            # print((sets))
            if datetime.datetime.fromtimestamp(event["_source"]["timestamp"] / 1000) > \
                    datetime.datetime(2020, 10, 1):  # or len(player_score_info) >= 20000:
                break
            for my_set in sets:
                winner_id = my_set["_source"]["winner_id"]
                loser_id = my_set["_source"]["loser_id"]
                try:
                    if winner_id in conversion_info1:
                        winner_user_id = conversion_info1[winner_id]
                    else:
                        winner_user_id = None
                    if loser_id in conversion_info1:
                        loser_user_id = conversion_info1[loser_id]
                    else:
                        loser_user_id = None
                    # print("winner_user_id = " + str(winner_user_id))
                    # print("loser_user_id = " + str(loser_user_id))
                    if winner_id is not None:
                        r_1 = player_score_info[winner_user_id]
                    else:
                        r_1 = 1000
                    if loser_id is not None:
                        r_2 = player_score_info[loser_user_id]
                    else:
                        r_2 = 1000
                    (new_r_1, new_r_2) = calculate_ratings(r_1, r_2, 1, 0)
                    player_score_info[winner_user_id] = new_r_1
                    player_score_info[loser_user_id] = new_r_2
                except KeyError:
                    # print("error")
                    continue

    with open('test.json', 'w') as f:
        json.dump(player_score_info, f)
