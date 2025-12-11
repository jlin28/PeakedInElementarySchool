# Joyce Lin, Evan Khosh, Sean Zheng, Zixi Qiao
# PIES
# SoftDev
# P01 -- ArRESTed Development
# TBD

from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from datetime import time
from db import *
from chess import *
from pprint import pprint
from api import apiCall
from db import add_film

app = Flask(__name__)
app.secret_key = 'help'

@app.route('/', methods=['GET', 'POST'])
def menu():
    print(request.form) # for testing purposes
    print(session) # for testing purposes

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

        return redirect(url_for('game'))

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
    session.clear() # testing purposes
    board = [[-1,-2,-3,-4,-5,-3,-2,-1],
            [-6,-6,-6,-6,-6,-6,-6,-6],
            [0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0],
            [6,6,6,6,6,6,6,6],
            [1,2,3,4,5,3,2,1]]
    if not 'turns' in session:
        session['turns'] = 1;
    else:
        session['turns'] = session['turns'] + 1

    turn = session['turns']
    #board = get_board_state(turn)

    if turn % 2 != 0:
       player = 'white'
    else:
       player = 'black'

    gridlabel = ['a','b','c','d','e','f','g','h']

    if request.method == 'POST':
        data = request.headers
        if 'select' in data:
            validarr = ""
            position = [gridlabel.index(data['select'][0]), int(data['select'][1])]
            for x,y in legal_squares(board, position[1], position[0], en_passant):
                validarr = validarr + ',' + gridlabel[y]+str(x)
            return validarr[1:];

    return render_template('game.html',
                            board=board,
                            player=player,
                        )

@app.route('/test', methods=['GET', 'POST'])
def testError():

    ######### FOR ERROR HANDLING TESTING PURPOSES ####################
    try:
        data = apiCall("film")
        add_film(data)
        return data
    except Exception as e:
        print(f"An unexpected error occured: {e}")
        return redirect('/error')

    ##################################################################

    return render_template('game.html')

@app.route('/error')
def error_page():
    #just to initialize the error handling part (we can polish it up later)
    return "oopsies, we had an error :C"

# RUN FLASK
if __name__=='__main__':
    app.debug = True
    app.run()
