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

    c.execute("""
        CREATE TABLE IF NOT EXISTS game (
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
