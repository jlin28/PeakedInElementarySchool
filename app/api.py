# Joyce Lin, Evan Khosh, Sean Zheng, Zixi Qiao
# PIES
# SoftDev
# P01 -- ArRESTed Development
# 12/22/2025

import urllib.request
import json
from pprint import pprint
import random
from chess import *

#setup

with open("static/words/spanish.txt", "r") as file:
    spanish_words = file.read().split(",")

with open("static/words/thesaurus.txt", "r") as file:
    thesaurus_words = file.read().split(",")

with open("static/words/countries.txt", "r") as file:
    countries = file.read().split(",")


OMDB_KEY = ""
SPANISH_ENGLISH_KEY = ""
SUPERHERO_KEY = ""
THESAURUS_KEY = ""
RICK_AND_MORTY_URL = "https://rickandmortyapi.com/api"
COUNTRIES_URL = "https://restcountries.com/v3.1/capital/all"
CHESS_ENGINE_URL = "https://chess-api.com/v1"

#gives a random set of data for specific api
def apiCall(api, color_to_move=None, difficulty=None):
    global OMDB_KEY
    global SPANISH_ENGLISH_KEY
    global SUPERHERO_KEY
    global THESAURUS_KEY
    if api == "film":
        with open("keys/key_OMDb.txt", "r") as f:
            OMDB_KEY = f.read().strip()
        data = getFilm(1)
        return data
    if api == "spanish":
        with open("keys/key_spanish_english.txt", "r") as f:
            SPANISH_ENGLISH_KEY = f.read().strip()
        data = getSpanish()
        return data
    if api == "superhero":
        with open("keys/key_Superhero.txt", "r") as f:
            SUPERHERO_KEY = f.read().strip()
        data = getHero()
        return data
    if api == "thesaurus":
        with open("keys/key_thesaurus.txt", "r") as f:
            THESAURUS_KEY = f.read().strip()
        data = getThesaurus()
        return data
    if api == "rick":
        return getPickle()
    if api == "country":
        return getCountry()
    if api == "chess":
        # MAKE SURE COLOR_TO_MOVE AND DIFFICULTY ARE NOT NONE
        return getNextMove(board_to_fen(get_internal_board(), color_to_move, castling_state, en_passant), difficulty)
    raise ParameterError("wrong parameter used")
    return ""

def getFilm(count):
    ID = ""
    for i in range(7):
        num = random.randint(0, 9)
        ID = ID + str(num)
    if ID == "0000000":
        return getFilm(count+1)
    ID = "tt" + ID
    #ID = "tt0062873" #for manually slapping in ilms
    OMDB_URL = f"https://www.omdbapi.com/?i={ID}&apikey={OMDB_KEY}"
    with urllib.request.urlopen(OMDB_URL) as response:
        raw_data = response.read()

    data = json.loads(raw_data)
    #print(data)
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
        #print(data)
    #print(str(count) + " searched")
    return data

def getSpanish():
    ID = random.randint(0,len(spanish_words) - 1)
    random_word = spanish_words[ID].strip()
    #print(random_word)
    SPANISH_ENGLISH_URL = f"https://dictionaryapi.com/api/v3/references/spanish/json/{random_word}?key={SPANISH_ENGLISH_KEY}"
    with urllib.request.urlopen(SPANISH_ENGLISH_URL) as response:
        raw_data = response.read()

    data = json.loads(raw_data)

    return data[0]

def getThesaurus():
    ID = random.randint(0,len(thesaurus_words) - 1)
    random_word = thesaurus_words[ID].strip()
    THESAURUS_URL = f"https://dictionaryapi.com/api/v3/references/thesaurus/json/{random_word}?key={THESAURUS_KEY}"
    with urllib.request.urlopen(THESAURUS_URL) as response:
        raw_data = response.read()

    data = json.loads(raw_data)
    return data[0]

def getHero():
    ID = random.randint(0,731)
    SUPERHERO_URL = f"https://www.superheroapi.com/api.php/{SUPERHERO_KEY}/{ID}"
    with urllib.request.urlopen(SUPERHERO_URL) as response:
        raw_data = response.read()
    data = json.loads(raw_data)
    return data

def getPickle():
    ID = random.randint(0,826)
    RICK_URL = f"https://rickandmortyapi.com/api/character/{ID}"
    with urllib.request.urlopen(RICK_URL) as response:
        raw_data = response.read()
    data = json.loads(raw_data)
    return data

def getCountry():
    ID = random.randint(0, len(countries) - 1)
    random_country = countries[ID].strip().replace(" ", "%20") #replace is for countries with spaces like South Korea
    #print(random_country)
    COUNTRY_URL = f"https://restcountries.com/v3.1/name/{random_country}"
    with urllib.request.urlopen(COUNTRY_URL) as response:
        raw_data = response.read()
    data = json.loads(raw_data)
    return data

def getNextMove(fen, difficulty):
    depth = 5
    if difficulty == "Easy":
        depth = 3
    elif difficulty == "Medium":
        depth = 5
    elif difficulty == "Hard":
        depth = 7
    data_dict = {
        "fen": fen,
        "depth": depth
    }

    data = json.dumps(data_dict).encode("utf-8")

    req = urllib.request.Request(
        CHESS_ENGINE_URL,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    with urllib.request.urlopen(req) as response:
        raw = response.read()

    move_list = json.loads(raw).get("text").split()

    start_square = move_list[1]
    r1 = -int(start_square[1]) + 8
    c1 = start_square[0]
    c1 = ord(c1) - 97 # convert from letter column to number index
    end_square = move_list[3]
    r2 = -int(end_square[1]) + 8
    c2 = end_square[0]
    c2 = ord(c2) - 97
    promotion_piece = None
    if len(move_list[4]) > 5 and move_list[4][2].isdigit():
        promotion_piece = move_list[4][4]
    return r1, c1, r2, c2, promotion_piece
