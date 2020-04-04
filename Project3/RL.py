import math
import random

import numpy as np
from ANN import ANN
from game import HexGame
from matplotlib import pyplot as plt
from mcts import MonteCarloTreeSearch
from tqdm import tqdm

np.set_printoptions(linewidth=500)  # print formatting

class RL:
    def __init__(self, G, M, env, ANN, MCTS, save_interval, buffer_size, batch_size):
        self.G = G
        self.M = M
        self.env = env
        self.ANN = ANN
        self.MCTS = MCTS
        self.save_interval = save_interval
        self.buffer_size = buffer_size
        self.batch_size = batch_size
        self.losses = []
        self.accuracies = []
        self.buffer = []

    def run(self):
        self.ANN.save(env.size, 0)
        for i in tqdm(range(G)):
            self.env.reset()
            self.MCTS.init_tree()
            while not self.env.is_game_over():
                D = self.MCTS.search(self.env, self.M)
                self.add_case(D)
                env.move(env.all_moves[np.argmax(D)])
            self.train_ann()
            if (i + 1) % self.save_interval == 0:
                self.save_model()
                self.ANN.epochs += 5
            self.MCTS.eps *= 0.99
        self.plot()

    def add_case(self, D):
        self.buffer.append((env.flat_state, D))
        if len(self.buffer) > 500:
            self.buffer.pop(0)

    def train_ann(self):
        training_cases = random.sample(self.buffer, min(len(self.buffer),self.batch_size))
        input, target = list(zip(*training_cases))
        self.losses.append(self.ANN.fit(input, target, debug=True))
        self.accuracies.append(self.ANN.accuracy(input, target))

    def save_model(self):
        self.ANN.save(size=env.size, level=i+1)
        self.write_db("cases/size_{}".format(self.env.size), self.buffer)

    def plot(self):
        self.episodes = np.arange(self.G)
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
        ax.plot(self.episodes, self.losses, color='tab:orange', label="Loss")
        ax.plot(self.episodes, self.accuracies, color='tab:blue', label="Accuracy")
        plt.legend()
        plt.show()

    def generate_cases(self):
        cases = []
        self.MCTS.eps = 1
        print("Generating training cases")
        for i in tqdm(range(self.G)):
            self.env.reset()
            self.MCTS.init_tree()
            while not self.env.is_game_over():
                D = self.MCTS.search(self.env, self.M)
                cases.append((self.env.flat_state, D))
                self.env.move(self.env.all_moves[np.argmax(D)])
            MCTS.eps *= 0.99
        self.write_db("cases/size_{}".format(self.env.size), cases)

    def plot_level_accuracies(self, levels):
        cases = self.load_db("cases/size_{}".format(self.env.size))
        losses = []
        accuracies = []
        for l in levels:
            self.ANN.load(self.env.size, l)
            input, target = list(zip(*cases))
            losses.append(self.ANN.get_loss(input, target))
            accuracies.append(self.ANN.accuracy(input, target))
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
        plt.xlabel("episodes")
        fig.axes[0].set_title("Size {}".format(self.env.size))
        ax.plot(levels, accuracies, color='tab:blue', label="Accuracy")
        ax.plot(levels, losses, color='tab:orange', label="Loss")
        plt.legend()
        plt.show()

    def write_db(self, filename, cases):
        inputs, targets = list(zip(*cases))
        with open(filename+'_inputs.txt', 'a') as file:
            np.savetxt(file, inputs)
        with open(filename+'_targets.txt', 'a') as file:
            np.savetxt(file, targets)

    def load_db(self, filename):
        import time
        start = time.time()
        inputs = np.loadtxt(filename+'_inputs.txt')
        targets = np.loadtxt(filename+'_targets.txt')
        cases = list(zip(inputs, targets))
        return cases


if __name__ == '__main__':
    # MCTS/RL parameters
    board_size = 5
    G = 500
    M = 500
    save_interval = 50
    buffer_size = 500
    batch_size = 150

    # ANN parameters
    activation_functions = ["linear", "sigmoid", "tanh", "relu"]
    optimizers = ["Adagrad", "SGD", "RMSprop", "Adam"]
    alpha = 0.001  # learning rate
    H_dims = [math.floor(2 * (2 + 2 * board_size ** 2) / 3) + board_size ** 2] * 3
    io_dim = board_size * board_size  # input and output layer sizes
    activation = activation_functions[3]
    optimizer = optimizers[3]
    epochs = 5

    ANN = ANN(io_dim, H_dims, alpha, optimizer, activation, epochs)
    MCTS = MonteCarloTreeSearch(ANN, c=1., eps=1, stoch_policy=True)
    env = HexGame(board_size)
    RL = RL(G, M, env, ANN, MCTS, save_interval, buffer_size, batch_size)

    # Run RL algorithm and plot results
    #RL.run()

    # Generate training cases
    #RL.generate_cases()

    # Plot model accuracies and losses
    levels = np.arange(0, 201, 50)
    RL.plot_level_accuracies(levels)
