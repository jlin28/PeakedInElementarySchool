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
from api import apiCall

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

        if 'cache' in session:
            cache = 'checked'

        if 'reverseTime' in session:
            reverseStatus = 'checked'

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
    global en_passant, castling_state
    turn = session['turns']

    gridlabel = ['a','b','c','d','e','f','g','h']

    cache = 'cache' in session
    selected_categories = session['categories'].copy()
    timeMode = 10 + ((2-difficulty)*20)

    if request.method == 'POST':
        data = request.headers

        #CHECK
        if 'check' in data:
            board = get_internal_board()
            # In singleplayer, human is white, AI is black
            if gamemode == 'singleplayer':
                color = 'white' if turn % 2 != 0 else 'black'
            else:
                color = 'white' if turn % 2 != 0 else 'black'

            incheckmate = in_checkmate(board, color)

            if not in_check(board, color):
                return ""
            elif incheckmate[0] and gamemode != 'singleplayer':
                return 'checkmate'
            else:
                return color

        # SELECT
        if 'select' in data:
            validarr = ""
            position = [gridlabel.index(data['select'][0]), int(data['select'][1])]

            if gamemode == 'singleplayer':
                # SINGLEPLAYER: always use white's perspective
                for x,y in legal_squares(get_display_board(get_internal_board()), position[1], position[0], en_passant):
                    validarr = validarr + ',' + gridlabel[y]+str(x)
            else:
                # MULTIPLAYER
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

            if gamemode == 'singleplayer':
                # Human (white) move - use display coordinates directly
                start_x = int(positions[0][1])
                start_y = gridlabel.index(positions[0][0])
                end_x = int(positions[1][1])
                end_y = gridlabel.index(positions[1][0])

                result = simulate_move(get_internal_board(),
                    start_x, start_y,
                    end_x, end_y,
                    en_passant,
                    castling_state
                )
                newBoard = result[0]
                en_passant = result[1]
                castling_state = result[2]

                set_board(newBoard)
                session['turns'] += 1
                turn = session['turns']
                make_board_state(turn, newBoard) # Store internal board

                # Check if human won
                gameover = game_over(newBoard, 'black')
                if gameover[0]:
                    return redirect(url_for('result', winner=gameover[1], totalturns=turn))

                # AI (black) moves
                ai_move = apiCall("chess", "black", difficulty=["Easy", "Medium", "Hard"][difficulty])
                result = simulate_move(newBoard,
                    ai_move[0], ai_move[1],
                    ai_move[2], ai_move[3],
                    en_passant,
                    castling_state
                )
                ai_board = result[0]
                en_passant = result[1]
                castling_state = result[2]

                set_board(ai_board)
                session['turns'] += 1
                turn = session['turns']
                make_board_state(turn, ai_board)  # Store internal board

                # Check if AI won
                gameover = game_over(ai_board, 'white')
                if gameover[0]:
                    return redirect(url_for('result', winner=gameover[1], totalturns=turn))

                # Return display board for white
                return get_display_board(ai_board, 'white')

            else:
                # MULTIPLAYER
                if turn % 2 == 0:  # Black's turn
                    # Convert display coordinates to internal coordinates
                    start_x = 7 - int(positions[0][1])
                    start_y = 7 - gridlabel.index(positions[0][0])
                    end_x = 7 - int(positions[1][1])
                    end_y = 7 - gridlabel.index(positions[1][0])
                    color = 'black'
                    color_to_move = 'white'
                else:  # White's turn
                    start_x = int(positions[0][1])
                    start_y = gridlabel.index(positions[0][0])
                    end_x = int(positions[1][1])
                    end_y = gridlabel.index(positions[1][0])
                    color = 'white'
                    color_to_move = 'black'

                result = simulate_move(get_internal_board(),
                    start_x, start_y,
                    end_x, end_y,
                    en_passant,
                    castling_state
                )
                newBoard = result[0]
                en_passant = result[1]
                castling_state = result[2]

                set_board(newBoard)
                session['turns'] += 1
                turn = session['turns']
                make_board_state(turn, newBoard)  # Store internal board

                gameover = game_over(newBoard, color_to_move)
                if gameover[0]:
                    return redirect(url_for('result', winner=gameover[1], totalturns=turn))

                # Return display board for next player
                next_color = 'white' if turn % 2 != 0 else 'black'
                return get_display_board(newBoard, next_color)

        if 'skip' in data:
            if gamemode == 'singleplayer':
                # Human got trivia wrong, AI moves
                ai_move = apiCall("chess", "black", difficulty=["Easy", "Medium", "Hard"][difficulty])
                result = simulate_move(get_internal_board(),
                    ai_move[0], ai_move[1],
                    ai_move[2], ai_move[3],
                    en_passant,
                    castling_state
                )
                ai_board = result[0]
                en_passant = result[1]
                castling_state = result[2]

                set_board(ai_board)
                session['turns'] += 1
                turn = session['turns']
                make_board_state(turn, ai_board)

                gameover = game_over(ai_board, 'white')
                if gameover[0]:
                    return redirect(url_for('result', winner=gameover[1], totalturns=turn))

                return get_display_board(ai_board, 'white')
            else:
                # Multiplayer skip
                session['turns'] += 1
                turn = session['turns']
                next_color = 'white' if turn % 2 != 0 else 'black'
                return get_display_board(get_internal_board(), next_color)

        if 'trivia' in data:
            cat = random.choice(selected_categories)
            if cache:
                return get_random_question(cat)
            else:
                try:
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

    if gamemode == 'singleplayer':
        display_board = get_display_board(get_internal_board(), 'white')
    else:
        current_color = 'white' if turn % 2 != 0 else 'black'
        display_board = get_display_board(get_internal_board(), current_color)

    return render_template('game.html',
                                board = display_board,
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
