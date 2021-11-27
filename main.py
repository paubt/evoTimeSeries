import math
import random

import pandas as pd
import numpy as np
import equationtree as et



# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    root = et.TwoChildNode(et.division)
    child1 = et.OneChildNode(math.sqrt)
    child2 = et.OneChildNode(math.sin)
    constEnd = et.Leaf(12)
    randL1 = et.randLeaf(1, 2)
    nDRand1 = et.nDistLeaf(2,1)

    root.insert(child1, child2)
    child1.insert(nDRand1)
    child2.insert(randL1)

    et.printAsFormula(root, True)
    root.update()
    et.printAsFormula(root, True)

