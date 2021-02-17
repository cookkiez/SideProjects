from random import randrange, random, shuffle
from math import ceil
from copy import deepcopy
from Agent import Agent

class Population:
    ## Our saved solutions
    # population = []
    ## Sum of all fitness values
    # popFitness = 0
    ## Save the best fitness and index of the solution in the population
    # bestFitnessIndex = 0
    # bestFitness = 0
    ## Number of solutions to save
    # popSize = 0
    ## Distance matrix for locations
    # distMatrix = []

    ## Initalize the population, build random (viable) paths to use as solution
    def __init__(self, n, bag, distMatrix):
        self.popFitness = 0
        self.bestFitnessIndex = 0
        self.bestFitness = 0
        self.popSize = n
        self.distMatrix = distMatrix
        self.population = []

        
        for i in range(0, n):
            path = self.randomPath(bag)
            a = Agent(path)
            self.population.append(a)
        
    ## Build a random path using a bag of indexes, e.g. for vertices 1,2,3 the bag is [1,2,3]
    def randomPath(self, bag):
        tempBag = bag.copy()
        ## Randomly select the starting vertex and remove it from choosing again
        firstEl = randrange(len(tempBag))
        tempBag.remove(firstEl)
        path = [firstEl]
        ## Copy the distance matrix
        tempDistMatrix = deepcopy(self.distMatrix)
        for row in tempDistMatrix:
            row[firstEl] = 0
        ## Iterate until full path has been built
        k = 1
        ii = 0
        while k < len(bag):
            ## Choose previous element and get its distances
            prevEl = path[k - 1]
            dists = tempDistMatrix[prevEl]
            
            ## Get sum of distances and calculate ratio for each vertex, then sum them up to get 'probabilities'
            ## Vertices that have a smaller distance have a bigger probability
            sumOfDists = sum(dists)
            probs = [(dist / sumOfDists) for dist in dists]
            newProbs = []
            for prob in probs:
                if prob == 0:
                    newProbs.append(0)
                else:
                    newProbs.append(1 / prob)
            probs = newProbs
            sumOfProbs = sum(probs)
            probs = [(prob / sumOfProbs) for prob in probs]
            for i in range(1, len(probs)):
                probs[i] += probs[i - 1]
            
            ## Randomly choose a vertex to add to path
            rand = random()
            nextEl = 0
            for prob in probs:
                if rand < prob:
                    for row in tempDistMatrix:
                        row[prevEl] = 0
                    path.append(nextEl) 
                    k += 1  
                    break
                nextEl += 1    
        return path

    ## Print current solutions and their fitness values
    def print(self):
        for a in self.population:
            print(a.path, a.fitnessValue)

    ## Calculates fitness of the population
    def calculateFitness(self):
        ## For saving best fitness value
        bestFitness = -100
        bestIndex = 0
        i = 0
        self.popFitness = 0
        ## Iterate over the population to sum the fitness of the whole population and 
        ## calculate individual fitnesses (also save best fitness value)
        for pop in self.population:
            self.popFitness += pop.fitness(self.distMatrix)
            if pop.fitnessValue > bestFitness:
                bestFitness = pop.fitnessValue
                bestIndex = i
            i += 1
        
        ## Save the best fitness value and its index in the population
        self.bestFitness = bestFitness
        self.bestFitnessIndex = bestIndex

    ## Mutation function, for each individual, mutate it with 'mutateRatio' probability
    ## Never mutate the best solution, which is on index 0 at this point
    def mutation(self, mutateRatio):
        i = 0
        for pop in self.population:
            rand = random()
            if not i == 0 and rand < mutateRatio:
                pop.mutate(mutateRatio)
                self.population[i] = pop
            i += 1            

    ## Calculate fitness of group in tournament to use for calculating probabilities
    def groupFitness(self, group):
        fitSum = 0
        for agent in group:
            fitSum += agent.fitnessValue
        return fitSum

    ## Make individuals of a group compete in a tournament, choose individual to 
    ## proceed to next round with probability 'p = fitnessValue / groupFitness(group)'
    def tournament(self, group, fitnessSum):
        ## When only two are left, return and use them for crossover
        if len(group) <= 2: 
            return group
        ## Calculate the number of individuals to proceed into next round
        numberOfNext = int(ceil(len(group) / 2))
        newGroup = []
        ## Build group for the next round of the tournament
        while len(newGroup) < numberOfNext:
            newAgent = None
            ## For every individual in the group select it with probability p
            for agent in group:
                prob = agent.fitnessValue / fitnessSum
                rand = random()
                ## If the individual is selected, add it to the new group and break from this loop
                if rand < prob and not agent == None:
                    newGroup.append(agent)
                    newAgent = agent
                    break
            ## If an individual has been selected, remove it from current group, so as to not select it again
            if not newAgent == None:
                group.remove(newAgent)
        ## Recursively call the function with new group
        return self.tournament(newGroup, self.groupFitness(newGroup))

    ## Select individuals for crossover and cross them over using tournament selection
    def tournamentSelection(self, k, crossoverRate):
        ## Save best individual
        bestPop = self.population[self.bestFitnessIndex]
        newPop = [bestPop]

        ## Get group size from parameters
        numberOfParticipants = k

        ## Do tournament selection over the population, generate 'crossoverRate * popSize' children
        tempPop = self.population.copy()
        while len(newPop) < (self.popSize * crossoverRate):
            ## Shuffle population randomly and take the first 'numberOfParticipants' to get a group 
            ## that will compete in a tournament
            shuffle(tempPop)
            tournamentGroup = tempPop[:numberOfParticipants]

            ## Get 2 winners of the tournament and perform crossover, then add child to new population
            winners = self.tournament(tournamentGroup, self.groupFitness(tournamentGroup))
            newAgent = self.crossover(winners[0], winners[1])
            newPop.append(newAgent)

        ## Fill the population up with new solutions to expand the search space
        while len(newPop) < self.popSize: 
            newPop.append(Agent(self.randomPath(list(range(0, len(self.population[0].path))))))

        ## Save new population
        self.population = newPop.copy()

    ## Select individuals randomly, based on their fitness value and perform crossover
    def selection(self, crossoverRate):
        ## Save the best individual
        bestPop = self.population[self.bestFitnessIndex]
        newPop = [bestPop]

        ## Choose 'popSize * crossoverRate' individuals for parents
        numberForCrossover = int(ceil(self.popSize * crossoverRate))
        while len(newPop) < numberForCrossover:
            ## Build a new population over which to perform crossover
            ## Choose each individual with probability according to its fitness value
            ## (with bigger populations the general fitness/sum(fitness) doesn't really work, so 
            ## I multiply it with 'popSize / 6' to get a better representation)
            for pop in self.population:
                probability = (pop.fitnessValue * (self.popSize / 6)) / self.popFitness
                rand = random()
                if rand < probability:
                    newPop.append(pop)

        ## Save the best individual and reset the current population
        self.population = [bestPop]
        ## Build a new population by performing crossover over previously selected individuals
        ## Iterate over all individuals and choose a partner randomly
        for pop in newPop:
            i = randrange(len(newPop))
            newAgent = self.crossover(pop, newPop[i])
            self.population.append(newAgent)
        ## If the build population is not big enough, add some random solutions (this expands the search space)
        while len(self.population) < self.popSize: 
            self.population.append(Agent(self.randomPath(list(range(0, len(self.population[0].path))))))

    def getBestAgent(self, agentArr):
        bestAgent = Agent([0,1])
        bestAgent.fitnessValue = -1000

        for agent in agentArr:
            agent.fitness(self.distMatrix)
            if agent.fitnessValue > bestAgent.fitnessValue:
                bestAgent = agent
        
        return bestAgent

    ## Perform crossover over two agents
    def crossover(self, agent1, agent2):
        ## Extract path from each agent and perform crossover over the paths
        pot1 = agent1.path
        pot2 = agent2.path
        
        ## Perform different crossovers and choose the child that has the best fitness value
        agentArr = []
        newAgent = None

        newPath = self.rekCrossoverStartEnd(pot1, pot2, 0, len(pot2)- 1, [], [])
        agentArr.append(Agent(newPath))

        newPath1 = self.crossoverDavis(pot1, pot2)
        newPath2 = self.crossoverDavis(pot2, pot1)
        agentArr.append(Agent(newPath1))
        agentArr.append(Agent(newPath2))

        newAgent = self.getBestAgent(agentArr)
        ## Return new agent using the build path
        return newAgent

    ## Slice paths into three parts and use the 2nd part of the 1st path for new path
    ## Get vertices from 3rd part of 2nd path on (in order) and put them in the new path in the same order
    def crossoverDavis(self, pot1, pot2):
        ## Choose slice length and copy the first path
        sliceLen = int(len(pot1) / 3)
        newPath = pot1.copy()
        
        ## Reset the elements that come from the second path
        for x in range(0, sliceLen):
            newPath[x] = -1
        for x in range(sliceLen * 2, len(newPath)):
            newPath[x] = -1

        ## Add vertices to new path in order, according to Davis
        i = sliceLen * 2
        for x in range(sliceLen * 2, len(pot2)):
            el = pot2[x]
            if el not in newPath:
                newPath[i] = el
                i += 1
                if i == len(pot2):
                    i = 0
        for x in range(0, sliceLen * 2):
            el = pot2[x]
            if el not in newPath:
                newPath[i] = el
                i += 1
                if i == len(pot2):
                    i = 0
    
        return newPath

    ## Recursively build a new path from the given paths
    ## Use the first agent to start building from the start and the second agent to start building from the end
    ## indeks1 starts at 0 and increases, indeks2 starts at len(pot2) and decreases
    def rekCrossoverStartEnd(self, pot1, pot2, indeks1, indeks2, zacetekPath, konecPath):
        ## Connect the start and the end to see if we have found a solution
        fullList = zacetekPath.copy()
        fullList.extend(konecPath)

        if indeks1 > len(pot1):
            indeks1 = 0
        if indeks2 < 0:
            indeks2 = len(pot2) - 1

        ## If solution has been found, return it
        if not fullList == None and len(set(fullList) & set(pot1)) == len(pot1):
            return fullList

        ## Check if indexes have not gone over the limit and get the current element from each path
        el1 = -1
        el2 = -1
        if indeks1 < len(pot1):
            el1 = pot1[indeks1]
        if indeks2 >= 0:    
            el2 = pot2[indeks2]

        ## If elements are viable and they are not already on the start or end of our new path, 
        ## add them to the start (el1) or to the end (el2)
        if not el1 == -1 and el1 not in zacetekPath and el1 not in konecPath:
            if zacetekPath == []:
                zacetekPath = [el1]
            else:
                zacetekPath.append(el1)
        if not el2 == -1 and el2 not in zacetekPath and el2 not in konecPath:
            if konecPath == []:
                konecPath = [el2]
            else:    
                konecPath.append(el2)
        indeks2 -= 1
        indeks1 += 1
        ## Recursively call the function with the added elements and new indeks1, indeks2
        return self.rekCrossoverStartEnd(pot1, pot2, indeks1, indeks2, zacetekPath, konecPath)