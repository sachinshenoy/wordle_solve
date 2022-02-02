# Wordle_Solve

Wordle_Solve is a script written in Python using the selenium module and RapidAPI (WordsAPI) service to try and solve the daily Wordle puzzle by taking control of the browser instance on your system. This has only been tested on Windows 10.

## Links

- [Repo](https://github.com/sachinshenoy/wordle_solve "<Wordle Solver> Repo")


## Screenshot

![Main Script](/screenshots/1.png "Main Script")



## Built With

- Requests
- Rich
- Selenium
- Python-Dotenv
- Chromium WebDriver

## Installation

- Clone the Repo
- Sign up for [RapidAPI](https://rapidapi.com/dpventures/api/wordsapi/pricing) Key by subscribing to [WordsAPI](https://www.wordsapi.com/) plan.
- Update the .env file with the API_KEY (Example file provided. DO NOT USE Quotes Around the Key string)
- Use the package manager [pip](https://pip.pypa.io/en/stable/) to install the dependencies.
- Download the appropriate [ChromeDriver](https://chromedriver.chromium.org/downloads) for the your version of Chrome Browser.


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

- [ ] Optimized Wait timers.
- [ ] Move the console messages to Logs.
- [ ] Fewer API Calls.
- [ ] Pick different Starting words.

## License
[MIT](https://choosealicense.com/licenses/mit/)

## Author

**Sachin Shenoy**

- [Profile](https://github.com/sachinshenoy "Sachin Shenoy")


## 🤝 Support

Give a ⭐️ if you like this project!
