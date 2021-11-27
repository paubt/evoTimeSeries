import math
import random
import sys

"""
allowed functions:
    one:

"""


# define here functions for the equations

def minus(a, b):
    return a - b


def plus(a, b):
    return a + b


def multiplication(a, b):
    return a * b


def division(a, divisor):
    # check that denominator unequal zero
    assert divisor != 0
    return a / divisor


def uniformRandom(a, b):
    return random.uniform(a, b)


def normalDistribution(a, b):
    return random.normalvariate(a, b)


# return the max value: x = 710
def sinHyper(a):
    try:
        return math.sinh(a)
    except OverflowError:
        if a > 0:
            return math.sinh(710)
        else:
            return math.sinh(-710)


def cosHyper(a):
    try:
        return math.cosh(a)
    except OverflowError:
        if a > 0:
            return math.cosh(710)
        else:
            return math.cosh(-710)


# helper function to translate from function name to operator character
dictFunNameToSym = {
    "division": '/',
    "minus": '-',
    "plus": '+',
    "multiplication": '*',
    "exp": "exp",
    "sqrt": "sqrt",
    # trigonometric functions
    "sin": "sin",
    "cos": "cos",
    "tan": "tan",

}


# helper function for formula printing
def printAsFormula(root, verbose):
    if verbose:
        print("function : ", end="")
    root.printFormula()
    if verbose:
        print(f" = {root.getValue()}")


# base node for the tree
# the parent for all other types of nodes
class Node:
    # add keyword pass cause we dont wont to add any other stuff to the class
    pass

    def update(self):
        pass

    def getValue(self):
        pass

    def printFormula(self):
        pass


class OneChildNode(Node):
    def __init__(self, operation):
        # the child
        self.child = None
        # function that only takes one input
        self.operation = operation

    # insert new child
    def insert(self, child):
        self.child = child

    # propagate the update to the leaves so the random variables can change
    def update(self):
        self.child.update()

    # calculate the value of the subtree and return it
    # if tree empty use zero
    def getValue(self):
        if self.child is None:
            return self.operation(0)
        else:
            return self.operation(self.child.getValue())

    def printFormula(self):
        print(str(dictFunNameToSym.get(self.operation.__name__)) + "(", end="")
        self.child.printFormula()
        print(")", end="")


class TwoChildNode(Node):
    def __init__(self, operation):
        self.left = Node
        self.right = Node
        self.operation = operation

    # insert new child
    def insert(self, left, right):
        self.left = left
        self.right = right

    # propagate the update to the leaves so the random variables can change
    def update(self):
        self.left.update()
        self.right.update()

    # calculate the value of the two subtrees and return the operation
    # if tree empty use zero
    def getValue(self):
        # get the left value
        if self.left is None:
            valueLeft = 0
        else:
            valueLeft = self.left.getValue()
        # get the right value
        if self.right is None:
            valueRight = 0
        else:
            valueRight = self.right.getValue()
        # return the operation
        return self.operation(valueLeft, valueRight)

    def printFormula(self):
        self.left.printFormula()
        print(dictFunNameToSym.get(self.operation.__name__), end="")
        self.right.printFormula()


class Leaf(Node):
    def __init__(self, value):
        self.value = value

    def getValue(self):
        return self.value

    def update(self):
        pass

    def printFormula(self):
        if self.value == math.pi:
            print("pi", end="")
        elif self.value == math.e:
            print("e", end="")
        else:
            print(self.value, end="")


# node that produces a random float with: min < x < max
class randLeaf(Node):
    # constructor
    def __init__(self, minimum, maximum):
        self.minimum = minimum
        self.maximum = maximum
        self.value = random.uniform(minimum, maximum)

    # updates the random values
    def update(self):
        self.value = random.uniform(self.minimum, self.maximum)

    # getter for the value
    def getValue(self):
        return self.value

    # print the value
    def printFormula(self):
        approx = u'\u2248'
        print(f"r{approx}{format(self.value, '.3f')}", end="")


# node that draws from a random distribution
class nDistLeaf(Node):
    def __init__(self, mu, sigma):
        self.mu = mu
        self.sigma = sigma
        self.value = random.normalvariate(self.mu, self.sigma)

    def update(self):
        self.value = random.normalvariate(self.mu, self.sigma)

    def getValue(self):
        return self.value

    def printFormula(self):
        approx = u'\u2248'
        print(f"N({self.mu},{self.sigma}){approx}{format(self.value, '.3f')}", end="")
