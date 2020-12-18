"""
Determines how many net positive and how many net negative matchups a character has, then
returns a score.
"""
import interpret_data


def how_many_pos_matchups(char_name: str, data) -> int:
    """
    Gets char matchup dict from interpret data, and returns a score with a number of positive MUs.
    :param data:
    :param char_name:
    :return:
    """
    matchups = interpret_data.get_chars_match_up(data)
    count = len([key for key in matchups[char_name] if matchups[char_name][key] > 0.5])
    return count


def get_pos_matchups(char_name: str, data) -> list:
    """
    Returns list of the character names with positive matchups (ie > 50% win rate).
    :param char_name:
    :param data:
    """
    matchups = interpret_data.get_chars_match_up(data)
    return [key for key in matchups[char_name] if matchups[char_name][key] > 0.5]


def find_best_matchup_teams(data) -> list:
    """Find the two characters that have the most impressive matchup combination."""
    matchups = interpret_data.get_chars_match_up(data)
    pos_matchups = {}
    for character in matchups:
        pos_matchups[character] = get_pos_matchups(character, data)
    # print(pos_matchups)
    combined_matchups = {}
    for char1 in pos_matchups:
        for char2 in pos_matchups:
            combined_matchups[(char1, char2)] = set()
            combined_matchups[(char1, char2)].update(pos_matchups[char1])
            combined_matchups[(char1, char2)].update(pos_matchups[char2])
    print(combined_matchups)
    max_mus = 0
    best = None
    for combination in combined_matchups:
        if len(combined_matchups[combination]) > max_mus:
            max_mus = len(combined_matchups[combination])
            best = combination
    print(best, max_mus)
    print(combined_matchups[best])


if __name__ == "__main__":
    my_data = interpret_data.start_scroll()
    interpret_data.merge_echoes(my_data)
    # print(get_pos_matchups("Terry", my_data))
    find_best_matchup_teams(my_data)
