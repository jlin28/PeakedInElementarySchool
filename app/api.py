import urllib.request
import json
import random
from pprint import pprint
from db import add_film

#setup

OMDB_KEY = ""
SPANISH_ENGLISH_KEY = ""
SUPERHERO_KEY = ""
THESAURUS_KEY = ""

RICK_AND_MORTY_URL = "https://rickandmortyapi.com/api"
COUNTRIES_URL = "https://restcountries.com/v3.1/capital/all"

#gives a random set of data for specific api
def apiCall(api):
    global OMDB_KEY
    global SPANISH_ENGLISH_KEY
    global SUPERHERO_KEY
    global THESAURUS_KEY
    if api == "film":
        with open("keys/key_OMDb.txt", "r") as f:
            OMDB_KEY = f.read().strip()
        data = getFilm(1)
        print("                  ")
        return data
    if api == "spanish":
        with open("keys/key_spanish_english.txt", "r") as f:
            SPANISH_ENGLISH_KEY = f.read().strip()
        data = getSpanish()
        return data[3]
    if api == "superhero":
        with open("keys/key_Superhero.txt", "r") as f:
            SUPERHERO_KEY = f.read().strip()
        url = SUPERHERO_URL = f"https://www.superheroapi.com/api.php/{SUPERHERO_KEY}/1"
    if api == "thesaurus":
        with open("keys/key_thesaurus.txt", "r") as f:
            THESAURUS_KEY = f.read().strip()
        THESAURUS_URL = f"https://dictionaryapi.com/api/v3/references/thesaurus/json/test?key={THESAURUS_KEY}"
        url = THESAURUS_URL
    if api == "rick":
        url = RICK_AND_MORTY_URL
    if api == "country":
        url = COUNTRIES_URL

    with urllib.request.urlopen(url) as response:
        raw_data = response.read()

    data = json.loads(raw_data)

    return data

def getFilm(count):
    ID = ""
    for i in range(7):
        num = random.randint(0, 9)
        ID = ID + str(num)
    if ID == "0000000":
        return getFilm()
    ID = "tt" + ID
    #ID = "tt0062873" #for manually slapping in ilms
    OMDB_URL = f"https://www.omdbapi.com/?i={ID}&apikey={OMDB_KEY}"
    with urllib.request.urlopen(OMDB_URL) as response:
        raw_data = response.read()

    data = json.loads(raw_data)
    print(data)
    if 'imdbVotes' not in data: #some ids don't work, so retry
        return getFilm(count+1)
    rating = data['imdbVotes']
    if rating == "N/A" or int(rating.replace(',','')) < 1000: #must have good enough votes or else no one will know, series can be put in if their episode votes is high enough
        return getFilm(count+1)
    type = data['Type']
    if type == "episode":
        ID = data['seriesID']
        OMDB_URL = f"https://www.omdbapi.com/?i={ID}&apikey={OMDB_KEY}"
        with urllib.request.urlopen(OMDB_URL) as response:
            raw_data = response.read()

        data = json.loads(raw_data)
        print(data)
    print(str(count) + " searched")
    return data

def getSpanish():
    SPANISH_ENGLISH_URL = f"https://dictionaryapi.com/api/v3/references/spanish/json/test?key={SPANISH_ENGLISH_KEY}"
    with urllib.request.urlopen(SPANISH_ENGLISH_URL) as response:
        raw_data = response.read()

    data = json.loads(raw_data)

    return data
