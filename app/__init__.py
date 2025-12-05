# Joyce Lin, Evan Khosh, Sean Zheng, Zixi Qiao
# PIES
# SoftDev
# P01 -- ArRESTed Development
# TBD

from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from db import *

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def menu():

    if 'submit' in request.form:
        create_questions()
        create_game_data()

        return redirect(url_for('game'))

    return render_template('menu.html')

@app.route('/game', methods=['GET', 'POST'])
def game():

    return render_template('game.html')

# RUN FLASK
if __name__=='__main__':
    app.debug = True
    app.run()
