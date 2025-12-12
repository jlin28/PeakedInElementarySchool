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
# from api import apiCall

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

            session['turns'] = 1
            add_board_state([[-1,-2,-3,-4,-5,-3,-2,-1],
                             [-6,-6,-6,-6,-6,-6,-6,-6],
                             [0,0,0,0,0,0,0,0],
                             [0,0,0,0,0,0,0,0],
                             [0,0,0,0,0,0,0,0],
                             [0,0,0,0,0,0,0,0],
                             [6,6,6,6,6,6,6,6],
                             [1,2,3,4,5,3,2,1]])

            return redirect(url_for('game', gamemode='singleplayer', difficulty=difficulties.index('checked')))

        if 'multiplayer' in request.form:
            create_questions()
            create_game_data()

            session['turns'] = 1
            add_board_state([[-1,-2,-3,-4,-5,-3,-2,-1],
                             [-6,-6,-6,-6,-6,-6,-6,-6],
                             [0,0,0,0,0,0,0,0],
                             [0,0,0,0,0,0,0,0],
                             [0,0,0,0,0,0,0,0],
                             [0,0,0,0,0,0,0,0],
                             [6,6,6,6,6,6,6,6],
                             [1,2,3,4,5,3,2,1]])

            return redirect(url_for('game', gamemode='multiplayer', difficulty=difficulties.index('checked')))

    return render_template('menu.html',
                            dEasy = difficulties[0],
                            dMed = difficulties[1],
                            dHard = difficulties[2],
                            placeholder1=setting1,
                            placeholder2=setting2)

@app.route('/game/<string:gamemode>/<int:difficulty>', methods=['GET', 'POST'])
def game(gamemode, difficulty):

    global current_pos

    turn = session['turns']
    current_pos = get_board_state(turn)

    if session['turns'] % 2 != 0:
       player = 'white'
    else:
       player = 'black'

    gridlabel = ['a','b','c','d','e','f','g','h']

    if request.method == 'POST':
        data = request.headers

        if 'select' in data:
            validarr = ""
            position = [gridlabel.index(data['select'][0]), int(data['select'][1])]
            for x,y in legal_squares(current_pos, position[1], position[0], en_passant):
                validarr = validarr + ',' + gridlabel[y]+str(x)
            return validarr[1:]

        if 'move' in data:
            positions = data['move'].split("+");

            session['turns'] = session['turns'] + 1
            turn += 1
            print(positions) # testing purposes

            current_pos = simulate_move(current_pos,
                            int(positions[0][1]), gridlabel.index(positions[0][0]),
                            int(positions[1][1]), gridlabel.index(positions[1][0]),
                            None,
                            castling_state
                          )[0]
            flip_board()
            add_board_state(current_pos)

    print(current_pos)
    return render_template('game.html',
                                board = current_pos,
                                player = player,
                          )

@app.route('/test', methods=['GET', 'POST'])
def testError():

    ######### FOR ERROR HANDLING TESTING PURPOSES ####################
    try:
        data = apiCall("film")
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
