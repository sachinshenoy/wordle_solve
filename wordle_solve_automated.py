import json
import logging
import re
import sys
import time
from collections import Counter

from rich import print as rprint
from rich.progress import track
from selenium import webdriver
from selenium.webdriver.common.by import By

start_word = "uraei"
keyboard = {
    "q": "div:nth-child(1) > button:nth-child(1)",
    "w": "div:nth-child(1) > button:nth-child(2)",
    "e": "div:nth-child(1) > button:nth-child(3)",
    "r": "div:nth-child(1) > button:nth-child(4)",
    "t": "div:nth-child(1) > button:nth-child(5)",
    "y": "div:nth-child(1) > button:nth-child(6)",
    "u": "div:nth-child(1) > button:nth-child(7)",
    "i": "div:nth-child(1) > button:nth-child(8)",
    "o": "div:nth-child(1) > button:nth-child(9)",
    "p": "div:nth-child(1) > button:nth-child(10)",
    "a": "div:nth-child(2) > button:nth-child(2)",
    "s": "div:nth-child(2) > button:nth-child(3)",
    "d": "div:nth-child(2) > button:nth-child(4)",
    "f": "div:nth-child(2) > button:nth-child(5)",
    "g": "div:nth-child(2) > button:nth-child(6)",
    "h": "div:nth-child(2) > button:nth-child(7)",
    "j": "div:nth-child(2) > button:nth-child(8)",
    "k": "div:nth-child(2) > button:nth-child(9)",
    "l": "div:nth-child(2) > button:nth-child(10)",
    "enter": "div:nth-child(3) > button:nth-child(1)",
    "z": "div:nth-child(3) > button:nth-child(2)",
    "x": "div:nth-child(3) > button:nth-child(3)",
    "c": "div:nth-child(3) > button:nth-child(4)",
    "v": "div:nth-child(3) > button:nth-child(5)",
    "b": "div:nth-child(3) > button:nth-child(6)",
    "n": "div:nth-child(3) > button:nth-child(7)",
    "m": "div:nth-child(3) > button:nth-child(8)",
    "x": "div:nth-child(3) > button:nth-child(9)",
    "del": "div:nth-child(3) > button:nth-child(10)",
}

start_time = time.time()

current_word_list = []


logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(message)s",
    filename="wordle_solve.log",
)


def load_words(file_name):
    """
    Loads the words from the filename (One word per line) provided
    and cleans up the words list to ensure that the words are stripped
    of any whitespaces and are only 5 characters long and are in lower case.


    Returns:
        [list]: List of words from the file containing the words.
    """
    five_letter_words = []
    # Loads the Dictionary text file
    with open(file_name) as word_file:
        lines = word_file.readlines()
        # Filter all words which are not 5 letters.
        for line in lines:
            if len(line.strip()) == 5:
                five_letter_words.append(line.strip().lower())
    print(f"Number of words in the {file_name} - {len(five_letter_words)}")
    return five_letter_words


def solution_found(result_list):
    """
    Get the input dictionary with determination of each character's validity
    and returns a true/false bool to indicate if the solution has been
    found.

    Args:
        result_dict (dict): Dictionary with wordle result for each character in the word.
    Returns:
        Bool with True or False to indicate if the wordle solution has been found.
    """
    if set(result_list) == {"correct"}:
        rprint("Congratulations - Solution Found \U0001F44D")
        rprint(f"Script Execution Time = {time.time() - start_time:.2f} Secs")
        rprint("Scripted by Sachin Shenoy")
        rprint("Twitter: https://twitter.com/sachinshenoy")
    return set(result_list) == {"correct"}


def sendkeys(web_driver, word):
    """
    This function take the webdriver and a string (word) as
    input which is then entered into the Wordle Puzzle one
    Charater at a time.

    Args:
        web_driver (selenium.webdriver): The Keyboard Shadow DOM from Wordle.
        word (str): Word to be entered into the current row of the wordle puzzle.
    Returns:
        None
    """
    for char in track(word, description="Entering the Word"):
        web_driver.find_element(By.CSS_SELECTOR, keyboard[char]).click()
        time.sleep(0.75)
    web_driver.find_element(By.CSS_SELECTOR, keyboard["enter"]).click()


