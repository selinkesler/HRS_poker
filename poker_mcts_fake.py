"""
An example implementation of the abstract Node class for use in MCTS
If you run this file then you can play against the computer.
A tic-tac-toe board is represented as a tuple of 9 values, each either None,
True, or False, respectively meaning 'empty', 'X', and 'O'.
The board is indexed by row:
0 1 2
3 4 5
6 7 8
For example, this game board
O - X
O X -
X - -
corrresponds to this tuple:
(False, None, True, False, True, None, True, None, None)

Hands 

Name            - Probability  - Combinations - how

Royal Flush     - 1 in 649,737 - 4            - 10, 11, 12, 13, 1 (with same type)
Straight Flush  - 1 in 72,193  - 36           - 4, 5, 6, 7, 8 (5 cards in a row with same type)    
Four of a Kind  - 1 in 4,164   - 624.         - same card in all types
Full House      - 1 in 693     - 3,744.       - a pair plus three of a kind in the same hand
Flush           - 1 in 508     - 5,108.       - 5 cards same type
Straight        - 1 in 253     - 10,200       - 5 cards in numerical order (not same type)
Three of a Kind - 1 in 46      - 54,912       - three of one card and two non-paired cards
Two Pair        - 1 in 20      - 123,552.     - two different pairings or sets of the same card in one hand
One Pair        - 1 in 1.36.   - 1,098,240.   - single pairing of the same card
High Card       - 1 in 0.99    - 1,302,540    - with no matching cards

['H2' 'S2' 'C2' 'D2' 'H3']
PokerBoard(tup=(True, None, None, None, None, None, None, None, None), turn=False, winner=None, terminal=False)

PokerBoard(tup=('H2', 'S2', None, None, None, None, None), turn=False, winner=None, terminal=False)
PokerBoard(tup=('H2', 'S2', M1, M2, M3, O1, O2), turn=False, winner=None, terminal=False)

"""

from collections import namedtuple
from random import choice
from cards import CardScores
from monte_carlo_tree_search import MCTS, Node
import random

_TTTB = namedtuple("PokerBoard", "tup turn winner terminal money_machine money_middle money_opp raised_opp checked_opp raised_ma checked_ma raised_money_opp raised_money_ma folded")

