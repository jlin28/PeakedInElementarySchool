# Joyce Lin, Evan Khosh, Sean Zheng, Zixi Qiao
# PIES
# SoftDev
# P01 -- ArRESTed Development
# 12/22/25

import sqlite3
from api import apiCall
import random
from pprint import pprint

#=============================MAKE=TABLES=============================#

def make_tables():
    DB_FILE="data.db"
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS films (
            id INTEGER PRIMARY KEY NOT NULL,
            title TEXT NOT NULL,
            genre TEXT NOT NULL,
            plot TEXT NOT NULL,
            director TEXT NOT NULL,
            rating TEXT NOT NULL,
            img TEXT NOT NULL,
            released TEXT NOT NULL
        )"""
    )
    #c.execute("DROP TABLE questions") #if any issues with questions
    c.execute("""
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY NOT NULL,
            type TEXT NOT NULL,
            image TEXT,
            question TEXT NOT NULL,
            answers TEXT NOT NULL,
            correct TEXT NOT NULL
        )"""
    )
    db.commit()
    db.close()
#make_tables() #for remaking tables
#=============================QUESTIONS=============================#

#films
def add_film(data):
    DB_FILE="data.db"
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()
    count = c.execute(f'SELECT COUNT(*) FROM films')
    count = count.fetchone()[0]
    command = 'INSERT INTO films VALUES (?, ?, ?, ?, ?, ?, ?, ?)'
    vars = (count, data['Title'], data['Genre'], data['Plot'], data['Director'], data['imdbRating'], data['Poster'], data['Released'])
    c.execute(command, vars)

    db.commit()
    db.close()

def jumble_answers(answers):
    result = []
    while len(answers) > 0:
        id = random.randint(0, len(answers) - 1)
        result.append(answers[id])
        answers.pop(id)
    return result

#parameter format: question - string | type - string | answers - list of strings | correct - string | image - string
#returns id of new question
def make_question(question, type, answers, correct, image):

    DB_FILE="data.db"
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()


    id = c.execute(f'SELECT COUNT(id) FROM questions').fetchone()[0]
    #print(id)

    answers_str = '%SPLIT%'.join(answers)
    #print(answers_str)

    command = 'INSERT INTO questions VALUES (?, ?, ?, ?, ?, ?)'
    vars = (id, type, image, question, answers_str, correct)
    c.execute(command, vars)

    db.commit()
    db.close()

    return id

def create_questions(count,cache, Dtype):
    DB_FILE="data.db"
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()
    types = ["OMDB", "Spanish", "Synonyms", "RickAndMorty", "Countries"]
    if  Dtype != None:
        type = Dtype
    answers = []
    img = None
    correct = "e"
    question = "bruh"
    for i in range(count):
        if Dtype == None:
            type = types[random.randint(0,len(types) - 1)]
        if type == "OMDB":
            DorP = random.randint(0,1) #0 for director and 1 for plot question
            total = c.execute("SELECT COUNT(*) FROM films")
            total = total.fetchone()[0] - 1
            while len(answers) < 1:
                if cache == False:
                    data = apiCall("film")
                    add_film(data)
                    title = data['Title']
                    director = data['Director']
                    plot = data['Plot']
                    img = data['Poster']
                else:
                    random_id = random.randint(0,total)
                    command = ("SELECT * FROM films WHERE id = ?")
                    vars = (random_id,)
                    row = c.execute(command, vars).fetchone()
                    title = row[1]
                    director = row[4]
                    plot = row[3]
                    img = row[6]
                if DorP == 0 and director != "N/A":
                    answers.append(director)
                if DorP == 1:
                    answers.append(plot)
            while len(answers) < 4:
                random_id = random.randint(0,total)
                if DorP == 0:
                    command = "SELECT director FROM films WHERE id = ?"
                if DorP == 1:
                    command = "SELECT plot FROM films WHERE id = ?"
                vars = (random_id,)
                grabbed = c.execute(command, vars).fetchone()[0]
                if DorP == 0 and grabbed != "N/A" and grabbed not in answers:
                    answers.append(grabbed)
                if DorP == 1 and grabbed not in answers:
                    answers.append(grabbed)
            #print(answers)
            if DorP == 0:
                question = f"Who is the Director of {title}?"
                correct = director
            if DorP == 1:
                question = f"What is the Plot of {title}?"
                correct = plot
            img = None

        if type == "Spanish":
            while len(answers) < 1:
                data = apiCall("spanish")
                if len(data['shortdef']) > 0:
                    word = data['meta']['stems'][0]
                    correct = data['shortdef'][0]
                    if ':' in correct:
                        correct = correct.split(':')[1].strip()
                    if ',' in correct:
                        correct = correct.split(',')[0]
                    if '(' in correct:
                        correct = correct.split('(')[0]
                    answers.append(correct)
            while len(answers) < 4:
                data = apiCall("spanish")
                #pprint(data)
                if len(data['shortdef']) > 0:
                    sdef = data['shortdef'][0]
                    if ':' in sdef:
                        sdef = sdef.split(':')[1].strip()
                    if ',' in sdef:
                        sdef = sdef.split(',')[0]
                    if '(' in sdef:
                        sdef = sdef.split('(')[0]
                    if sdef not in answers:
                        answers.append(sdef)
            question = f"What is the Spanish Translation of {word}?"
            img = None
        #superhero is blocked off in __init__.py due to the image requiring human verification -> error loading the image
        if type == "Superhero":
            data = apiCall("superhero")
            correct = data['name']
            img = data['image']['url']
            answers.append(correct)
            while len(answers) < 4:
                data = apiCall("superhero")
                if data['name'] not in answers:
                    answers.append(data['name'])
            question = "Who is this superhero?"

        if type == "Synonyms":
            while len(answers) < 1:
                data = apiCall("thesaurus")
                if isinstance(data, dict):
                    word = data['meta']['id']
                    syns = data['meta']['syns'][0]
                    if len(syns) > 0:
                        correct = data['meta']['syns'][0][random.randint(0, len(syns) - 1)]
                        answers.append(correct)
            while len(answers) < 4:
                data = apiCall("thesaurus")
                if isinstance(data, dict):
                    syns = data['meta']['syns'][0]
                    synonym = data['meta']['syns'][0][random.randint(0, len(syns) - 1)]
                    if len(syns) > 0 and synonym not in answers:
                        answers.append(synonym)
            img = None
            question = f"Which of the following is a synonym for {word}?"

        if type == "RickAndMorty":
            data = apiCall("rick")
            #pprint(data)
            correct = data['name']
            img = data['image']
            answers.append(correct)
            while len(answers) < 4:
                data = apiCall("rick")
                if data['name'] not in answers:
                    answers.append(data['name'])
            question = "Who is this character from Rick and Morty?"

        if type == "Countries":
            CorF = random.randint(0,1) #0 for capital and 1 for flag question
            data = apiCall("country")[0]
            img = data['flags']['png']
            name = data['name']['common']
            if CorF == 0:
                correct = data['capital'][0]
                question = f"What is the capital of {name}?"
            if CorF == 1:
                correct = name
                question = f"What country is this?"
            answers.append(correct)
            while len(answers) < 4:
                data = apiCall("country")[0]
                if CorF == 0 and data['capital'][0] not in answers:
                    answers.append(data['capital'][0])
                if CorF == 1 and data['name']['common'] not in answers:
                    answers.append(data['name']['common'])

        make_question(question, type, jumble_answers(answers), correct, img)
    db.commit()
    db.close()

#create_questions(1000, True, None) #to create questions
#add_film(apiCall("film"))

# game
def create_game_data():

    DB_FILE="data.db"
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()

    c.execute("DROP TABLE IF EXISTS game")

    c.execute("""
        CREATE TABLE game (
            turn INTEGER PRIMARY KEY NOT NULL,
            board TEXT NOT NULL
        )"""
    )

    db.commit()
    db.close()

#return format: [[id], [type], [image], [question], [answers], [correct]]
def get_question(id):

    DB_FILE="data.db"
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()

    command = 'SELECT * FROM questions WHERE id = ?'
    vars = (id,)
    data = c.execute(command, vars).fetchone()

    question = []
    for item in data:
        question += [[item]]

    question[4] = question[4][0].split("%SPLIT%")

    db.commit()
    db.close()

    return question

#return format: [[id], [type], [image], [question], [answers], [correct]]
def get_random_question(type):

    DB_FILE="data.db"
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()

    command = 'SELECT id FROM questions WHERE type = ?'
    vars = (type,)
    ids = c.execute(command, vars).fetchall()
    id = random.choice(ids)[0]

    db.commit()
    db.close()

    return get_question(id)
#print(get_random_question())

def get_latest_id():
    DB_FILE="data.db"
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()

    count = c.execute(f'SELECT COUNT(id) FROM questions').fetchone()[0]

    db.commit()
    db.close()

    return count-1
#=============================GAME=============================#


#parameter format: turn - int (0 is starting positions) | board - 2-D array
def make_board_state(turn, board):

    DB_FILE="data.db"
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()

    board_rows = []
    for row in board:
        board_rows.append("%COL%".join(map(str, row)))
    board_str = "%ROW%".join(board_rows)

    command = 'INSERT INTO game VALUES (?, ?)'
    vars = (turn, board_str)
    c.execute(command, vars)

    db.commit()
    db.close()


#parameter format: board - 2-D array
def add_board_state(board):

    DB_FILE="data.db"
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()

    turn = c.execute('SELECT COUNT(turn) FROM game').fetchone()[0] + 1

    db.commit()
    db.close()

    make_board_state(turn, board)


#return format: 2-D array
def get_board_state(turn):

    DB_FILE="data.db"
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()

    command = 'SELECT board FROM game WHERE turn = ?'
    vars = (str(turn),)
    board_str = c.execute(command, vars).fetchone()[0]

    board = []
    board_rows = board_str.split("%ROW%")
    for row in board_rows:
        board.append(list(map(int, row.split("%COL%"))))

    db.commit()
    db.close()

    return board
