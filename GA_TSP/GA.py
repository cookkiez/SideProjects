from random import betavariate, random, randrange, shuffle
from copy import deepcopy
import csv
import numpy
from Agent import Agent
from Population import Population

file = open("distances.txt", "r")
dists = file.read().split("\n")

razdalje = []

for d in dists:
    r = []
    vmes = d.split()
    for v in vmes:
       r.append(int(v))
    if not r: 
        break
    razdalje.append(r)

n = 1000
mutateRatio = 0.4
crossoverRatio = 0.75

pops = Population(n, list(range(0, len(razdalje))), razdalje)
popsSel = Population(n, list(range(0, len(razdalje))), razdalje)
popsSel.population = []
popsSel.population = deepcopy(pops.population)

sel = 0
prevSel = 0
tour = 0
prevTour = 0

for i in range(0, 1500):
    if tour > 50 and sel > 50:
        break

    pops.calculateFitness()
    k = n / 10
    pops.tournamentSelection(int(k), crossoverRatio)
    pops.mutation(mutateRatio)

    popsSel.calculateFitness()
    popsSel.selection(crossoverRatio)
    popsSel.mutation(mutateRatio)

    print("generation: ", i)
    print("Best fitness for tournamnent selection: ", pops.bestFitness)
    print("Best fitness for random selection: ", popsSel.bestFitness)
    if prevSel == popsSel.bestFitness:
        sel += 1
    else:
        prevSel = popsSel.bestFitness
        sel = 0
    if prevTour == pops.bestFitness:
        tour += 1
    else:
        prevTour = pops.bestFitness
        tour = 0

bestTour = pops.population[0]
print(bestTour.path, bestTour.fitnessValue, bestTour.length)

bestSel = popsSel.population[0]
print(bestSel.path, bestSel.fitnessValue, bestSel.length)
