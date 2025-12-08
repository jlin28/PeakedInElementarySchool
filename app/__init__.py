# Joyce Lin, Evan Khosh, Sean Zheng, Zixi Qiao
# PIES
# SoftDev
# P01 -- ArRESTed Development
# TBD

from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from datetime import time
from db import *

app = Flask(__name__)
app.secret_key = 'help'

@app.route('/', methods=['GET', 'POST'])
def menu():
    print(request.form) # for testing purposes

    # SETS DEFAULT SETTINGS
    difficulties = ['', '', '']
    setting1=''
    setting2=''

    if request.method == 'POST':
        # ADDS SETTINGS TO SESSION
        if 'difficulty' in request.form:
            difficulties[int(request.form['difficulty'])] = 'checked'
        else: difficulties[0] = 'checked'

        if 'setting1' in request.form:
            setting1='checked'

        if 'setting2' in request.form:
            setting2='checked'

        if 'singleplayer' in request.form:
            create_questions()
            create_game_data()

            return redirect(url_for('game', gamemode='singleplayer', difficulty=difficulties.index('checked')))

        if 'singleplayer' in request.form:
            create_questions()
            create_game_data()

            return redirect(url_for('game', gamemode='multiplayer', difficulty=difficulties.index('checked')))

    return render_template('menu.html',
                            dEasy = difficulties[0],
                            dMed = difficulties[1],
                            dHard = difficulties[2],
                            placeholder1=setting1,
                            placeholder2=setting2)

@app.route('/game/<string:gamemode>/<int:difficulty>', methods=['GET', 'POST'])
def game(gamemode, difficulty):

    return render_template('game.html')

# RUN FLASK
if __name__=='__main__':
    app.debug = True
    app.run()
