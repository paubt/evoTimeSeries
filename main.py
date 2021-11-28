import math
import random

import pandas as pd
import numpy as np
import equationtree as et
import inout

# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    s = inout.readInCSV("data/gasincome.csv")
    '''
    print(s)
    
    root = et.TwoChildNode(et.plus)
    child1 = et.OneChildNode(math.sqrt)
    child2 = et.OneChildNode(math.sqrt)
    constEnd = et.Leaf(12)
    randL1 = et.RandLeaf(1, 2)
    nDRand1 = et.NDistLeaf(2, 1)
    oValue1 = et.OldValueLeaf(s, 'G', 1, 1)
    oValue2 = et.OldValueLeaf(s, 'Y', 2, 1)

    root.insert(child1, child2)
    child1.insert(oValue1)
    child2.insert(oValue2)

    et.printAsFormula(root, True)
    root.update(2)
    et.printAsFormula(root, True)
    root.update(3)
    et.printAsFormula(root, True)
    root.update(4)
    et.printAsFormula(root, True)
    root.update(5)
    et.printAsFormula(root, True)
    print("\n\n")
    '''

    colNameList = ['G', 'Y']
    testTree = et.createRandomEquationTree(10, True, 0, 10, 10, 1, s, colNameList, 3, 1)

