# Wordle_Solve

Wordle_Solve is a script written in Python using the selenium module to try and solve the daily Wordle puzzle by taking control of the browser instance on your system. This has only been tested on Windows 10 in light and dark mode. The WordsAPI hosted on RapidAPI was used to generate a Zipf distribution frequency score for each word in the Wordle word collection; which is then used to select the best guess for the next word from list condensed based on the results of the previous guesses.

## Links

- [Repo](https://github.com/sachinshenoy/wordle_solve "<Wordle Solver> Repo")
- [RapidAPI](https://rapidapi.com/dpventures/api/wordsapi/pricing)
- [WordsAPI](https://www.wordsapi.com/)
- [ChromeDriver](https://chromedriver.chromium.org/downloads)


## Screenshot

![Main Script](/screenshots/1.png "Main Script")



## Built With

- Python 3.10.x
- Rich
- Selenium
- Chromium WebDriver

## Installation

- **Requires Python Version >= 3.10.x**
- Clone the Repo
- Use the package manager [pip](https://pip.pypa.io/en/stable/) to install the dependencies.
- Download the appropriate [ChromeDriver](https://chromedriver.chromium.org/downloads) for the your version of Chrome Browser and save it in the same folder as the python script.


```bash
python -m venv venv

{--ACTIVATE THE VENV AS PER YOUR OS--}

pip install -r requirements.txt

```

## Usage

```python
# Run the Python Script !!

python wordle_solve_automated.py

```

## Future Updates

- [X] ~~Optimized Wait timers.~~
- [ ] Move the console messages to Logs.
- [ ] Move away from BasicConfig for Logging
- [X] ~~Fewer API Calls.~~
- [X] ~~Pick different Starting words.~~

## License
[MIT](https://choosealicense.com/licenses/mit/)

## Author

**Sachin Shenoy**

- [Profile](https://github.com/sachinshenoy "Sachin Shenoy")


## 🤝 Support

Give a ⭐️ if you like this project!