# Inheriting from a namedtuple is convenient because it makes the class
# immutable and predefines __init__, __repr__, __hash__, __eq__, and others
class PokerBoard(_TTTB, Node):

    def find_children(board):
        # print('find_children \n')
        tmp_child_counter = 0
        moves = set()

        if (board.money_opp == 0 or board.money_machine == 0 )and board.raised_money_opp == board.raised_money_ma: 
            # if either one of them is all in - open all cards

            moves = board.assign_cards_to_middle_all_combinations(1)

            #board = board.assign_cards_to_middle(2)
            #board = board.assign_cards_to_middle(3)
            #board = board.assign_cards_to_middle(4)

            #winner, hand_with_score_ma, hand_with_score_opp = _find_winner(board.tup, folded=None)
            #terminal = True

            # turn = board.turn

            # moves.add(PokerBoard(board.tup, turn, winner, terminal, board.money_machine, board.money_middle, board.money_opp, board.raised_opp, board.checked_opp, board.raised_ma, board.checked_ma, board.raised_money_opp, board.raised_money_ma, board.folded))

            return moves 

        if (board.checked_opp and board.checked_ma) or (board.raised_opp and board.raised_ma and (board.raised_money_opp == board.raised_money_ma)):
            # both checked or both raised the same amount
            # not yet finished, open the next card
            # after opening one card, set both checks to FALSE
            turn = board.turn
            winner = board.winner
            terminal = board.terminal

            if board.tup[2] == None : 
                m2 = board.assign_cards_to_middle_all_combinations(2)
                return m2
                # board = board.assign_cards_to_middle(2)

            elif board.tup[3] == None : 
                m3 = board.assign_cards_to_middle_all_combinations(3)
                return m3
                # board = board.assign_cards_to_middle(3)

            elif board.tup[4] == None : 
                m4 = board.assign_cards_to_middle_all_combinations(4)
                return m4
                #board = board.assign_cards_to_middle(4)

            elif board.tup[4] != None :
                winner, hand_with_score_ma, hand_with_score_opp = _find_winner(board.tup,folded=None)
                terminal = True

                # new
                moves.add(PokerBoard(board.tup, turn, winner, terminal, board.money_machine, board.money_middle, board.money_opp, raised_opp, checked_opp, raised_ma, checked_ma, board.raised_money_opp, board.raised_money_ma, board.folded))
                return moves

            #checked_opp = False   
            #checked_ma = False   
            #raised_opp = False   
            #raised_ma = False

            # moves.add(PokerBoard(board.tup, turn, winner, terminal, board.money_machine, board.money_middle, board.money_opp, raised_opp, checked_opp, raised_ma, checked_ma, board.raised_money_opp, board.raised_money_ma, board.folded))
            # return moves 

        if board.terminal:  # If the game is finished then no moves can be made
            return set() 

        
        if board.turn: # turn machine
            if (board.raised_opp and board.raised_ma and (board.raised_money_opp > board.raised_money_ma)) or board.raised_opp and not board.raised_ma:
                # both raised but opp has raised more 

                # can raise
                if board.money_machine >= (board.raised_money_opp - board.raised_money_ma) : 
                    moves.add(board.make_move('R', board.raised_money_opp - board.raised_money_ma))
                else:
                    moves.add(board.make_move('R', money_machine))

                # can also fold
                moves.add(board.make_move('F', 0))


            elif not board.raised_opp and (not board.checked_ma or not board.raised_ma): # if opponnent didnt raise and machine didnt checked or raised before
                # can check 
                moves.add(board.make_move('C', 0))
                # can raise if didnt raised before and still has money
                if not board.raised_ma and board.money_machine > 0:

                    if board.money_machine > 10:
                        moves.add(board.make_move('R', 5))
                        moves.add(board.make_move('R', 10))
                        moves.add(board.make_move('R', 15))

                    elif board.money_machine > 5:
                        moves.add(board.make_move('R', 5))
                        moves.add(board.make_move('R', 10))

                    elif board.money_machine > 0:
                        moves.add(board.make_move('R', 5))

            
        else: # turn oppponent
            if (board.raised_opp and board.raised_ma and (board.raised_money_ma > board.raised_money_opp)) or board.raised_ma and not board.raised_opp:
                # both raised but opp has raised more 

                # can raise
                if board.money_opp >= board.raised_money_ma - board.raised_money_opp : 
                    moves.add(board.make_move('R', board.raised_money_ma - board.raised_money_opp))
                else:
                    moves.add(board.make_move('R', money_opp))

                # can also fold
                moves.add(board.make_move('F', 0))

            elif not board.raised_opp and (not board.checked_opp or not board.raised_opp): # if opponnent didnt raise 
                # can check 
                moves.add(board.make_move('C', 0))
                # can raise if didnt raised before and still has money
                if not board.raised_ma and board.money_opp > 0:

                    if board.money_opp > 10:
                        moves.add(board.make_move('R', 5))
                        moves.add(board.make_move('R', 10))
                        moves.add(board.make_move('R', 15))

                    elif board.money_opp > 5:
                        moves.add(board.make_move('R', 5))
                        moves.add(board.make_move('R', 10))

                    elif board.money_opp > 0:
                        moves.add(board.make_move('R', 5))

        return moves

    def find_random_child(board):
        # maybe check terminal stuff at FIRST (?)

        if (board.money_opp == 0 or board.money_machine == 0 )and board.raised_money_opp == board.raised_money_ma: 
            # if either one of them is all in - open all cards
            board = board.assign_cards_to_middle(2)
            board = board.assign_cards_to_middle(3)
            board = board.assign_cards_to_middle(4)

            winner, hand_with_score_ma, hand_with_score_opp = _find_winner(board.tup, folded=None)
            terminal = True
            turn = board.turn

            board = PokerBoard(board.tup, turn, winner, terminal, board.money_machine, board.money_middle, board.money_opp, board.raised_opp, board.checked_opp, board.raised_ma, board.checked_ma, board.raised_money_opp, board.raised_money_ma, board.folded)
            print('RANDOM BAOARD : ', board)
            return board

        if (board.checked_opp and board.checked_ma) or (board.raised_opp and board.raised_ma and (board.raised_money_opp == board.raised_money_ma)):
            # both checked or both raised the same amount
            # not yet finished, open the next card
            # after opening one card, set both checks to FALSE
            turn = board.turn
            winner = board.winner
            terminal = board.terminal

            if board.tup[2] == None : 
                board = board.assign_cards_to_middle(2)

            elif board.tup[3] == None : 
                board = board.assign_cards_to_middle(3)

            elif board.tup[4] == None : 
                board = board.assign_cards_to_middle(4)

            elif board.tup[4] != None :
                winner, hand_with_score_ma, hand_with_score_opp = _find_winner(board.tup, folded=None)
                terminal = True

            checked_opp = False   
            checked_ma = False   
            raised_opp = False   
            raised_ma = False

            board = PokerBoard(board.tup, turn, winner, terminal, board.money_machine, board.money_middle, board.money_opp, raised_opp, checked_opp, raised_ma, checked_ma, board.raised_money_opp, board.raised_money_ma, board.folded)
            print('RANDOM BAOARD : ', board)
            return board

        if board.terminal:  # If the game is finished then no moves can be made
            return None

        empty_spots = []
        if board.turn: # turn machine

            if (board.raised_opp and board.raised_ma and (board.raised_money_opp > board.raised_money_ma)) or board.raised_opp and not board.raised_ma:
                # both raised but opp has raised more 

                # can raise
                if board.money_machine >= (board.raised_money_opp - board.raised_money_ma) : 
                    empty_spots.append(['R', board.raised_money_opp - board.raised_money_ma])
                else:
                    empty_spots.append(['R', money_machine])

                # can also fold
                empty_spots.append(['F', 0])

            elif not board.raised_opp and (not board.checked_ma or not board.raised_ma): # if opponnent didnt raise and machine didnt checked or raised before
                # can check 
                empty_spots.append(['C', 0])
                # can raise if didnt raised before and still has money
                if not board.raised_ma and board.money_machine > 0:

                    if board.money_machine > 10:
                        empty_spots.append(['R', 5])
                        empty_spots.append(['R', 10])
                        empty_spots.append(['R', 15])

                    elif board.money_machine > 5:
                        empty_spots.append(['R', 5])
                        empty_spots.append(['R', 10])

                    elif board.money_machine > 0:
                        empty_spots.append(['R', 5])

            
        else: # turn oppponent
            if (board.raised_opp and board.raised_ma and (board.raised_money_ma > board.raised_money_opp)) or board.raised_ma and not board.raised_opp:
                # both raised but opp has raised more 

                # can raise
                if board.money_opp >= (board.raised_money_ma - board.raised_money_opp) : 
                    empty_spots.append(['R', board.raised_money_ma - board.raised_money_opp])
                else:
                    empty_spots.append(['R', money_opp])

                # can also fold
                empty_spots.append(['F', 0])

            elif not board.raised_opp and (not board.checked_opp or not board.raised_opp): # if opponnent didnt raise 
                # can check 
                empty_spots.append(['C', 0])
                # can raise if didnt raised before and still has money
                if not board.raised_ma and board.money_opp > 0:

                    if board.money_opp > 10:
                        empty_spots.append(['R', 5])
                        empty_spots.append(['R', 10])
                        empty_spots.append(['R', 15])

                    elif board.money_opp > 5:
                        empty_spots.append(['R', 5])
                        empty_spots.append(['R', 10])

                    elif board.money_opp > 0:
                        empty_spots.append(['R', 5])

        random_choice = choice(empty_spots)
        print('Random CHOICE :\n ', random_choice)

        board = board.make_move(random_choice[0], random_choice[1])
        print('RANDOM BAOARD : ', board)

        # return board.make_move(random_choice[0], random_choice[1])
        return board

    def reward(board):
        if not board.terminal:
            raise RuntimeError(f"reward called on nonterminal board {board}")
        #if board.winner is board.turn:
            # It's your turn and you've already won. Should be impossible.
         #   raise RuntimeError(f"reward called on unreachable board {board}")
        #if board.turn is (not board.winner):
         #   return 0  # Your opponent has just won. Bad.
        #if board.winner is None:
         #   return 0.5  # is a tie

        if board.winner :
            money_in_the_middle = board.money_middle
            return money_in_the_middle # 10
        else :
            money_in_the_middle = board.money_middle
            return -money_in_the_middle
        # The winner is neither True, False, nor None
        raise RuntimeError(f"board has unknown winner type {board.winner}")  

    def is_terminal(board):
        return board.terminal

    def assign_cards(board, deck):
        random_card_list = []
        tup_tmp = board.tup
        for index in range(0,4): # give card machines
            random_card = random.choice(deck)
            deck.remove(random_card)

            if index < 2 : 
                tup = tup_tmp[:index] + (random_card,) + tup_tmp[index + 1 :]
            else :
                ind = index + 3
                tup = tup_tmp[:ind] + (random_card,) + tup_tmp[ind + 1 :]
            tup_tmp = tup
        print('assign_cards :', tup)

        return PokerBoard(tup, board.turn, board.winner, board.terminal, board.money_machine, board.money_middle, board.money_opp, board.raised_opp, board.checked_opp, board.raised_ma, board.checked_ma, board.raised_money_opp, board.raised_money_ma, board.folded)

    def assign_cards_to_middle_all_combinations(board,index):

        moves = set()
        winner = None
        terminal = False

        checked_opp = False   
        checked_ma = False   
        raised_opp = False   
        raised_ma = False

        turn = not board.turn

        card_combos_in = CardScores()
        deck = card_combos_in.build_deck()

        already_exists = []
        already_exists.append(board.tup[0]) #card 1 machine 
        already_exists.append(board.tup[1]) #card 2 machine 
        already_exists.append(board.tup[5]) #card 1 opp 
        already_exists.append(board.tup[6]) #card 2 opp 

        if index >= 3 :
            # assigning index 3 -- opening 2nd card in the middle, should check the first card in the middle
            already_exists.append(board.tup[2])
        if index == 4 :
            # assigning index 4 -- opening 3rd card in the middle, should check the second card in the middle as well
            already_exists.append(board.tup[3])

        print('DECK ', deck)
        print('already_exists : ', already_exists)

        for already_existing_card in already_exists:
            deck.remove(already_existing_card)

        if index == 1 :
            combi = card_combos_in.combinations(deck,3)

            for combi_possibilities in combi:
                tup = board.tup[:2] + (combi_possibilities[0],) + board.tup[2 + 1 :]
                tup = tup[:3] + (combi_possibilities[1],) + tup[3 + 1 :]
                tup = tup[:4] + (combi_possibilities[2],) + tup[4 + 1 :]

                moves.add(PokerBoard(tup, turn, winner, terminal, board.money_machine, board.money_middle, board.money_opp, raised_opp, checked_opp, raised_ma, checked_ma, board.raised_money_opp, board.raised_money_ma, board.folded))

            return moves

        for random_card in deck :
            tup = board.tup[:index] + (random_card,) + board.tup[index + 1 :]

            if index == 4 : 
                winner, hand_with_score_ma, hand_with_score_opp = _find_winner(tup, folded=None)
                terminal = True

            moves.add(PokerBoard(tup, turn, winner, terminal, board.money_machine, board.money_middle, board.money_opp, raised_opp, checked_opp, raised_ma, checked_ma, board.raised_money_opp, board.raised_money_ma, board.folded))

        return moves

    def assign_cards_to_middle(board,index):

        card_combos_in = CardScores()
        deck = card_combos_in.build_deck()

        random_card = random.choice(deck)

        while random_card in board.tup:
            deck.remove(random_card)
            random_card = random.choice(deck)

        tup = board.tup[:index] + (random_card,) + board.tup[index + 1 :]
        turn = not board.turn

        return PokerBoard(tup, turn, board.winner, board.terminal, board.money_machine, board.money_middle, board.money_opp, board.raised_opp, board.checked_opp, board.raised_ma, board.checked_ma, board.raised_money_opp, board.raised_money_ma, board.folded)

    def make_move(board, action, raised_mon):

        # print('make_move board beginning : ', board)
        #print('\n')

        if action == 'R':

            checked_ma = False
            checked_opp = False
            folded = None

            if board.turn: # turn machine
                raised_ma = True
                raised_money_ma = board.raised_money_ma + raised_mon
                money_machine = board.money_machine - raised_mon
                money_middle = raised_mon + board.money_middle

                # get old values for opp
                raised_opp = board.raised_opp
                raised_money_opp = board.raised_money_opp
                money_opp = board.money_opp
            else:
                raised_opp = True
                raised_money_opp = board.raised_money_opp + raised_mon
                money_opp = board.money_opp - raised_mon 
                money_middle = board.money_middle + raised_mon

                # get old values for machine
                raised_ma = board.raised_ma
                raised_money_ma = board.raised_money_ma
                money_machine = board.money_machine


        elif action == 'C':

            folded = None
            money_middle = board.money_middle

            # get old values for opp
            raised_money_opp = board.raised_money_opp
            money_opp = board.money_opp

            # get old values for machine
            raised_money_ma = board.raised_money_ma
            money_machine = board.money_machine

            if board.turn: # turn machine
                checked_ma = True
                raised_ma = False
                checked_opp = board.checked_opp
                raised_opp = board.raised_opp
                
         
            else: # turn opp
                checked_opp = True
                raised_opp = False
                checked_ma = board.checked_ma
                raised_ma = board.raised_ma
                         

        elif action == 'F':
            checked_ma = False
            checked_opp = False
            money_middle = board.money_middle
            # get old values for opp
            raised_opp = board.raised_opp
            raised_money_opp = board.raised_money_opp
            money_opp = board.money_opp
            # get old values for machine
            raised_ma = board.raised_ma
            raised_money_ma = board.raised_money_ma
            money_machine = board.money_machine

            if board.turn:
                folded = 'ma'
            else:
                folded = 'opp'

        turn = not board.turn
        winner, hand_with_score_ma, hand_with_score_opp = _find_winner(board.tup, folded)
        is_terminal = (winner is not None) # or not any(v is None for v in tup)

        # print('make_move TURN : ', turn)
        #print('make_move WINNER : ', winner)
        #print('make_move TERMINAL : ', is_terminal)
        # print('\n')

        # print('make_move POKERBOARD After : ', PokerBoard(board.tup, turn, winner, is_terminal, money_machine, money_middle, money_opp, raised_opp, checked_opp, raised_ma, checked_ma, raised_money_opp, raised_money_ma, folded))

        return PokerBoard(board.tup, turn, winner, is_terminal, money_machine, money_middle, money_opp, raised_opp, checked_opp, raised_ma, checked_ma, raised_money_opp, raised_money_ma, folded)



