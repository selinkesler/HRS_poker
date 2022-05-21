"""
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
import copy
import time
import signal

from func_timeout import func_timeout, FunctionTimedOut
import timeout_decorator 



def timeout_handler(signum, frame):   # Custom signal handler
	raise TimeoutException




_TTTB = namedtuple("PokerBoard", "tup turn winner terminal money_machine money_middle money_opp raised_opp checked_opp raised_ma checked_ma raised_money_opp raised_money_ma folded")

class PokerBoard(_TTTB, Node):

	class TimeoutException(Exception):   # Custom exception class
		pass

	def find_children(board):
		# finding all random children from that step for rollouts
		tmp_child_counter = 0
		moves = set()

		if (board.money_opp == 0 or board.money_machine == 0 )and board.raised_money_opp == board.raised_money_ma: 
			# if either one of them is all in - open all cards

			moves = board.assign_cards_to_middle_all_combinations(1)

			return moves 

		if (board.checked_opp and board.checked_ma) or (board.raised_opp and board.raised_ma and (board.raised_money_opp == board.raised_money_ma)):
			# both checked or both raised the same amount
			# not yet finished, open the next card
			# after opening one card, set both checks to FALSE
			turn = board.turn
			winner = board.winner
			terminal = board.terminal

			if board.tup[5] == None : 
				m3 = board.assign_cards_to_middle_all_combinations(5)
				return m3
				# board = board.assign_cards_to_middle(3)

			elif board.tup[6] == None : 
				m4 = board.assign_cards_to_middle_all_combinations(6)
				return m4
				#board = board.assign_cards_to_middle(4)

			elif board.tup[6] != None :
				winner, hand_with_score_ma, hand_with_score_opp = _find_winner(board.tup,folded=None)
				terminal = True

				# new
				moves.add(PokerBoard(board.tup, turn, winner, terminal, board.money_machine, board.money_middle, board.money_opp, board.raised_opp, board.checked_opp, board.raised_ma, board.checked_ma, board.raised_money_opp, board.raised_money_ma, board.folded))
				return moves

		if board.terminal:  # If the game is finished then no moves can be made
			return set() 

		
		if board.turn: # turn machine
			if (board.raised_opp and board.raised_ma and (board.raised_money_opp > board.raised_money_ma)) or board.raised_opp and not board.raised_ma:
				# both raised but opp has raised more 
				# can raise
				if board.money_machine >= (board.raised_money_opp - board.raised_money_ma) : 
					moves.add(board.make_move('R', board.raised_money_opp - board.raised_money_ma))
				else:
					moves.add(board.make_move('R', board.money_machine))

				# can also fold
				moves.add(board.make_move('F', 0))


			elif not board.raised_opp and (not board.checked_ma or not board.raised_ma): # if opponnent didnt raise and machine didnt checked or raised before
				# can check 
				moves.add(board.make_move('C', 0))
				# can raise if didnt raised before and still has money
				if not board.raised_ma and board.money_machine > 0:

					if board.money_machine <= board.money_opp :
						money_intervall = int(board.money_machine/5)

					else : # if opponnent has less money, no need to raise more than he/she
						money_intervall = int(board.money_opp/5)

					for intervall in range(1,money_intervall+1):
						moves.add(board.make_move('R', 5*intervall))

				
		else: # turn oppponent
			if (board.raised_opp and board.raised_ma and (board.raised_money_ma > board.raised_money_opp)) or board.raised_ma and not board.raised_opp:
				# both raised but opp has raised more 

				# can raise
				if board.money_opp >= board.raised_money_ma - board.raised_money_opp : 
					moves.add(board.make_move('R', board.raised_money_ma - board.raised_money_opp))
				else:
					moves.add(board.make_move('R', board.money_opp))

				# can also fold
				moves.add(board.make_move('F', 0))

			elif not board.raised_opp and (not board.checked_opp or not board.raised_opp): # if opponnent didnt raise 
				# can check 
				moves.add(board.make_move('C', 0))
				# can raise if didnt raised before and still has money
				if not board.raised_opp and board.money_opp > 0:

					if board.money_opp <= board.money_machine :
						money_intervall = int(board.money_opp/5)

					else : # if opponnent has less money, no need to raise more than he/she
						money_intervall = int(board.money_machine/5)

					for intervall in range(1,money_intervall+1):
						moves.add(board.make_move('R', 5*intervall))

		return moves

	def find_random_child(board):
		# finding random child from all the possibilities for the rollouts!

		if (board.money_opp == 0 or board.money_machine == 0 )and board.raised_money_opp == board.raised_money_ma: 
			# if either one of them is all in - open all cards
			board = board.assign_cards_to_middle(5)
			board = board.assign_cards_to_middle(6)

			winner, hand_with_score_ma, hand_with_score_opp = _find_winner(board.tup, folded=None)
			terminal = True
			turn = board.turn

			board = PokerBoard(board.tup, turn, winner, terminal, board.money_machine, board.money_middle, board.money_opp, board.raised_opp, board.checked_opp, board.raised_ma, board.checked_ma, board.raised_money_opp, board.raised_money_ma, board.folded)
			# print('RANDOM BAOARD : ', board)
			return board

		if (board.checked_opp and board.checked_ma) or (board.raised_opp and board.raised_ma and (board.raised_money_opp == board.raised_money_ma)):
			# both checked or both raised the same amount
			# not yet finished, open the next card
			# after opening one card, set both checks to FALSE
			turn = board.turn
			winner = board.winner
			terminal = board.terminal

			if board.tup[5] == None : 
				board = board.assign_cards_to_middle(5)

			elif board.tup[6] == None : 
				board = board.assign_cards_to_middle(6)

			elif board.tup[6] != None :
				winner, hand_with_score_ma, hand_with_score_opp = _find_winner(board.tup, folded=None)
				terminal = True

			checked_opp = False   
			checked_ma = False   
			raised_opp = False   
			raised_ma = False

			board = PokerBoard(board.tup, turn, winner, terminal, board.money_machine, board.money_middle, board.money_opp, raised_opp, checked_opp, raised_ma, checked_ma, board.raised_money_opp, board.raised_money_ma, board.folded)
			# print('RANDOM BAOARD : ', board)
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
					empty_spots.append(['R', board.money_machine])

				# can also fold
				empty_spots.append(['F', 0])

			elif not board.raised_opp and (not board.checked_ma or not board.raised_ma): # if opponnent didnt raise and machine didnt checked or raised before
				# can check 
				empty_spots.append(['C', 0])
				# can raise if didnt raised before and still has money

				if not board.raised_ma and board.money_machine > 0:

					if board.money_machine <= board.money_opp :
						money_intervall = int(board.money_machine/5)

					else : # if opponnent has less money, no need to raise more than he/she
						money_intervall = int(board.money_opp/5)

					for intervall in range(1,money_intervall+1):
						empty_spots.append(['R', 5*intervall])

			
		else: # turn oppponent
			if (board.raised_opp and board.raised_ma and (board.raised_money_ma > board.raised_money_opp)) or board.raised_ma and not board.raised_opp:
				# both raised but opp has raised more 

				# can raise
				if board.money_opp >= (board.raised_money_ma - board.raised_money_opp) : 
					empty_spots.append(['R', board.raised_money_ma - board.raised_money_opp])
				else:
					empty_spots.append(['R', board.money_opp])

				# can also fold
				empty_spots.append(['F', 0])

			elif not board.raised_opp and (not board.checked_opp or not board.raised_opp): # if opponnent didnt raise 
				# can check 
				empty_spots.append(['C', 0])
				# can raise if didnt raised before and still has money

				if not board.raised_opp and board.money_opp > 0:

					if board.money_opp <= board.money_machine :
						money_intervall = int(board.money_opp/5)

					else : # if opponnent has less money, no need to raise more than he/she
						money_intervall = int(board.money_machine/5)

					for intervall in range(1,money_intervall+1):
						empty_spots.append(['R', 5*intervall])

		random_choice = choice(empty_spots)
		# print('Random CHOICE :\n ', random_choice)

		board = board.make_move(random_choice[0], random_choice[1])
		# print('RANDOM BAOARD : ', board)

		# return board.make_move(random_choice[0], random_choice[1])
		return board

	def reward(board):
		"""
		calculate the reward for the terminal state for rollouts
		Input : board
		Output : reward
		"""
		reward_to_get = board.money_middle
		if not board.terminal:
			raise RuntimeError("reward called on nonterminal board ")
		if board.winner :
			return -reward_to_get # 10
		else :
			return reward_to_get

		raise RuntimeError("board has unknown winner type")  

	def is_terminal(board):
		return board.terminal

	def assign_cards(board, deck, cards=[]):
		random_card_list = []
		tup_tmp = board.tup

		if cards == []:
			for index in range(0,4): # give card machines
				random_card = random.choice(deck)
				deck.remove(random_card)

				if index < 2 : 
					tup = tup_tmp[:index] + (random_card,) + tup_tmp[index + 1 :]
				tup_tmp = tup
		else: 
			for index in range(0,4): # give card machines

				if index < 2 : 
					tup = tup_tmp[:index] + (cards[index],) + tup_tmp[index + 1 :]
				tup_tmp = tup

		return PokerBoard(tup, board.turn, board.winner, board.terminal, board.money_machine, board.money_middle, board.money_opp, board.raised_opp, board.checked_opp, board.raised_ma, board.checked_ma, board.raised_money_opp, board.raised_money_ma, board.folded)


	def assign_cards_for_estimation(board, deck):
		# assin random cards to opponent while 'removing' the machine cards so that opp doesnt know machine cards

		random_card_list = []
		tup_tmp = board.tup
		tup_new = board.tup

		# remove existing cards from deck for random choice
		deck.remove(tup_tmp[0])
		deck.remove(tup_tmp[1])
		deck.remove(tup_tmp[2])
		deck.remove(tup_tmp[3])
		deck.remove(tup_tmp[4])

		if tup_tmp[5] != None:
			deck.remove(tup_tmp[5])

		if tup_tmp[6] != None:
			deck.remove(tup_tmp[6])

		# choose random card for opp
		random_card = random.choice(deck)
		deck.remove(random_card)

		tup = tup_tmp[:0] + (random_card,) + tup_tmp[0 + 1 :]
		tup_tmp = tup

		random_card = random.choice(deck)
		tup = tup_tmp[:1] + (random_card,) + tup_tmp[1 + 1 :]

		return PokerBoard(tup, board.turn, board.winner, board.terminal, board.money_machine, board.money_middle, board.money_opp, board.raised_opp, board.checked_opp, board.raised_ma, board.checked_ma, board.raised_money_opp, board.raised_money_ma, board.folded)


	def get_opponents_real_cards(board):

		# get real opp cards, which the machine doesn't know untill now
		op_card_1 = input("opponnent Card 1 ? ")
		op_card_2 = input("opponnent Card 2 ? ")
		board = board.assign_cards_to_middle(index=7,card=op_card_1)
		board = board.assign_cards_to_middle(index=8,card=op_card_2)

		return board


	def assign_cards_to_middle_all_combinations(board,index):
		# for finding random children, random cards should be assigned to middle 

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

		already_exists.append(board.tup[2]) #card 1 middle
		already_exists.append(board.tup[3]) #card 2 middle
		already_exists.append(board.tup[4]) #card 3 middle


		if index == 6 :
			# assigning index 4 -- opening 3rd card in the middle, should check the second card in the middle as well
			already_exists.append(board.tup[5])

		for already_existing_card in already_exists:
			deck.remove(already_existing_card)

		if index == 1 :
			combi = card_combos_in.combinations(deck,2)
			# all 2 card possibilities will be added as possibility for opponents cards

			for combi_possibilities in combi:
				tup = board.tup[:5] + (combi_possibilities[0],) + board.tup[5 + 1 :]
				tup = tup[:6] + (combi_possibilities[1],) + tup[6 + 1 :]

				moves.add(PokerBoard(tup, turn, winner, terminal, board.money_machine, board.money_middle, board.money_opp, raised_opp, checked_opp, raised_ma, checked_ma, board.raised_money_opp, board.raised_money_ma, board.folded))

			return moves

		for random_card in deck :
			tup = board.tup[:index] + (random_card,) + board.tup[index + 1 :]

			if index == 6 : 
				winner, hand_with_score_ma, hand_with_score_opp = _find_winner(tup, folded=None)
				terminal = True

			moves.add(PokerBoard(tup, turn, winner, terminal, board.money_machine, board.money_middle, board.money_opp, raised_opp, checked_opp, raised_ma, checked_ma, board.raised_money_opp, board.raised_money_ma, board.folded))

		return moves

	def assign_cards_to_middle(board,index,card=None):

		if card is not None :
			# if a card is given, use direclty tha card
			random_card = card

		else:
			# if no card id given, create a random card, whihc is not 'opened' in the middle
			card_combos_in = CardScores()
			deck = card_combos_in.build_deck()
			random_card = random.choice(deck)

			while random_card in board.tup:
				deck.remove(random_card)
				random_card = random.choice(deck)

		# assign new card to board
		tup = board.tup[:index] + (random_card,) + board.tup[index + 1 :]
		turn = not board.turn

		return PokerBoard(tup, turn, board.winner, board.terminal, board.money_machine, board.money_middle, board.money_opp, board.raised_opp, board.checked_opp, board.raised_ma, board.checked_ma, board.raised_money_opp, board.raised_money_ma, board.folded)

	def make_move(board, action, raised_mon,real=False):
		# used both for random rollouts as well as real game
		# makes the moves in the board and returns the new board setting after the move

		if action == 'R': # RAISED

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


		elif action == 'C': # CHECKED 

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
						 

		elif action == 'F': #  FOLDED
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
		#if ((board.checked_opp and board.checked_ma) or (board.raised_opp and board.raised_ma and (board.raised_money_opp == board.raised_money_ma))) or ((board.money_opp == 0 or board.money_machine == 0 )and board.raised_money_opp == board.raised_money_ma):
		if not real :
			winner, hand_with_score_ma, hand_with_score_opp = _find_winner(board.tup, folded)

		else :
			if folded == 'ma' :
				winner = False
			elif folded == 'opp':
				winner = True
			else :
				winner = None

		is_terminal = (winner is not None) # or not any(v is None for v in tup)

		return PokerBoard(board.tup, turn, winner, is_terminal, money_machine, money_middle, money_opp, raised_opp, checked_opp, raised_ma, checked_ma, raised_money_opp, raised_money_ma, folded)




def opponent_estimation(board,tree): 
	######  estimate opponents moves! ######
	card_combos = CardScores()
	deck_new = card_combos.build_deck()
	for _ in range(10): # to assign n times random cards to opp for simulation
		deck_new = card_combos.build_deck()
		# create a copy of the board state so that the simulations for opponent can be done
		opponent_guess_board = copy.deepcopy(board)
		# assin random cards to opponent while 'removing' the machine cards so that opp doesnt know machine cards
		opponent_guess_board = opponent_guess_board.assign_cards_for_estimation(deck_new)
		# do simulations for the opponnet
		for _ in range(100):
			# time.sleep(3)
			tree.do_rollout(opponent_guess_board) # Whatever your function that might hang

	# 3 levels are declared for opponent
	# level 3 : pro - takes the best action from simulations
	# level 2 : middle - chooses random from best and second best action from simulation
	# level 1 : noob - chooses random from third and second best action from simulation
	opponent_guess_board = tree.choose_estimate_with_level(opponent_guess_board,level=2)

	if opponent_guess_board.raised_money_opp > board.raised_money_opp:
		print('OPPPONNENT WILL PROBABLY RAISE MONEY BY ', opponent_guess_board.raised_money_opp-board.raised_money_opp)

	elif opponent_guess_board.checked_opp != board.checked_opp:
		print('OPPONNENT WILL PROBABLY CHECK')

	elif opponent_guess_board.folded == 'opp':
		print('OPPONNENT WILL PROBABLY FOLD')

	######  opponent estimation done! ######


def machine_decision(board,tree): 
	for _ in range(300):
		tree.do_rollout(board)

	board = tree.choose(board)

	return board




def play_game():
	tree = MCTS()
	card_combos = CardScores()
	deck = card_combos.build_deck()
	# create cards to play with 
	# 2 for machine, 2 for opp, 3 for middle
	# 2598960 combinations in total
	# combi = card_combos.combinations(deck,7)
	board = new_poker_board()

	still_playing = True
	board_exists = False

	while still_playing:
		print('BOARD EX : ', board_exists)

		if board_exists :
			wanna_play = input("Another round ? (Y/N) ")

			if wanna_play == 'N':
				break

			elif wanna_play == 'Y':
				print('Lets go!')

				tup=(None,) *9
				turn=False
				winner=None
				terminal=False
				raised_opp=False
				checked_opp=False
				raised_ma=False 
				checked_ma=False
				raised_money_opp=0
				raised_money_ma=0
				folded=None
				money_middle = 0

				board = PokerBoard(tup, turn, winner, terminal, old_board.money_machine, money_middle, old_board.money_opp, raised_opp, checked_opp, raised_ma, checked_ma, raised_money_opp, raised_money_ma, folded)
				if board.money_machine == 0 :
					print('sorry, machine doesnt have any money left')
					break
				elif board.money_opp == 0:
					print('sorry, you dont have any money left')
					break


		new_board = board.assign_cards(deck)

		# ALTERNATIVE FROM DETECTION !
		# board.assign_cards_to_middle(index=0,card=ma_card_1)
		# board.assign_cards_to_middle(index=1,card=ma_card_1)

		

		board = new_board
		print('BOARD IN THE BEGINNING : ', board)

		turn_iteration = 1

		while True:
			action_check = False
			if not board.turn : # if turn opponnent

				while not action_check:    
					action = input("Raise (R), Check (C) or Fold(F) ? ")

					if turn_iteration == 1 and action != 'R' :
						print('MUST RAISE IN THE FIRST ROUND')

					elif action == 'F':
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
							elif (int(raised_mon)+board.raised_money_opp) < board.raised_money_ma :
								print('you need to raise at least as much as machine')
								act_2_input = input("Still wanna raise ? (Y/N) ")
								if act_2_input == 'N':
									action_check_2 = True

							# elif (board.raised_money_ma < board.raised_money_opp + int(raised_mon)) and int(raised_mon) > board.money_machine:

							elif (board.raised_ma and (int(raised_mon)+board.raised_money_opp > board.money_machine + board.raised_money_ma)) or (not board.raised_ma and (int(raised_mon) > board.money_machine)):

								print('cant raise more money than your opponnent has, doesnt make sense :D' )
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

				board = board.make_move(action, int(raised_mon),real=True)


				if board.terminal and (board.folded == None):
					winner = None
					terminal = False
					board = PokerBoard(board.tup, board.turn, winner, terminal, board.money_machine, board.money_middle, board.money_opp, board.raised_opp, board.checked_opp, board.raised_ma, board.checked_ma, board.raised_money_opp, board.raised_money_ma, board.folded)

				'''terminal_state,board = check_board_terminal(board)
					if terminal_state :
					old_board = board
					break'''

			print('\n')

			if turn_iteration == 1 :
				# first round
				# machine can only raise for now

				board = board.make_move('R', int(raised_mon),real=True)
				print('MACHINE ALSO RAISES 5 ')
				# print('board in first ROUND: ', board)

				# cards open 

				# FROM DETECTION
				# board = board.assign_cards_to_middle(index=2,card=mid_1)
				# board = board.assign_cards_to_middle(index=3,card=mid_2)
				# board = board.assign_cards_to_middle(index=4,card=mid_3)

				board = board.assign_cards_to_middle(2)
				board = board.assign_cards_to_middle(3)
				board = board.assign_cards_to_middle(4)

				turn = not board.turn

				checked_opp = False   
				checked_ma = False   
				raised_opp = False   
				raised_ma = False

				board = PokerBoard(board.tup, turn, board.winner, board.terminal, board.money_machine, board.money_middle, board.money_opp, raised_opp, checked_opp, raised_ma, checked_ma, board.raised_money_opp, board.raised_money_ma, board.folded)
				print('NEW 3 CARDS ARE OPENED IN THE MIDDLE')
				print('CURRENT CARDS IN THE MIDDLE : ', board.tup)
				# print('board with new cards : ',board)
				turn_iteration += 1
				board_exists = True

				board = check_if_open_new_card(board)

				terminal_state,board = check_board_terminal(board)
				if terminal_state :
					old_board = board
					break
				
			else : # after the first turn (after opening the 3 cards in the middle)

				print('BOARD AFTER HUMAN MOVE : \n', board)
				print('\n')
				# You can train as you go, or only at the beginning.
				# Here, we train as we go, doing fifty rollouts each turn.

				# check if new cards should be opened
				board = check_if_open_new_card(board)
				# print('BOARD AFTER NEW CARD CHECK (AFTER HUMAN MOVE) : \n', board)
				board_before_move = board

				terminal_state,board = check_board_terminal(board)
				if terminal_state :
					old_board = board
					break

				#### buraya
				try:
					board = func_timeout(5, machine_decision, args=(board, tree))
				except FunctionTimedOut:
					print ( "Machine decicion time out, skip it dont wait it")
					turn = not board.turn
					if board.checked_opp :
						checked_ma = True
						# just check as default
						board = PokerBoard(board.tup, turn, board.winner, board.terminal, board.money_machine, board.money_middle, board.money_opp, board.raised_opp, board.checked_opp, board.raised_ma, checked_ma, board.raised_money_opp, board.raised_money_ma, board.folded)
					elif board.raised_opp and not board.raised_ma:
						raised_ma = True
						raised_money_ma = board.raised_money_opp
						board = PokerBoard(board.tup, turn, board.winner, board.terminal, board.money_machine, board.money_middle, board.money_opp, board.raised_opp, board.checked_opp, raised_ma, board.checked_ma, board.raised_money_opp, raised_money_ma, board.folded)



				# dont wanna end the game with rollout moves (comes from simulation)
				if board.terminal and (board.folded == None):
					winner = None
					terminal = False
					board = PokerBoard(board.tup, board.turn, winner, terminal, board.money_machine, board.money_middle, board.money_opp, board.raised_opp, board.checked_opp, board.raised_ma, board.checked_ma, board.raised_money_opp, board.raised_money_ma, board.folded)


				if board.raised_money_ma > board_before_move.raised_money_ma:
					print('MACHINE RAISED MONEY BY ', board.raised_money_ma-board_before_move.raised_money_ma)
					# machine has raised

				elif board.checked_ma != board_before_move.checked_ma:
					print('MACHINE CHECKED')
					# machine has checked -- so that both checkeds are set to false
			
				elif board.folded == 'ma':
					print('MACHINE FOLDED')
					# machine has folded

				print('\n')
				print('BOARD AFTER MACHINE DECISION : \n', board)
				print('\n')

				# check if new cards should be opened
				board = check_if_open_new_card(board)

				terminal_state,board = check_board_terminal(board)
				if terminal_state :
					old_board = board
					break


				try:
					doitReturnValue = func_timeout(3, opponent_estimation, args=(board, tree))
				except FunctionTimedOut:
					print ( "Oppinent estimation time out, skip it dont wait it")

				# Handle any exceptions that doit might raise here

				
def check_board_terminal(board):
	if board.terminal:
		print('TERMINAL')
		money_machine = board.money_machine
		money_opp = board.money_opp
		money_middle = board.money_middle

		if board.winner : # machine won
			money_machine = board.money_middle + board.money_machine
		elif board.winner == False:
			money_opp = board.money_middle + board.money_opp

		money_middle = 0

		board = PokerBoard(board.tup, board.turn, board.winner, board.terminal, money_machine, money_middle, money_opp, board.raised_opp, board.checked_opp, board.raised_ma, board.checked_ma, board.raised_money_opp, board.raised_money_ma, board.folded)
		old_board = board
		return True, old_board
	else:
		return False, board

def check_if_open_new_card(board):

	if board.terminal:
		print('GAME OVER')

		if board.folded == 'opp':
			winner = True
		elif board.folded == 'ma':
			winner = False

			print(board)

		else : 

			board = board.get_opponents_real_cards()
			winner, hand_with_score_ma, hand_with_score_opp, c_h_best, c_o_best  = _find_winner_real(board.tup, folded=None)

		print('winner : ', 'MACHINE' if winner else 'OPPONNENT')


	if (board.money_opp == 0 or board.money_machine == 0 )and board.raised_money_opp == board.raised_money_ma: 
		# if either one of them is all in - open all cards
		board = board.assign_cards_to_middle(5)
		board = board.assign_cards_to_middle(6)

		print('ALL IN, OPENING ALL THE CARDS IN THE MIDDLE')
		print(board.tup)
		print('\n')

		board = board.get_opponents_real_cards()

		winner, hand_with_score_ma, hand_with_score_opp, c_h_best, c_o_best = _find_winner_real(board.tup, folded=None)

		if winner is not None :
			print('winner : ', 'MACHINE' if winner else 'OPPONNENT')

			if board.folded is None :

				print('machine : ' + hand_with_score_ma + ' , ' + str(c_h_best))
				print('opponnent : ' + hand_with_score_opp + ' , ' + str(c_o_best))

		terminal = True
		turn = not board.turn
		money_machine = board.money_machine
		money_opp = board.money_opp
		money_middle = board.money_middle

		'''if winner : # machine won
									money_machine = board.money_middle + board.money_machine
								elif board.winner == False:
									money_opp = board.money_middle + board.money_opp
						
								money_middle = 0'''

		board = PokerBoard(board.tup, turn, winner, terminal, money_machine, money_middle, money_opp, board.raised_opp, board.checked_opp, board.raised_ma, board.checked_ma, board.raised_money_opp, board.raised_money_ma, board.folded)


	elif (board.checked_opp and board.checked_ma) or (board.raised_opp and board.raised_ma and (board.raised_money_opp == board.raised_money_ma)):
		# both checked or both raised the same amount
		# not yet finished, open the next card
		# after opening one card, set both checks to FALSE

		winner = board.winner
		terminal = board.terminal
		turn = board.turn
		money_machine = board.money_machine
		money_opp = board.money_opp
		money_middle = board.money_middle

		if board.tup[5] == None : 
			board = board.assign_cards_to_middle(5)

		elif board.tup[6] == None : 
			board = board.assign_cards_to_middle(6)

		elif board.tup[6] != None :
			board = board.get_opponents_real_cards()

			winner, hand_with_score_ma, hand_with_score_opp, c_h_best, c_o_best = _find_winner_real(board.tup,folded=None)
			terminal = True

			'''if winner : # machine won
															  money_machine = board.money_middle + board.money_machine
														  elif board.winner == False:
															  money_opp = board.money_middle + board.money_opp
											  
														  money_middle = 0 '''          

		checked_opp = False   
		checked_ma = False   
		raised_opp = False   
		raised_ma = False

		board = PokerBoard(board.tup, turn, winner, terminal, money_machine, money_middle, money_opp, raised_opp, checked_opp, raised_ma, checked_ma, board.raised_money_opp, board.raised_money_ma, board.folded)
		
		print('\nOPENED NEW CARD SINCE BOTH PLAYERS RAISED SAME AMOUNT OR BOTH CHECKED IN THE ROUND')
		print('NEW CARDS : ', board.tup)
		print('\nNEW ROUND')
		print('BOARD SITUATION : ', board)


		if winner is not None :
			print('winner : ', 'MACHINE' if winner else 'OPPONNENT')

			if board.folded is None :

				print('machine : ' + hand_with_score_ma + ' , ' + str(c_h_best))
				print('opponnent : ' + hand_with_score_opp + ' , ' + str(c_o_best))

	return board

def _find_winner(tup, folded):
	# to find winner in use of the random rollout
	# generates oppponnents cards randomly!!

	hand_with_score_ma = None
	hand_with_score_opp = None

	if folded == None :
		card_combos = CardScores()

		if tup[6] == None : # if the 3rd card in the middle IS NOT OPENED YET
			winner = None

		else:
			machine_hand = []
			opp_hand = []

			# for random opponnent cards
			deck = card_combos.build_deck()
			for i in range(0,7):
				deck.remove(tup[i])
			for i in range (0,2):
				random_card = random.choice(deck)
				opp_hand.append(random_card)
			#############################

			opp_hand.append(tup[2])
			opp_hand.append(tup[3])
			opp_hand.append(tup[4])
			opp_hand.append(tup[5])
			opp_hand.append(tup[6])


			for i in range (0,7):
				machine_hand.append(tup[i])

			combi_hand = card_combos.combinations(machine_hand,5)
			combi_opp = card_combos.combinations(opp_hand,5)

			# calculate scores machine hand for all combination possibilities
			score_machine = 0
			hand_with_score_ma = None
			for c_h in combi_hand:
				score_machine_tmp, hand_with_score_ma_tmp = card_combos.score_hand(c_h)

				if score_machine_tmp*1000 > score_machine*1000:
					score_machine = score_machine_tmp
					hand_with_score_ma = hand_with_score_ma_tmp

			# calculate scores opponent hand for all combination possibilities
			score_opp = 0
			hand_with_score_opp = None
			for c_o in combi_opp:
				score_opp_tmp, hand_with_score_opp_tmp = card_combos.score_hand(c_o)

				if score_opp_tmp*1000 > score_opp*1000:
					score_opp = score_opp_tmp
					hand_with_score_opp = hand_with_score_opp_tmp

			if score_machine*1000 >= score_opp*1000: # for comma position 
				winner = True
			else:
				winner = False

	elif folded == 'opp':
		winner = True
	elif folded == 'ma':
		winner = False
	else :
		print('should never arrive here')

	return winner, hand_with_score_ma, hand_with_score_opp

def _find_winner_real(tup, folded):
	# finding winner for the real game, opponents real cards should already been asked

	hand_with_score_ma = None
	hand_with_score_opp = None
	c_o_best = ''
	c_h_best = ''

	if folded == None :
		card_combos = CardScores()

		if tup[6] == None : # if the 3rd card in the middle IS NOT OPENED YET
			winner = None

		else:
			machine_hand = []
			opp_hand = []

			for i in range (0,7):
				machine_hand.append(tup[i])
				opp_hand.append(tup[i+2]) # get the real values from the tuple
 
			# from 7 cards build the 5 card combination of each hand to calculate scores
			combi_hand = card_combos.combinations(machine_hand,5)
			combi_opp = card_combos.combinations(opp_hand,5)

			# calculate scores machine hand for all combination possibilities
			score_machine = 0
			for c_h in combi_hand:
				score_machine_tmp, hand_with_score_ma_tmp = card_combos.score_hand(c_h)

				if score_machine_tmp*1000 > score_machine*1000:
					score_machine = score_machine_tmp
					hand_with_score_ma = hand_with_score_ma_tmp
					c_h_best = c_h # get only the best

			# calculate scores opponent hand for all combination possibilities
			score_opp = 0
			for c_o in combi_opp:
				score_opp_tmp, hand_with_score_opp_tmp = card_combos.score_hand(c_o)

				if score_opp_tmp*1000 > score_opp*1000:
					score_opp = score_opp_tmp
					hand_with_score_opp = hand_with_score_opp_tmp
					c_o_best = c_o # get only the best

			# find the winner with comparing the best scores of both hands
			if score_machine*1000 >= score_opp*1000: # for comma positions 
				winner = True
			else:
				winner = False

	# check if someone folded
	elif folded == 'opp':
		winner = True

	elif folded == 'ma':
		winner = False
	else :
		print('should never arrive here')

	return winner, hand_with_score_ma, hand_with_score_opp, c_h_best, c_o_best

def new_poker_board():
	# create new Pokerboard with init parameters
	return PokerBoard(tup=(None,) *9, turn=False, winner=None, terminal=False, money_machine=30, money_middle=0, money_opp=30, raised_opp=False, checked_opp=False, raised_ma=False, checked_ma=False, raised_money_opp=0, raised_money_ma=0, folded=None)


if __name__ == "__main__":
	play_game()

