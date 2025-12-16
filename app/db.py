# Joyce Lin, Evan Khosh, Sean Zheng, Zixi Qiao
# PIES
# SoftDev
# P01 -- ArRESTed Development
# 12/22/25

import sqlite3
from api import apiCall
import random

#=============================MAKE=TABLES=============================#

# questions
def create_questions(count):

    DB_FILE="data.db"
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()
    #c.execute("DROP TABLE questions")
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

    types = ["film", "spanish", "superhero", "thesaurus", "rick", "country"]
    type = random.randint(len(types))
    type = "film"
    for i in range(count):
        if type == "film":
            data = apiCall(type)
            add_film(data)
            #make_question(f"Who directed {data['Title']}?", answers, data['Director'], null)

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


#=============================QUESTIONS=============================#


#return format: [[question], [answers], [correct], [image]]
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

    question[1] = question[1][0].split("%SPLIT%")

    db.commit()
    db.close()

    return question


#return format: [[question], [answers], [correct], [image]]
def get_random_question():

    DB_FILE="data.db"
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()

    count = c.execute(f'SELECT COUNT(id) FROM questions')
    id = randint(1, count)

    db.commit()
    db.close()

    return get_question(id)


#parameter format: question - string | answers - list of strings | correct - string | image - string
#returns id of new question
def make_question(question, answers, correct, image):

    DB_FILE="data.db"
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()


    id = c.execute(f'SELECT COUNT(id) FROM questions')

    answers_str = '%SPLIT%'.join(answers)

    command = 'INSERT INTO questions VALUES (?, ?, ?, ?)'
    vars = (id, type, image, question, answers_str, correct)
    c.execute(command, vars)

    db.commit()
    db.close()

    return id

#=============================API DATA=============================#

def add_film(data):
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
            released TEXT NOT NULL
        )"""
    )

    count = c.execute(f'SELECT COUNT(*) FROM films')
    count = count.fetchone()[0]
    command = 'INSERT INTO films VALUES (?, ?, ?, ?, ?, ?, ?)'
    vars = (count, data['Title'], data['Genre'], data['Plot'], data['Director'], data['imdbRating'], data['Released'])
    c.execute(command, vars)

    db.commit()
    db.close()

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