def play_game():
    tree = MCTS()
    card_combos = CardScores()
    deck = card_combos.build_deck()
    # create cards to play with 
    # 2 for machine, 2 for opp, 3 for middle
    # 2598960 combinations in total
    # combi = card_combos.combinations(deck,7)
    board = new_poker_board()

    '''for i in range(0,2): # give card machines
                    random_card = random.choice(deck)
                    deck.remove(random_card)
                    board.tup = (random_card) * 7
                    # board.tup[i] = random_card
            
                for i in range(5,7): # give card opponnent
                    random_card = random.choice(deck)
                    deck.remove(random_card)
                    board.tup[i] = random_card'''

    new_board = board.assign_cards(deck)
    board = new_board
    print('board beginning: ', board)

    while True:
        action_check = False
        if not board.turn : # if turn opponnent

            while not action_check:    
                action = input("Raise (R), Check (C) or Fold(F) ? ")

                if action == 'F':
                    raised_mon = 0
                    action_check = True
                    # need somehow to get all the money from middle !!! - for the reward system can be important
                    break
            
                elif action == 'R':
                    action_check_2 = False
                    while not action_check_2:
                        raised_mon = input("How much?  ")
                        if int(raised_mon) > board.money_opp:
                            print('You dont have that much money bro')
                            act_2_input = input("Still wanna raise ? (Y/N) ")
                            if act_2_input == 'N':
                                action_check_2 = True
                        elif int(raised_mon) < board.raised_money_ma :
                            print('you need to raise at least as much as machine')
                            act_2_input = input("Still wanna raise ? (Y/N) ")
                            if act_2_input == 'N':
                                action_check_2 = True
                        else:
                            print('YOU RAISED BY ', raised_mon)
                            action_check_2 = True
                            action_check = True

                elif action == 'C':
                    if board.raised_ma:
                        print('CANT CHECK, MONEY RISED!')
                    else :
                        raised_mon = 0
                        action_check = True
                        print('YOU CHECKED')

            board = board.make_move(action, int(raised_mon))

            if board.terminal:
                break

        print('board after human move             : ', board)
        # You can train as you go, or only at the beginning.
        # Here, we train as we go, doing fifty rollouts each turn.

        # check if new cards should be opened
        board = check_if_open_new_card(board)
        print('board after human move after check : ', board)
        board_before_move = board

        t = 0
        for _ in range(200):
            t += 1
            # print('t : ', t)
            tree.do_rollout(board)

        board = tree.choose(board)
        if board.raised_money_ma > board_before_move.raised_money_ma:
            print('MACHINE RAISED MONEY BY ', board.raised_money_ma)
            # machine has raised

        elif board.checked_ma != board_before_move.checked_ma:
            print('MACHINE CHECKED')
            # machine has checked -- so that both checkeds are set to false
    
        elif board.folded == 'ma':
            print('MACHINE FOLDED')
            # machine has folded

        print('BOARD DECISION :', board)

        # check if new cards should be opened
        board = check_if_open_new_card(board)

        if board.terminal:
            break

