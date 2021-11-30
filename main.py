import math
import random
import time

import pandas as pd
import numpy as np
import equationtree as et
import inout

# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    s = inout.readInCSV("data/gasincome.csv")
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

    tempTree1 = et.createRandomEquationTree(30, False, 0, 10, 10, 1, s, colNameList, 3, 1)
    et.printAsFormula(tempTree1, True)
    print()
    et.mutateTree(tempTree1, s, colNameList, 1)
    print()
    et.printAsFormula(tempTree1, True)
