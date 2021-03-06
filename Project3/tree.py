import random
import numpy as np


class Tree:
    def __init__(self):
        self.state_to_node = {}  # key: (player, state), value: Node-object

    def get_node(self, env):  # lookup Node in tree
        state = env.get_state()
        if self.state_to_node.get(state):
            return self.state_to_node[state]
        else:
            self.state_to_node[state] = Node(state[0], env.get_legal_actions())
            return False

    def get_distribution(self, env):
        moves = env.all_moves
        node = self.state_to_node[env.get_state()]
        D = np.zeros(env.size**2)
        for i in range(env.size**2):
            D[i] = node.actions[moves[i]][0]/node.visits if moves[i] in node.actions else 0
        return np.asarray(D, dtype = np.float64)

    def rollout_policy(self, env, ANN=0, eps=1, stoch=True):
        legal = env.get_legal_actions()
        if random.random() < eps:
            return random.choice(legal)  # choose random action
        else:
            _, stoch_index, greedy_index = ANN.get_move(env)
            if stoch:
                return env.all_moves[stoch_index]
            else:
                return env.all_moves[greedy_index]

    def tree_policy(self, env, c):
        node = self.get_node(env)
        actions = list(node.actions.keys())
        action_values = [node.get_action_value(a, c) for a in actions]
        return actions[np.argmax(action_values) if env.player == 1 else np.argmin(action_values)]

    def backup(self, nodes, result):
        for node in nodes:
            node.update_values(result)


class Node:
    def __init__(self, player, legal_actions):
        self.player = player
        self.visits = 0
        self.actions = {a: [0,0] for a in legal_actions}  # key: action, value: [visits, q_value]
        self.prev_action = None

    def update_values(self, result):
        self.visits += 1
        self.actions[self.prev_action][0] += 1
        n, q = self.actions[self.prev_action]
        self.actions[self.prev_action][1] += (result - q) / n

    def set_last_action(self, action):
        self.prev_action = action

    def get_action_value(self, action, c):
        n, q = self.actions[action]
        c *= 1 if self.player == 1 else -1
        return q + c * np.sqrt(np.log(self.visits if self.visits > 0 else 1) / (n + 1))

    def __repr__(self):
        return "Player: {}, Visits: {}, Actions: {}, Previous action: {}".format(self.player, self.visits, self.actions, self.prev_action)
