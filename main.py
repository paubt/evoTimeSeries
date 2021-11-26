import math

import pandas as pd
import numpy as np
import equationtree as et


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    root = et.OneChildNode(math.exp)
    child = et.OneChildNode(math.cos)

    root.insert(child)

    t = root.getValue()
    print(t)

    print_hi('PyCharm')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