def find_bg(web_driver, row_number):
    """
    Identifies the background colors of the words from the results grid
    and assigns them results as follows to list:
    Green: "correct"
    Yellow: "present"
    Gray: "absent"
    These results are then returned for each character in the word
    as a list of results.

    Args:
        web_driver (selenium.webdrider): Selenium Webdriver
        row_number (int): Row number for which the results are needed.

    Returns:
        [list]: List containing 5 elements with correspond to each
        character in the row being analyzed
    """
    char_results = []
    result_list = []
    game_row_x_root = web_driver.find_element(
        By.CSS_SELECTOR, f"#board > game-row:nth-child({row_number})"
    )
    game_row_x_root_shadow = game_row_x_root.shadow_root
    for i in range(1, 6):
        game_row_x_i_root = game_row_x_root_shadow.find_element(
            By.CSS_SELECTOR, f"div > game-tile:nth-child({i})"
        )
        game_row_x_i_root_shadow = game_row_x_i_root.shadow_root
        cell = game_row_x_i_root_shadow.find_element(By.CSS_SELECTOR, "div")
        cell_bg = cell.value_of_css_property("background-color")
        result_list.append(cell_bg)
        # rprint(cell_bg)

    for bg in track(result_list, description="Analyzing Results"):
        match bg:
            case "rgba(181, 159, 59, 1)" | "rgba(201, 180, 88, 1)":
                char_results.append("present")
            case "rgba(58, 58, 60, 1)" | "rgba(120, 124, 126, 1)":
                char_results.append("absent")
            case "rgba(83, 141, 78, 1)" | "rgba(106, 170, 100, 1)":
                char_results.append("correct")
            case "rgba(129, 131, 132, 1)":
                char_results.append("other")
            case default:
                char_results.append("other")
    rprint(f"Word Result - {char_results}")
    return char_results


def solve_row(row_results, word_guess):
    """
    Receives a dictionary with the results of the previous word entered.
    It then performs two actions:
    1. Eliminates words from the possible word list.
    2. Checks this list against the WordAPI (RapidAPI) for popularity
    using the frequency metric.

    The most popular word is then returned.This word with
    the highest frequency is considered more likely as it would be less
    obscure.

    Args:
        row_result (dictionary): Dictionary of each character of the previous
        word with the results like "present", "absent" or "correct"

    Returns:
        [str]: Best solution word based on previous results
    """
    multi_char = {}

    # Checks if a word guess has repeating characters. If there is a charater
    # repearing, it then updates the multi_char dictionary with the row
    # result determination of each of those repeating charaters.
    # This is done using regex. The span for each finditer result
    # returns a tuple with the location where the substring started and ended.
    # We use the starting position of the substring to gather the row result
    # for that character from the row_result list and add all the findings
    # is to a temp list which is then added to the multi_char dictionary
    # and used further down in the word elimination logic.

    if len(set(word_guess)) < 5:
        for char, occurance in Counter(word_guess).most_common():
            if occurance > 1:
                temp_list = []
                matches = re.finditer(char, word_guess)
                for result in matches:
                    temp_list.append(row_results[result.span()[0]])
                multi_char[char] = temp_list

    word_list = current_word_list.copy()
    for idx, guess in enumerate(zip(word_guess, row_results)):
        match guess[1]:
            case "present":
                for word in word_list:
                    if not (guess[0] in word) or (guess[0] == word[idx]):
                        current_word_list.remove(word)
                word_list = current_word_list.copy()
            case "absent":
                for word in word_list:
                    if guess[0] in word and Counter(word_guess)[guess[0]] == 1:
                        current_word_list.remove(word)
                    elif guess[0] == word[idx]:
                        current_word_list.remove(word)
                word_list = current_word_list.copy()
            case "correct":
                for word in word_list:
                    if (
                        not (guess[0] == word[idx])
                        # and Counter(word_guess)[guess[0]] == 1
                    ):
                        current_word_list.remove(word)
                word_list = current_word_list.copy()

            case "other":
                print(f"Character - {guess[0]} at index {idx} has state 'other'")
                sys.exit("Something went wrong. Character status incorrect !")
    # Check if a word guess has repeating characters. If there is a charater
    # repearing, it then checks to see if both the characters need to exist
    # in the word based of word results.
    # i.e : If one is present and other is correct or the other way around.
    # If that is the case then it will remove all words from the word list
    # which do not have these characters.
    # Assumption: There can only be two or three repeating characters
    if len(set(word_guess)) < 5:
        for char, occurance in Counter(word_guess).most_common():
            if occurance > 1:
                match multi_char[char]:
                    case ["present", "correct"] | ["correct", "present"]:
                        for word in word_list:
                            if Counter(word)[char] != occurance:
                                current_word_list.remove(word)
                    case ["present", "correct", "correct"] | [
                        "present",
                        "correct",
                        "present",
                    ] | ["correct", "present", "present"] | [
                        "correct",
                        "present",
                        "correct",
                    ]:
                        for word in word_list:
                            if Counter(word)[char] != occurance:
                                current_word_list.remove(word)
        word_list = current_word_list.copy()

    rprint(f"Multi Character Dictionary: {multi_char}")
    rprint(f"Current Word List length - {str(len(word_list))}")

    # This is the avoid a API Call to get word frequencies
    # as we know the second word is going to be 'stomp'
    # if "".join(row_result.keys()) == "uraei":
    #     return {7.0: "stomp"}

    word_dict = {}
    max_frequency = 0

    with open("words_json.txt", "r") as fh:
        frequency_dict = json.load(fh)

    for word in word_list:
        word_dict[word] = frequency_dict[word]
        if max_frequency < word_dict[word]:
            recommended_word = word
            max_frequency = word_dict[word]

    # reverse_sorted_keys = sorted(word_dict, reverse=True)
    current_word_list.remove(recommended_word)
    rprint(f"Word-Dict: {word_dict}")
    # rprint(f"API Cache Hit Rate : {(cache_count*100)/len(word_list):.2f} %")
    rprint(
        f"Recommended Word : {recommended_word}, Frequency : {word_dict[recommended_word]}"
    )
    return recommended_word


