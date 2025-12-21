# Joyce Lin, Evan Khosh, Sean Zheng, Zixi Qiao
# PIES
# SoftDev
# P01 -- ArRESTed Development
# 12/22/2025

from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import time
from db import *
from chess import *
from pprint import pprint
from random import randint

app = Flask(__name__)
app.secret_key = 'help'

@app.route('/', methods=['GET', 'POST'])
def menu():
    # SETTING TIME
    curHour = time.localtime()[3]
    if curHour >= 18: curTime = 0
    else: curTime = 1

    # ALL POSSIBLE QUESTION TYPES
    question_categories = ['OMDB', 'Countries', 'Spanish', 'Synonyms','RickAndMorty']

    # SETS DEFAULT SETTINGS
    difficulties = ['checked', '', '']
    setting1=''
    cache=''
    reverseStatus = ''
    selected_categories = []

    # CHECKS FOR PREVIOUS SETTINGS
    if 'categories' in session:
        if 'difficulty' in session:
            difficulties[0] = ''
            difficulties[session['difficulty']] = 'checked'

        if 'setting1' in session:
            setting1 = 'checked'

        if 'setting2' in session:
            cache = 'checked'

        if 'reverseTime' in session:
            reverseStatus = 'checked'

        selected_categories = []

    # CREATES NEW GAME
    if request.method == 'POST':
        session.clear()
        print(request.form)
        data = request.form

        # ADDS SETTINGS TO SESSION
        if 'difficulty' in data:
            session['difficulty'] = int(data['difficulty'])

        if 'setting1' in data:
            session['setting1'] = 'checked'

        if 'cache' in data:
            session['cache'] = 'checked'

        if 'reverseTime' in data:
            session['reverseTime'] = 'checked'

        for cat in question_categories:
            if cat in data:
                selected_categories.append(cat)
        session['categories'] = selected_categories.copy()
        
        if 'singleplayer' in data:
            reset_board()
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

            return redirect(url_for('game', gamemode='singleplayer', difficulty=session['difficulty']))

        if 'multiplayer' in data:
            reset_board()
            create_game_data()

            session['turns'] = 1
            add_board_state([[-1,-2,-3,-4,-5,-3,-2,-1],
                             [-6,-6,-6,-6,-6,-6,-6,-6],
                             [0 ,0,0,0,0,0,0,0],
                             [0,0,0,0,0,0,0,0],
                             [0,0,0,0,0,0,0,0],
                             [0,0,0,0,0,0,0,0],
                             [6,6,6,6,6,6,6,6],
                             [1,2,3,4,5,3,2,1]])

            return redirect(url_for('game', gamemode='multiplayer', difficulty=session['difficulty']))

    return render_template('menu.html',
                            time = curTime,
                            reverseStatus = reverseStatus,
                            dEasy = difficulties[0],
                            dMed = difficulties[1],
                            dHard = difficulties[2],
                            placeholder1=setting1,
                            quickload=cache,
                            categories=question_categories,
                            selected=selected_categories)

