import math
import random
import time

import pandas as pd
import numpy as np
import equationtree as et
import timeSeries as ts
import inout

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    df = inout.readInCSV("data/gasincome.csv")
    colNameList = ['G', 'Y']
    listOfTimes = []

    ''' 
    # count the number of valid equations created
    count = 0
    error = 0
    for t in range(0, 20):
        start = time.time()
        for x in range(0, 10):
            tempTree = et.createRandomEquationTree(90, False, 0, 10, 10, 1, s, colNameList, 3, 1)
            count += 1
            try:
                tempTree.getValue()
            except ValueError:
                error += 1
            except OverflowError:
                error += 1
            except ZeroDivisionError:
                error += 1

        print(f"mean error rate:{error/count}")
    '''

    tempTree1 = et.createRandomEquationTree(10, False, 0, 10, 10, 1, df, colNameList, 3, 1)
    et.printAsFormula(tempTree1, True);
    print()

    # first only use itself for predicting
    # drop 'Y' and transform the dataFrame to a Series
    df.drop(columns=['Y'], inplace=True)

    s = pd.Series(df['G'], index=df.index)

    ts.evaluateTimeSeries(s, tempTree1, 5)
