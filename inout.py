import pandas as pd
import numpy as np


def readInCSV(path):
    arr = pd.read_csv(path)

    return arr
