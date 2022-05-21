"""
A minimal implementation of Monte Carlo tree search (MCTS) in Python 3
Luke Harold Miles, July 2019, Public Domain Dedication
See also https://en.wikipedia.org/wiki/Monte_Carlo_tree_search
https://gist.github.com/qpwo/c538c6f73727e254fdc7fab81024f6e1
"""
from abc import ABC, abstractmethod
from collections import defaultdict
import math
import random

class MCTS:
    "Monte Carlo tree searcher. First rollout the tree then choose a move."

    def __init__(self, exploration_weight=20):
        self.Q = defaultdict(int)  # total reward of each node
        self.N = defaultdict(int)  # total visit count for each node
        self.children = dict()  # children of each node
        self.exploration_weight = exploration_weight
        self.tmp = 0

    def choose(self, node):
        "Choose the best successor of node. (Choose a move in the game)"
        if node.is_terminal():
            raise RuntimeError(f"choose called on terminal node {node}")

        if node not in self.children:
            return node.find_random_child()

        def score(n):
            if self.N[n] == 0:
                return float("-inf")  # avoid unseen moves
            return self.Q[n] / self.N[n]  # average reward

        # print('Chooooose : ', self.children[node])

        scores = []
        for i in self.children[node]:
            scores.append(score(i))

        # print('scores :', scores)
        # print(sorted(scores, reverse=True))
        # print(sorted(scores, reverse=True)[1])

        # print('scores :', scores)



        return max(self.children[node], key=score)


    def choose_estimate_with_level(self, node,level):
        "Choose the best successor of node. (Choose a move in the game)"
        if node.is_terminal():
            raise RuntimeError(f"choose called on terminal node {node}")

        if node not in self.children:
            return node.find_random_child()

        def score(n):
            if self.N[n] == 0:
                return float("-inf")  # avoid unseen moves
            return self.Q[n] / self.N[n]  # average reward

        second_best_action = None
        third_best_action = None
        scores = []
        for i in self.children[node]:
            scores.append(score(i))

        sorted_scores = sorted(scores, reverse=True)
        best_action = max(self.children[node], key=score)
        if len(sorted_scores) >= 2:
            second_best_score = sorted_scores[1]
            second_best_score_index = scores.index(second_best_score)
        if len(sorted_scores) >= 3:
            third_best_score = sorted_scores[2]
            third_best_score_index = scores.index(third_best_score)

        tmp_c = 0
        for nodes_to_look in self.children[node]:
            if len(sorted_scores) >= 2:
                if tmp_c == second_best_score_index:
                    second_best_action = nodes_to_look
                if len(sorted_scores) >= 3:
                    if tmp_c == third_best_score_index:
                        third_best_action = nodes_to_look
            tmp_c += 1

        if level == 3:
            # pro
            # get best found action through the simulations
            return best_action

        elif level == 2:
            # mid level
            mid = []
            mid.append(best_action)
            if second_best_action != None:
                mid.append(second_best_action)
        
            return random.choice(mid)

        elif level == 1:
            # noob level 
            noob = []
            if second_best_action != None:
                noob.append(second_best_action)
            if third_best_action != None:
                noob.append(third_best_action)
            if second_best_action == None and third_best_action == None:
                noob.append(best_action)
            
            return random.choice(noob)

        
    def do_rollout(self, node):
        "Make the tree one layer better. (Train for one iteration.)"
        self.tmp += 1
        # print('do rollout count : ', self.tmp)

        path = self._select(node)
        #print('do_rollout PATH : ', path)
        leaf = path[-1]
        # print('do_rollout LEAF : ', leaf)
        self._expand(leaf)
        reward = self._simulate(leaf)
        #print('reward : ', reward)
        self._backpropagate(path, reward)
        #print('_backpropagate done')

    def _select(self, node):
        "Find an unexplored descendent of `node`"
        path = []
        # print('in _select')
        while True:
            # print('node : ', node)
            path.append(node)
            if node not in self.children or not self.children[node]:
                # print('########## node is either unexplored or terminal ###########')
                # node is either unexplored or terminal
                return path
            unexplored = self.children[node] - self.children.keys()
            # print('unexplored : ', len(unexplored))
            if unexplored:
                n = unexplored.pop()
                path.append(n)
                return path
            node = self._uct_select(node)  # descend a layer deeper

    def _expand(self, node):
        "Update the `children` dict with the children of `node`"
        if node in self.children:
            return  # already expanded
        self.children[node] = node.find_children()

    def _simulate(self, node):
        "Returns the reward for a random simulation (to completion) of `node`"
        invert_reward = True
        while True:
            #print('SIMULATION node before :', node)
            #print('SIMULATION node.is_terminal() ; ', node.is_terminal())
            if node.is_terminal():
                reward = node.reward()
                # print('SIMULATION reward : ', reward)
                return 1 - reward if invert_reward else reward

            try:
                node = node.find_random_child()
                pass
            except Exception as e:
                print('EERRRROR')
                print(node) 
            
            #print('SIMULATION node after :', node)
            invert_reward = not invert_reward

    def _backpropagate(self, path, reward):
        "Send the reward back up to the ancestors of the leaf"
        for node in reversed(path):
            self.N[node] += 1
            self.Q[node] += reward
            reward = 1 - reward  # 1 for me is 0 for my enemy, and vice versa

    def _uct_select(self, node):
        "Select a child of node, balancing exploration & exploitation"

        # All children of node should already be expanded:
        assert all(n in self.children for n in self.children[node])

        log_N_vertex = math.log(self.N[node])

        def uct(n):
            "Upper confidence bound for trees"
            return self.Q[n] / self.N[n] + self.exploration_weight * math.sqrt(
                log_N_vertex / self.N[n]
            )

        return max(self.children[node], key=uct)


class Node(ABC):
    """
    A representation of a single board state.
    MCTS works by constructing a tree of these Nodes.
    Could be e.g. a chess or checkers board state.
    """

    @abstractmethod
    def find_children(self):
        "All possible successors of this board state"
        return set()

    @abstractmethod
    def find_random_child(self):
        "Random successor of this board state (for more efficient simulation)"
        return None

    @abstractmethod
    def is_terminal(self):
        "Returns True if the node has no children"
        return True

    @abstractmethod
    def reward(self):
        "Assumes `self` is terminal node. 1=win, 0=loss, .5=tie, etc"
        return 0

    @abstractmethod
    def __hash__(self):
        "Nodes must be hashable"
        return 123456789

    @abstractmethod
    def __eq__(node1, node2):
        "Nodes must be comparable"
        return True


