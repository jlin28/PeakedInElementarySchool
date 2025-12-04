import urllib.request
import json

#setup
with open("keys/key_MoviesAPI.txt", "r") as f:
    MOVIE_KEY = f.read().strip()

with open("keys/key_spanish_english.txt", "r") as f:
    SPANISH_ENGLISH_KEY = f.read().strip()

with open("keys/key_SuperheroAPI.txt", "r") as f:
    SUPERHERO_KEY = f.read().strip()

with open("keys/key_thesaurus.txt", "r") as f:
    THESAURUS_KEY = f.read().strip()

MOVIE_URL = f"https://www.omdbapi.com/?i=tt3896198&apikey={MOVIE_KEY}"
SPANISH_ENGLISH_URL = f"https://dictionaryapi.com/api/v3/references/spanish/json/test?key={SPANISH_ENGLISH_KEY}"
SUPERHERO_URL = f"https://www.superheroapi.com/api.php/{SUPERHERO_KEY}/1"
THESAURUS_URL = f"https://dictionaryapi.com/api/v3/references/thesaurus/json/test?key={THESAURUS_KEY}"
RICK_AND_MORTY_URL = "https://rickandmortyapi.com/api"
COUNTRIES_URL = "https://restcountries.com/v3.1/capital/"

def apiCall(api):
    if api == "movie":
        url = MOVIE_URL
    if api == "spanish":
        url = SPANISH_ENGLISH_URL
    if api = "superhero":
        url = SUPERHERO_URL

    with urllib.request.urlopen(url) as response:
        raw_data = response.read()

    data = json.loads(raw_data)

    return data

print(apiCall("movie"))
