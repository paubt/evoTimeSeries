import math
import sys

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import equationtree as et


# note this function can be outplayed by using high maxLag and thous evaluating only small part of the series
def rssSeries(originalSeries, predictionSeries, maxLag):
    assert len(originalSeries) == len(predictionSeries)
    rss = 0
    # iterate trough two series excluding the first maxLag values
    for i in range(maxLag, len(originalSeries)):
        try:
            if predictionSeries.iloc[i] >= np.inf:
                raise OverflowError
            rss += pow(originalSeries.iloc[i] - predictionSeries.iloc[i], 2)
        # this means adding the next error would overflow the int thus evaluating to nan
        except OverflowError:
            return np.nan
        except ZeroDivisionError:
            return np.nan
        except RuntimeWarning:
            return np.nan
    return rss


def predictTreeOnSeries(series, tree):
    # use a tree and series to obtain prediction as list/Series
    # prediction list
    predictionList = list()
    # go through the Series and make the predictions
    for t in range(0, len(series)):
        # propagate the new time t trough the tree
        tree.update(t)
        # try safe the predictionList in a series
        # if there is a logical error (syntax, domain,...) this throws a error
        try:
            predictionList.append(tree.getValue())
        # if error thrown append nan to the list for the time t
        except ValueError:
            predictionList.append(np.nan)
        except OverflowError:
            predictionList.append(np.nan)
        except ZeroDivisionError:
            predictionList.append(np.nan)
    # transform predictionList to a Series
    prediction = pd.Series(predictionList)
    return prediction


def randomSearchV1(series, maxLag, n, verbose):
    # repeat n times
    assert n >= 0
    # prediction list
    predictionList = list()
    # variable for best so far
    bestTree = None
    bestValueOfRSS = sys.maxsize
    # repeat n times
    while n > 0:
        n -= 1
        # create new random tree
        tempTree = et.createRandomEquationTree(10, False, 0, 10, 10, 1, series, 'G', maxLag, 1)
        # obtain prediction
        prediction = predictTreeOnSeries(series, tempTree)
        # reindex
        prediction.rename(lambda x: 1960 + x, inplace=True)
        # calculate RSS residual sum of squares (sum of prediction error's)
        rss = rssSeries(series, prediction, maxLag)
        # check if new best
        if rss < bestValueOfRSS:
            bestTree = tempTree
            bestValueOfRSS = rss
            if verbose:
                print(f"n = {n} new best found with RSS of :{bestValueOfRSS} with function   ", end="")
                et.printAsFormula(bestTree, False)
    # plot the original and the best prediction
    printOriginalAndPrediction(series, bestTree, 0)
    return bestTree


def randomSearchV2(series, maxLag, n, verbose):
    # n is the amount of iterations to do the random search
    # repeat n times
    assert n >= 0
    # prediction list
    predictionList = list()
    # variable for best so far
    bestTree = None
    bestValueRSSLength = sys.maxsize
    # repeat n times
    while n > 0:
        n -= 1
        # create new random tree
        tempTree = et.createRandomEquationTree(10, False, 0, 10, 10, 1, series, 'G', maxLag, 1)
        # use the prediction function to obtain predictions as series
        prediction = predictTreeOnSeries(series, tempTree)
        # reindex
        prediction.rename(lambda x: 1960 + x, inplace=True)
        # calculate RSS residual sum of squares (sum of prediction error's)
        rss = rssSeries(series, prediction, maxLag)
        # length of the tree
        length = et.countElementsOfTree(tempTree)
        # "fitness" the weighted sum of length and rss
        fitness = rss + 15 * length
        # check if new best
        if fitness < bestValueRSSLength:
            bestTree = tempTree
            bestValueRSSLength = fitness
            if verbose:
                print(f"n = {n} new best found with RSS of :{rss} and fitness:{bestValueRSSLength} with function   ",
                      end="")
                et.printAsFormula(bestTree, False)
    # plot the original and the best prediction
    printOriginalAndPrediction(series, bestTree, 0)
    return bestTree


