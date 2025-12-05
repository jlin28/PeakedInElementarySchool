# Joyce Lin, Evan Khosh, Sean Zheng, Zixi Qiao
# PIES
# SoftDev
# P01 -- ArRESTed Development
# 12/22/25

import sqlite

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

    data = c.execute(f'SELECT ALL FROM questions WHERE id = "{id}"').fetchone()

    question = []
    for item in data:
        question += [[item]]

    question[1] = question[1][0].split("%SPLIT%")

    db.commit()
    db.close()

    return question


#parameter format: question - string | answers - list of strings | correct - string | image - string
#returns id of new question
def make_question(question, answers, correct, image):

    DB_FILE="data.db"
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()

    id = c.execute(f'SELECT COUNT(id) FROM questions')

    answers_str = '%SPLIT%'.join(answers)

    c.execute(f'INSERT INTO questions VALUES ("{id}", "{answers_str}", "{correct}", "{image}")')

    db.commit()
    db.close()

    return id


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

    c.execute(f'INSERT INTO game VALUES ("{turn}", "{board_str}"')

    db.commit()
    db.close()


#return format: 2-D array
def get_board_state(turn):

    DB_FILE="data.db"
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()

    board_str = c.execute(f'SELECT ALL FROM questions WHERE id = "{id}"').fetchone()[0]

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