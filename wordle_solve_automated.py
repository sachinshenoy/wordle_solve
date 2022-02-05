import logging
import sys
import time

from dotenv import dotenv_values
import requests
import requests_cache
from rich import print as rprint
from rich.progress import track
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

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


current_word_list = []
requests_cache.install_cache(
    cache_name="wordle",
    backend="sqlite",
    expire_after=-1,
    ignored_parameters=["x-rapidapi-key"],
    match_headers=True,
    stale_if_error=True,
)
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(message)s",
    filename="wordle_solve.log",
)


def load_words():
    """
    Loads the words from the wordle_words.txt list and cleans up the words
    list to ensure that the words are stripped of any whitespaces
    and are only 5 characters long and are in lower case.


    Returns:
        [list]: List of potential words for the wordle solution
    """
    five_letter_words = []
    # Loads the Dictionary text file
    with open("wordle_words.txt") as word_file:
        lines = word_file.readlines()
        # Filter all words which are not 5 letters.
        for line in lines:
            if len(line.strip()) == 5:
                five_letter_words.append(line.strip().lower())
    print(f"Current Word List length - {len(five_letter_words)}")
    return five_letter_words


def solution_found(result_dict):
    """
    Get the input dictionary with determination of each character's validity
    and returns a true/false bool to indicate if the solution has been
    found.

    Args:
        result_dict (dict): Dictionary with wordle result for each character in the word.
    Returns:
        Bool with True or False to indicate if the wordle solution has been found.
    """
    if set(result_dict.values()) == {"correct"}:
        print("Congratulations - Solution Found \U0001F44D")
        print("Scripted by Sachin Shenoy")
        print("Twitter: https://twitter.com/sachinshenoy")
    return set(result_dict.values()) == {"correct"}


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


def find_bg(web_driver, word):
    """
    Uses the background colors of the words on the onscreen
    keyboard (as it matches the grid) to assign them results like:
    Green: "correct"
    Yellow: "present"
    Gray: "absent"
    These results are then returned for each character in the work
    as a disctionary with their associated results.

    Args:
        web_driver (selenium.webdrider): Selenium Webdriver
        word (str): The word which was guessed

    Returns:
        [dict]: Dictionary of characters in the word as keys and the
        results as values.
    """
    char_results = {}
    for char in track(word, description="Analyzing Results"):
        bg = web_driver.find_element(
            By.CSS_SELECTOR, keyboard[char]
        ).value_of_css_property("background-color")
        # rprint(f"Char - {char} BackGround: {bg}")
        match bg:
            case "rgba(181, 159, 59, 1)" | "rgba(201, 180, 88, 1)":
                char_results[char] = "present"
            case "rgba(58, 58, 60, 1)" | "rgba(120, 124, 126, 1)":
                char_results[char] = "absent"
            case "rgba(83, 141, 78, 1)" | "rgba(106, 170, 100, 1)":
                char_results[char] = "correct"
            case "rgba(129, 131, 132, 1)":
                char_results[char] = "other"
            case default:
                char_results[char] = "other"
    rprint(f"Word Result - {char_results}")
    return char_results


def solve_row(row_result):
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
        [str]: Like solution word
    """
    word_list = current_word_list.copy()
    for idx, char in enumerate(row_result):
        match row_result[char]:
            case "present":
                for word in word_list:
                    if not (char in word) or (char == word[idx]):
                        current_word_list.remove(word)
                word_list = current_word_list.copy()
            case "absent":
                for word in word_list:
                    if char in word:
                        current_word_list.remove(word)
                word_list = current_word_list.copy()
            case "correct":
                for word in word_list:
                    if not (char == word[idx]):
                        current_word_list.remove(word)
                word_list = current_word_list.copy()
            case "other":
                print(f"Character - {char} at index {idx} has state 'other'")
                sys.exit("Something went wrong. Character status incorrect !")
    print(f"Current Word List length - {str(len(word_list))}")

    # This is the avoid a API Call to get word frequencies
    # as we know the second word is going to be 'stomp'
    # if "".join(row_result.keys()) == "uraei":
    #     return {7.0: "stomp"}

    word_dict = {}
    word_dict[0.0] = []
    config = dotenv_values(".env")
    API_KEY = config.get("API_KEY")
    for word in word_list:
        url = f"https://wordsapiv1.p.rapidapi.com/words/{word}"
        headers = {
            "x-rapidapi-host": "wordsapiv1.p.rapidapi.com",
            "x-rapidapi-key": API_KEY,
        }
        response = requests.request("GET", url, headers=headers)
        if response.from_cache:
            print(f"{word} retrived from Cache!")
        response_json = response.json()
        if response.ok:
            if response_json.get("frequency"):
                word_dict[response_json["frequency"]] = word
            else:
                word_dict[0.0].append(word)
    reverse_sorted_keys = sorted(word_dict, reverse=True)
    rprint(f"Word-Dict: {word_dict}")
    return word_dict[reverse_sorted_keys[0]]


def main():
    """
    Script to control Chrome Browser to Solve that day's
    Wordle Puzzle.
    Input: None
    Output: Solution to the Wordle Puzzle by controlling the browser
    """

    global current_word_list
    current_word_list = load_words()

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
    # game_keyboard_root_shadow.find_element(
    #     By.CSS_SELECTOR, "div:nth-child(1) > button:nth-child(2)"
    # ).click()

    sendkeys(game_keyboard_root_shadow, "uraei")
    time.sleep(5)
    row_result = find_bg(game_keyboard_root_shadow, "uraei")
    new_word = solve_row(row_result)
    if solution_found(row_result):
        sys.exit()

    # sendkeys(game_keyboard_root_shadow, "stomp")
    # time.sleep(5)
    # row_result = find_bg(game_keyboard_root_shadow, "stomp")
    # new_word = solve_row(row_result)
    # if solution_found(row_result):
    #     sys.exit()

    for _ in range(4):
        sendkeys(game_keyboard_root_shadow, new_word)
        time.sleep(5)
        row_result = find_bg(game_keyboard_root_shadow, new_word)
        if solution_found(row_result):
            # share_button = game_modal_root_shadow.find_element(By.CSS_SELECTOR, "#keyboard")
            sys.exit()
        else:
            new_word = solve_row(row_result)
    print("Uh Oh - Couldn't find the Solution \U0001F622")


if __name__ == "__main__":
    main()
