import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import equationtree as et


def evaluateTimeSeries(series, maxLag):
    print(series)
    # create a tree with oldValueLeaves on the series with max lag of 5
    tempTree1 = et.createRandomEquationTree(10, False, 0, 10, 10, 1, series, 'G', maxLag, 1)
    # list to safe the "predictions" of the tree in
    predictionList = list()
    # start of the index of the series
    year = 1960
    # go through the Series
    for t in range(0, len(series)):
        print(f"this is tree at t={t}", end="")
        # propagate the new time t trough the tree
        tempTree1.update(t)
        # print the tree
        et.printAsFormula(tempTree1, True)
        # try safe the predictionList in a series
        # if there is a logical error (syntax, domain,...) this throws a error
        try:
            predictionList.append(tempTree1.getValue())
        # if error thrown append nan to the list for the time t
        except ValueError:
            print(" = mathDomainError")
            predictionList.append(np.nan)
        except OverflowError:
            print(" = OverflowError = to big")
            predictionList.append(np.nan)

        except ZeroDivisionError:
            print(" = ZeroDivisionError")
            predictionList.append(np.nan)
        year += 1
    # transform predictionList to a Series
    prediction = pd.Series(predictionList)
    # reindex
    prediction.rename(lambda x: 1960+x, inplace=True)
    print(prediction)

    plt.plot(series)
    plt.plot(prediction)
    plt.show()