@app.route('/game/<string:gamemode>/<int:difficulty>', methods=['GET', 'POST'])
def game(gamemode, difficulty):
    turn = session['turns']
    current_pos = get_board_state(turn)

    gridlabel = ['a','b','c','d','e','f','g','h']

    cache = 'cache' in session
    selected_categories = session['categories'].copy()
    timeMode = 10 + ((2-difficulty)*20)

    if request.method == 'POST':
        data = request.headers

        #CHECK
        if 'check' in data:
            board = get_board_state(turn)
            if turn % 2 != 0:
                color = 'white'
            if turn % 2 == 0:
                color = 'black'

            incheckmate = in_checkmate(get_board_state(turn), color)

            if not in_check(board, color):
                return ""
            elif incheckmate[0] and gamemode != 'singleplayer':
                return 'checkmate'
            else:
                return color

        #SELECT
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

        #MOVE
        if 'move' in data:
            positions = data['move'].split("+")

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
                return redirect(url_for('result', winner=gameover[1], totalturns=turn))

            #SINGLEPLAYER
            if gamemode == 'singleplayer':
                session['turns'] = session['turns'] + 1
                turn += 1

                if turn % 2 == 0:
                    color = 'black'
                    color_to_move = 'white'
                    bot_move = bot_move(get_display_board(get_internal_board()), color)
                    newBoard = simulate_move(get_display_board(get_internal_board()),
                        bot_move[0], bot_move[1],
                        bot_move[2], bot_move[3],
                        None,
                        castling_state
                    )[0]
                else:
                    color = 'white'
                    color_to_move = 'black'
                    bot_move = bot_move(get_display_board(get_internal_board()), color)
                    newBoard = simulate_move(get_display_board(get_internal_board()),
                        bot_move[0], bot_move[1],
                        bot_move[2], bot_move[3],
                        None,
                        castling_state
                    )[0]

                set_board(newBoard)

                make_board_state(turn, get_display_board(newBoard, color))

                gameover = game_over(get_board_state(turn), color_to_move)
                if gameover[0]:
                    return redirect(url_for('result', winner=game_over[1], totalturns=turn))

                incheckmate = in_checkmate(get_board_state(turn), color_to_move)
                if incheckmate[0]:
                    return get_board_state(turn) #tell them theyre in checkmate somehow

            print(get_board_state(turn))
            return get_board_state(turn)

        if 'skip' in data:
            session['turns'] = session['turns'] + 1
            turn += 1

            if turn % 2 == 0:
                color = 'black'
            else:
                color = 'white'

            make_board_state(turn, get_display_board(get_internal_board(), color))

            if gamemode == 'singleplayer':
                session['turns'] = session['turns'] + 1
                turn += 1

                if gamemode == 0:
                    chance = 65
                elif gamemode == 1:
                    chance = 80
                else:
                    chance = 95

                if randint(0, 99) < chance:
                    if turn % 2 == 0:
                        color = 'black'
                        color_to_move = 'white'
                        bot_move = bot_move(get_display_board(get_internal_board()), color)
                        newBoard = simulate_move(get_display_board(get_internal_board()),
                            bot_move[0], bot_move[1],
                            bot_move[2], bot_move[3],
                            None,
                            castling_state
                        )[0]
                    else:
                        color = 'white'
                        color_to_move = 'black'
                        bot_move = bot_move(get_display_board(get_internal_board()), color)
                        newBoard = simulate_move(get_display_board(get_internal_board()),
                            bot_move[0], bot_move[1],
                            bot_move[2], bot_move[3],
                            None,
                            castling_state
                        )[0]

                    set_board(newBoard)

                    make_board_state(turn, get_display_board(newBoard, color))

                    gameover = game_over(get_board_state(turn), color_to_move)
                    if gameover[0]:
                        return redirect(url_for('result', winner=game_over[1], totalturns=turn))

                    incheckmate = in_checkmate(get_board_state(turn), color_to_move)
                    if incheckmate[0]:
                        return get_board_state(turn) #tell them theyre in checkmate somehow
                else:
                    if turn % 2 == 0:
                        color = 'black'
                    else:
                        color = 'white'

                    make_board_state(turn, get_display_board(get_internal_board(), color))

            return get_board_state(turn)

        if 'trivia' in data:
            cat = random.choice(selected_categories)
            if (cache):
                return get_random_question(cat)
            else:
                try:
                    print('category:')
                    print(cat)
                    create_questions(1, True, cat)
                    return get_question(get_latest_id())
                except Exception:
                    print("Error Found")
                    return get_random_question(cat)

        if 'remove' in data:
            position = data['remove']
            print(position)

            if turn % 2 != 0:
                remove_piece(int(position[1]), gridlabel.index(position[0]))
            else:
                remove_piece(7-int(position[1]), 7-gridlabel.index(position[0]))
            print('remove:')
            print(str(7-int(position[1])) + "," + str(7-gridlabel.index(position[0])))
            print(get_internal_board())


    return render_template('game.html',
                                board = get_board_state(turn),
                                turn = turn,
                                timeMode = timeMode,
                          )

@app.route('/result/<string:winner>/<int:totalturns>', methods=['GET', 'POST'])
def result(winner, totalturns):
    maxTurns = totalturns

    if request.method == 'POST':
        data = request.headers
        turn = int(data['turn'])

        if 'direction' in data:
            if data['direction'] == 'next':
                turn += 1
            return get_board_state(turn)

        if 'previous_board' in data:
            if data['direction'] == 'prev':
                turn -= 1
            return get_board_state(turn)

        if 'restart' in request.form:
            return redirect(url_for('menu'))

    return render_template('result.html',
                            winner = winner,
                            board = get_board_state(1),
                            maxTurns = maxTurns
                        )

@app.route('/error')
def error():
    #just to initialize the error handling part (we can polish it up later)
    return "oopsies, we had an error :C"

# RUN FLASK
if __name__=='__main__':
    app.debug = True
    app.run()
