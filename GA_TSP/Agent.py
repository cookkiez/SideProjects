from random import randrange, random

## Stores an individual solution 
class Agent:
    ## The solution, its fitness value and its length
    ## (because the fitness value is 1/(length**2))
    # path = []
    # fitnessValue = 0
    # length = 0

    ## Initialize the individual
    def __init__(self, p):
        self.path = p
        self.fitnessValue = 0
        self.length = 0

    ## Calculate fitness of this individual
    ## Iterate over its solution and sum the costs
    def fitness(self, distMatrix):
        sum = 0
        
        for i in range(1, len(self.path)):
            j = self.path[i] 
            k = self.path[i - 1]
            sum += distMatrix[j][k]
        fit = 1.0/(sum)
        self.length = sum
        self.fitnessValue = fit
        return fit

    ## Randomly mutate this individual
    ## Iterate over its solution, every index(vertex/city) of the solution has a 'p = mutateRatio'
    ## probability to be mutated, this means that it is switched with another random index(vertex/city)
    def mutate(self, mutateRatio):
        i = 0
        for p in self.path:
            rand = random()
            if rand < mutateRatio:
                j = randrange(len(self.path))
                while not j == i:
                    j = randrange(len(self.path))
                temp = self.path[i]
                self.path[i] = self.path[j]
                self.path[j] = temp
            i += 1

