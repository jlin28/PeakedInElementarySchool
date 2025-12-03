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