def main():
    """
    Script to control Chrome Browser to Solve that day's
    Wordle Puzzle.
    Input: None
    Output: Solution to the Wordle Puzzle by controlling the browser
    """

    global current_word_list
    current_word_list = load_words("wordle_words.txt")
    allowed_guesses = load_words("wordle_allowed_guesses.txt")

    if not (start_word in current_word_list or start_word in allowed_guesses) or not (
        len(start_word) == 5
    ):
        rprint("Uh Oh - Please check 'Start Word' \U0001F622")
        rprint(f"Script Execution Time = {time.time() - start_time: .2f} Secs")
        rprint("Scripted by Sachin Shenoy")
        rprint("Twitter: https://twitter.com/sachinshenoy")
        sys.exit()

    options = webdriver.ChromeOptions()
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    options.add_experimental_option("detach", True)

    driver = webdriver.Chrome(options=options)
    driver.get("https://www.powerlanguage.co.uk/wordle/")
    driver.implicitly_wait(5)

    game_app_root = driver.find_element(By.CSS_SELECTOR, "game-app")
    game_app_root_shadow = game_app_root.shadow_root

    # Close the initial help screen
    game_modal_root = game_app_root_shadow.find_element(By.CSS_SELECTOR, "game-modal")
    game_modal_root_shadow = game_modal_root.shadow_root
    close_button = game_modal_root_shadow.find_element(By.CSS_SELECTOR, "game-icon")
    close_button.click()

    # Identify the Keyboard Elements in the Shadow DOM
    game_keyboard_root = game_app_root_shadow.find_element(
        By.CSS_SELECTOR, "game-keyboard"
    )
    game_keyboard_root_shadow = game_keyboard_root.shadow_root
    game_keyboard_root_shadow.find_element(By.CSS_SELECTOR, "#keyboard")

    # Send the start word to the Wordle Puzzle
    sendkeys(game_keyboard_root_shadow, start_word)
    time.sleep(2)
    row_results = find_bg(game_app_root_shadow, 1)
    new_word = solve_row(row_results, start_word)
    if solution_found(row_results):
        sys.exit()

    # sendkeys(game_keyboard_root_shadow, "stomp")
    # time.sleep(3)
    # row_results = find_bg(game_app_root_shadow, 2)
    # new_word = solve_row(row_results, "stomp")
    # if solution_found(row_results):
    #     sys.exit()

    for i in range(2, 7):
        sendkeys(game_keyboard_root_shadow, new_word)
        time.sleep(2)
        row_results = find_bg(game_app_root_shadow, i)
        if solution_found(row_results):
            sys.exit()
        else:
            new_word = solve_row(row_results, new_word)
    rprint("Uh Oh - Couldn't find the Solution \U0001F622")
    rprint(f"Script Execution Time = {time.time() - start_time: .2f} Secs")


if __name__ == "__main__":
    main()
