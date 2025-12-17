# Joyce Lin, Evan Khosh, Sean Zheng, Zixi Qiao
# PIES
# SoftDev
# P01 -- ArRESTed Development
# TBD

from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import time
from db import *
from chess import *
from pprint import pprint
# from api import apiCall

app = Flask(__name__)
app.secret_key = 'help'

@app.route('/', methods=['GET', 'POST'])
def menu():
    # SETTING TIME
    curHour = time.localtime()[3]
    if curHour >= 18: curTime = 0
    else: curTime = 1

    # ALL POSSIBLE QUESTION TYPES
    question_categories = ['movies', 'countries', 'spanish', 'superheroes']
    difficulty_types = ['easy', 'medium', 'hard']

    # SETS DEFAULT SETTINGS
    difficulties = ['checked', '', '']
    setting1=''
    setting2=''
    reverseStatus = ''
    selected_categories = []

    # CHECKS FOR PREVIOUS SETTINGS
    if 'categories' in session:
        if 'difficulty' in session:
            difficulties[0] = ''
            difficulties[difficulty_types.index(session['difficulty'])] = 'checked'

        if 'setting1' in session:
            setting1 = 'checked'

        if 'setting2' in session:
            setting2 = 'checked'

        if 'reverseTime' in session:
            reverseStatus = 'checked'

        selected_categories = session['categories'].copy()

    # CREATES NEW GAME
    if request.method == 'POST':
        session.clear()
        data = request.form

        # ADDS SETTINGS TO SESSION
        if 'difficulty' in data:
            session['difficulty'] = difficulty_types[0]

        if 'setting1' in data:
            session['setting1'] = 'checked'

        if 'setting2' in data:
            session['setting2'] = 'checked'

        if 'reverseTime' in data:
            session['reverseTime'] = 'checked'

        for cat in question_categories:
            if cat in data:
                selected_categories.append(cat)
        session['categories'] = selected_categories.copy()

        if 'singleplayer' in data:
            reset_board()
            # create_questions()
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

        if 'multiplayer' in data:
            reset_board()
            # create_questions()
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
                            time = curTime,
                            reverseStatus = reverseStatus,
                            dEasy = difficulties[0],
                            dMed = difficulties[1],
                            dHard = difficulties[2],
                            placeholder1=setting1,
                            placeholder2=setting2,
                            categories=question_categories,
                            selected=selected_categories)

@app.route('/game/<string:gamemode>/<int:difficulty>', methods=['GET', 'POST'])
def game(gamemode, difficulty):

    turn = session['turns']
    current_pos = get_board_state(turn)

    gridlabel = ['a','b','c','d','e','f','g','h']

    if request.method == 'POST':
        data = request.headers

        if 'select' in data:
            validarr = ""
            position = [gridlabel.index(data['select'][0]), int(data['select'][1])]
            if turn % 2 == 0:
                position[0] = 7 - position[0]
                position[1] = 7 - position[1]

            for x,y in legal_squares(get_display_board(get_internal_board()), position[1], position[0], en_passant):
                if turn % 2 != 0:
                    validarr = validarr + ',' + gridlabel[y]+str(x)
                else:
                    validarr = validarr + ',' + gridlabel[7-y]+str(7-x)
            return validarr[1:]

        if 'move' in data:
            positions = data['move'].split("+");

            session['turns'] = session['turns'] + 1
            turn += 1

            color = ''
            color_to_move = ''

            if turn % 2 == 0:
                color = 'black'
                color_to_move = 'white'
                newBoard = simulate_move(get_display_board(get_internal_board()),
                    int(positions[0][1]), gridlabel.index(positions[0][0]),
                    int(positions[1][1]), gridlabel.index(positions[1][0]),
                    None,
                    castling_state
                )[0]
            else:
                color = 'white'
                color_to_move = 'black'
                newBoard = simulate_move(get_display_board(get_internal_board()),
                    7-int(positions[0][1]), 7-gridlabel.index(positions[0][0]),
                    7-int(positions[1][1]), 7-gridlabel.index(positions[1][0]),
                    None,
                    castling_state
                )[0]

            set_board(newBoard)

            make_board_state(turn, get_display_board(newBoard, color))

            gameover = game_over(get_board_state(turn), color_to_move)
            if gameover[0]:
                return redirect(url_for('result', winner=game_over[1]))

            incheckmate = in_checkmate(get_board_state(turn), color_to_move)
            if incheckmate[0]:
                return get_board_state(turn) #tell them theyre in checkmate somehow

            return get_board_state(turn)

    return render_template('game.html',
                                board = get_board_state(turn),
                                turn = turn,
                          )

@app.route('/result/<string:winner>', methods=['GET', 'POST'])
def result(winner):

    turn = 0

    if request.method == 'POST':
        data = request.form

        if 'next_board' in data:
            turn += 1

            return get_board_state(turn)

        if 'previous_board' in data:
            turn -= 1

            return get_board_state(turn)

        if 'play' in data:

            return redirect(url_for('menu'))

    return render_template('result.html',
                            winner = winner,
                            board = get_board_state(turn)
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