def check_if_open_new_card(board):

    if (board.money_opp == 0 or board.money_machine == 0 )and board.raised_money_opp == board.raised_money_ma: 
        # if either one of them is all in - open all cards
        board = board.assign_cards_to_middle(2)
        board = board.assign_cards_to_middle(3)
        board = board.assign_cards_to_middle(4)

        winner, hand_with_score_ma, hand_with_score_opp = _find_winner(board.tup, folded=None)
        terminal = True
        turn = not board.turn

        print('winner : ', 'MACHINE' if winner else 'OPPONNENT')

        board = PokerBoard(board.tup, turn, winner, terminal, board.money_machine, board.money_middle, board.money_opp, board.raised_opp, board.checked_opp, board.raised_ma, board.checked_ma, board.raised_money_opp, board.raised_money_ma, board.folded)
        print('ALL IN')
        print(board)

    if (board.checked_opp and board.checked_ma) or (board.raised_opp and board.raised_ma and (board.raised_money_opp == board.raised_money_ma)):
        # both checked or both raised the same amount
        # not yet finished, open the next card
        # after opening one card, set both checks to FALSE

        winner = board.winner
        terminal = board.terminal
        turn = board.turn

        if board.tup[2] == None : 
            board = board.assign_cards_to_middle(2)

        elif board.tup[3] == None : 
            board = board.assign_cards_to_middle(3)

        elif board.tup[4] == None : 
            board = board.assign_cards_to_middle(4)

        elif board.tup[4] != None :
            winner, hand_with_score_ma, hand_with_score_opp = _find_winner(board.tup,folded=None)
            terminal = True

            print('winner : ', 'MACHINE' if winner else 'OPPONNENT')

        checked_opp = False   
        checked_ma = False   
        raised_opp = False   
        raised_ma = False

        board = PokerBoard(board.tup, turn, winner, terminal, board.money_machine, board.money_middle, board.money_opp, raised_opp, checked_opp, raised_ma, checked_ma, board.raised_money_opp, board.raised_money_ma, board.folded)
        print('OPENED NEW CARD')
        print(board)

    return board


