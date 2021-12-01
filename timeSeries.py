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


def randomSearch(series, maxLag, n, verbose):
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
        # clear prediction list
        predictionList.clear()
        # go through the Series and make the predictions
        for t in range(0, len(series)):
            # propagate the new time t trough the tree
            tempTree.update(t)
            # try safe the predictionList in a series
            # if there is a logical error (syntax, domain,...) this throws a error
            try:
                predictionList.append(tempTree.getValue())
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
    printOriginalAndPrediction(series, bestTree,0)
    return bestTree


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
