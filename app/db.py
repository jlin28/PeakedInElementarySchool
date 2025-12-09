# Joyce Lin, Evan Khosh, Sean Zheng, Zixi Qiao
# PIES
# SoftDev
# P01 -- ArRESTed Development
# 12/22/25

import sqlite3

#=============================MAKE=TABLES=============================#


# questions
def create_questions():

    DB_FILE="data.db"
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY NOT NULL,
            image TEXT,
            question TEXT NOT NULL,
            answers TEXT NOT NULL,
            correct TEXT NOT NULL
        )"""
    )

    db.commit()
    db.close()


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

    command = 'SELECT ALL FROM questions WHERE id = ?'
    vars = (id)
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
    vars = (id, answers_str, correct, image)
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

    board_str = "["
    for row in board:
        board_str += "[[" + "], [".join(row) + "]], "
    board_str = board_str[0:-2] + "]"

    command = 'INSERT INTO game VALUES (?, ?)'
    vars = (turn, board_str)
    c.execute(command, vars)

    db.commit()
    db.close()


#parameter format: board - 2-D array
def make_board_state(board):

    DB_FILE="data.db"
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()

    turn = c.execute(f'SELECT COUNT(turn) FROM questions')

    db.commit()
    db.close()

    make_board_state(turn, board)


#return format: 2-D array
def get_board_state(turn):

    DB_FILE="data.db"
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()

    command = 'SELECT ALL FROM questions WHERE id = ?'
    vars = (id)
    board_str = c.execute(command, vars).fetchone()[0]

    board = [
        [board_str[2, 24].split(", ")],
        [board_str[28, 50].split(", ")],
        [board_str[54, 76].split(", ")],
        [board_str[80, 102].split(", ")],
        [board_str[106, 128].split(", ")],
        [board_str[132, 154].split(", ")],
        [board_str[158, 180].split(", ")],
        [board_str[184, 206].split(", ")],
    ]

    db.commit()
    db.close()

    return board
