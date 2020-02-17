from actor import Actor
from criticTable import CriticTable
from criticNN import CriticNN
from env import Board
from progressbar import ProgressBar
import numpy as np
import time
import matplotlib.pyplot as plt



class Agent:
    def __init__(self, env, alphaActor, alphaCritic, lam, eps, gamma, criticType, hiddenLayers, hiddenLayerSize):
        self.env = env
        self.eps = eps
        self.epsDecay = epsDecay
        self.actor = Actor(alphaActor, lam, gamma)
        self.criticType = criticType
        if criticType == 0: #use criticTable
            self.critic = CriticTable(alphaCritic, lam, gamma)
        else: #use criticNN
            state = env.getState()
            inputLayerSize = len(state)
            self.critic = CriticNN(alphaCritic, lam, gamma, hiddenLayers, hiddenLayerSize, inputLayerSize)

    def learn(self, runs):
        eps = self.eps
        epsDecay = self.epsDecay
        pegsLeft = []
        iterationNumber = []
        iteration = 0
        start_time = time.time()
        #pbar = ProgressBar()
        for i in range(runs):#pbar(range(runs)):
            iteration += 1
            self.env.reset()
            self.actor.resetEligibilities()
            self.critic.resetEligibilities()
            # initialize new state values and (s,a)-pairs for start (s,a)
            state = self.env.getState()
            if self.criticType == 0:
                self.critic.createEligibility(state)
                self.critic.createStateValues(state)

            validActions = self.env.generateActions()
            self.actor.createSAPs(state, validActions)
            self.actor.createEligibilities(state, validActions)
            action = self.actor.findNextAction(state, validActions, eps)

            while len(validActions) > 0:
                lastState = state # save current state before new action
                self.env.execute(action)
                state = self.env.getState()
                validActions = self.env.generateActions()

                if self.criticType == 0:
                    self.critic.createEligibility(state)
                    self.critic.createStateValues(state)

                self.actor.createSAPs(state, validActions)
                self.actor.createEligibilities(state, validActions)

                reinforcement = self.env.reinforcement()
                action = self.actor.findNextAction(state, validActions, eps)

                self.actor.updateCurrentEligibility(state, action)
                td_error = self.critic.findTDError(reinforcement, lastState, state)

                if self.criticType == 0:
                    self.critic.updateCurrentEligibility(lastState)
                    self.critic.updateStateValues()
                else:
                    self.critic.fit(reinforcement, lastState, state, td_error)

                self.critic.updateEligibilities() #flyttet utenfor, siden denne skal begge typer critics utføre

                self.actor.updateSAPs(td_error)
                self.actor.updateEligibilities()

            if self.criticType == 1:
                print("ep", i,"  Pegs", self.env.numberOfPegsLeft(), " LastState Value", "%.3f" % self.critic.valueState(lastState), " eps", "%.3f" % eps)
            pegsLeft.append(self.env.numberOfPegsLeft())
            iterationNumber.append(i)

            eps = eps * epsDecay
        time_spent = time.time() - start_time
        print("Time spent", time_spent)
        plt.plot(iterationNumber, pegsLeft)
        plt.show()

    def runGreedy(self, delay):
        start_time = time.time()
        self.env.reset()
        self.env.draw()
        reinforcement = 0
        state = self.env.getState()
        validActions = self.env.generateActions()
        action = self.actor.findNextAction(state, validActions, 0)
        while len(validActions) > 0:
            self.env.draw(delay)
            self.env.execute(action)
            reinforcement = self.env.reinforcement()
            state = self.env.getState()
            self.actor.createSAPs(state, self.env.generateActions())
            validActions = self.env.generateActions()
            action = self.actor.findNextAction(state, validActions, 0)
        self.env.draw()


if __name__ == '__main__':
    type = 0
    size = 5
    initial = [(2,1)] # start with hole in (r,c)
    random = 0 # remove random pegs
    env = Board(type, size, initial, random)
    delay = 0.5 # for visualization

    alpha = 0.001
    lam = 0.85  #lambda
    gamma = 0.9
    eps = 1
    epsDecay = 0.995
    criticValuation = 1 # neural net valuation of states.
    hiddenLayerSize = 5
    hiddenLayers = 1
    agent = Agent(env, alpha, alpha, lam, eps, gamma, criticValuation, hiddenLayers, hiddenLayerSize)

    agent.learn(1000)
    visualize = input('Do you want to visualize the solution? (y/n): ')
    if visualize == 'y':
        agent.runGreedy(delay)