def getFitnessECountRSS(series, tree, maxLag):
    # use the prediction function to obtain predictions as series
    prediction = predictTreeOnSeries(series, tree)
    # reindex
    prediction.rename(lambda x: 1960 + x, inplace=True)
    # calculate RSS residual sum of squares (sum of prediction error's)
    rss = rssSeries(series, prediction, maxLag)
    # length of the tree
    length = et.countElementsOfTree(tree)
    # "fitness" the weighted sum of length and rss
    fitness = rss + 15 * length
    return fitness


def fitnessNTimes(series, tree, maxLag, n):
    # sum of RSS
    sRss = 0
    # repeat the prediction n times to get a mean value cause of the random elements
    for i in range(0, n):
        # use the prediction function to obtain predictions as series
        prediction = predictTreeOnSeries(series, tree)
        # reindex
        prediction.rename(lambda x: 1960 + x, inplace=True)
        # calculate RSS residual sum of squares (sum of prediction error's)
        rss = rssSeries(series, prediction, maxLag)
        sRss += rss
    # calculate mean RSS
    meanRss = sRss/n
    # length of the tree
    length = et.countElementsOfTree(tree)
    # "fitness" the weighted sum of length and rss
    fitness = meanRss + 15 * length
    return fitness


def localHillClimb(series, colName, tree, maxLag, iterations, neighbourCount, verbose=False, plot=False):
    # assertions
    assert iterations > 0
    assert neighbourCount > 0
    # calculate alpha for the transparency of the graphs of each iteration
    alpha = 0.1
    # this is where the current tree through the iterations is stored
    currentTree = tree
    currentTreeFitness = sys.maxsize
    plt.plot(series, color="C2")
    for i in range(0, iterations):
        # print some stuff
        if verbose:
            print(f"\niteration nr: {i}\n")
            et.printAsFormula(currentTree, True)
        # the variables store the best trough the neighborhood search
        tempBestTree = currentTree
        tempBestTreeFitness = getFitnessECountRSS(series, tempBestTree, maxLag)
        for n in range(0, neighbourCount):
            # copy the tree
            newTree = currentTree.copyMe()
            # mutate the new tree
            et.mutateTree(newTree, series, colName, maxLag)
            # asses the fitness of the tree
            tempFitness = fitnessNTimes(series, newTree, maxLag, 50)
            if verbose:
                print(f"the mutated tree nr {n} is with fitness {tempFitness}:")
                et.printAsFormula(newTree, False)
            # if the the mutated tree / new tree is better than replace it
            if tempFitness < tempBestTreeFitness:
                if verbose:
                    print("found a better one")
                tempBestTree = newTree
                tempBestTreeFitness = tempFitness
        # set the best of the neighborhood as current tree for the next generation
        currentTree = tempBestTree
        if plot:
            pred = predictTreeOnSeries(series, currentTree)
            pred.rename(lambda x: 1960 + x, inplace=True)
            plt.plot(pred, color="C1", alpha=alpha)
    plt.plot(series, color="C2")
    plt.show()
    tree = currentTree


def printOriginalAndPrediction(series, predTree, maxLag):
    # list to safe the "predictions" of the tree in
    predictionList = list()
    # go through the Series
    for t in range(0, len(series)):
        # propagate the new time t trough the tree
        predTree.update(t)
        # try safe the predictionList in a series
        # if there is a logical error (syntax, domain,...) this throws a error
        try:
            predictionList.append(predTree.getValue())
        # if error thrown append nan to the list for the time t
        except ValueError:
            predictionList.append(np.nan)
        except OverflowError:
            predictionList.append(np.nan)
        except ZeroDivisionError:
            predictionList.append(np.nan)
    # transform predictionList to a Series
    prediction = pd.Series(predictionList)
    # reindex
    prediction.rename(lambda x: 1960 + x, inplace=True)

    plt.plot(series)
    plt.plot(prediction)
    plt.show()
