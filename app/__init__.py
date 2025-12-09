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
        session.clear()
        for x,y in request.form.to_dict().items():
            session[x] = y;

    #    create_questions()
    #    create_game_data()

        # return redirect(url_for('game'))

    # SETS PREVIOUS SETTINGS
    if 'difficulty' in session:
        difficulties[int(session['difficulty'])] = 'checked'
    else: difficulties[0] = 'checked'
    if 'setting1' in session:
        setting1='checked'
    if 'setting2' in session:
        setting2='checked'

    return render_template('menu.html',
                            dEasy = difficulties[0],
                            dMed = difficulties[1],
                            dHard = difficulties[2],
                            placeholder1=setting1,
                            placeholder2=setting2)

@app.route('/game', methods=['GET', 'POST'])
def game():
    board = [[-1,-2,-3,-4,-5,-3,-2,-1],
            [-6,-6,-6,-6,-6,-6,-6,-6],
            [0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0],
            [6,6,6,6,6,6,6,6],
            [1,2,3,4,5,3,2,1]]
    #if not 'turns' in session:
    #    session['turns'] = 1;
    #else:
    #    session['turns'] = session['turns'] + 1
    return render_template('game.html',
                            #board=get_board_state(session['turns'])
                            board = board,
                            pieces = ['rook', 'knight', 'bishop', 'queen', 'king','pawn'],
                            gridlabel = ['a','b','c','d','e','f','g','h']
                        )

# RUN FLASK
if __name__=='__main__':
    app.debug = True
    app.run()