def _find_winner(tup, folded):

    hand_with_score_ma = None
    hand_with_score_opp = None

    if folded == None :
        card_combos = CardScores()

        if tup[4] == None : # if the 3rd card in the middle IS NOT OPENED YET
            winner = None

        else:
            machine_hand = []
            opp_hand = []

            for i in range (0,5):
                machine_hand.append(tup[i])
                opp_hand.append(tup[i+2])

            score_machine, hand_with_score_ma = card_combos.score_hand(machine_hand)
            score_opp, hand_with_score_opp = card_combos.score_hand(opp_hand)

            if score_machine*1000 >= score_opp*1000: # for comma stellen 
                winner = True
            else:
                winner = False

    elif folded == 'opp':
        winner = True
    elif folded == 'ma':
        winner = False
    else :
        print('should never arrive here')

    # print('winner : ', 'MACHINE' if winner else 'OPPONNENT')

    return winner, hand_with_score_ma, hand_with_score_opp

def new_poker_board():
    return PokerBoard(tup=(None,) *7, turn=False, winner=None, terminal=False, money_machine=15, money_middle=0, money_opp=15, raised_opp=False, checked_opp=False, raised_ma=False, checked_ma=False, raised_money_opp=0, raised_money_ma=0, folded=None)


if __name__ == "__main__":
    play_game()

