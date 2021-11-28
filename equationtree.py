import math
import random


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


def power(base, exponent):
    return math.pow(base, exponent)


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
    "power": "^",
    # trigonometric functions
    "sin": "sin",
    "cos": "cos",
    "tan": "tan",

}
# helper translator to subscript
SUB = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")


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

    def update(self, t):
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
    def update(self, t):
        self.child.update(t)

    # calculate the value of the subtree and return it
    # if tree empty use zero
    def getValue(self):
        if self.child is None:
            return self.operation(0)
        else:
            return self.operation(self.child.getValue())

    def printFormula(self):
        print(str(dictFunNameToSym.get(self.operation.__name__)) + "(", end="")
        if self.child is None:
            print("NAN", end="")
        else:
            self.child.printFormula()
        print(")", end="")


class TwoChildNode(Node):
    def __init__(self, operation):
        self.left = None
        self.right = None
        self.operation = operation

    # insert new child
    def insert(self, left, right):
        self.left = left
        self.right = right

    # propagate the update to the leaves so the random variables can change
    def update(self, t):
        self.left.update(t)
        self.right.update(t)

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
        print("(", end="")
        if self.left is None:
            print("NAN", end="")
        else:
            self.left.printFormula()
        print(dictFunNameToSym.get(self.operation.__name__), end="")
        if self.right is None:
            print("NAN", end="")
        else:
            self.right.printFormula()
        print(")", end="")


class Leaf(Node):
    def __init__(self, value):
        self.value = value

    def getValue(self):
        return self.value

    def update(self, t):
        pass

    def printFormula(self):
        if self.value == math.pi:
            print("pi", end="")
        elif self.value == math.e:
            print("e", end="")
        else:
            print(self.value, end="")


# node that produces a random float with: min < x < max
class RandLeaf(Node):
    # constructor
    def __init__(self, minimum, maximum):
        self.minimum = minimum
        self.maximum = maximum
        self.value = random.uniform(minimum, maximum)

    # updates the random values
    def update(self, t):
        self.value = random.uniform(self.minimum, self.maximum)

    # getter for the value
    def getValue(self):
        return self.value

    # print the value
    def printFormula(self):
        approx = u'\u2248'
        print(f"r{approx}{format(self.value, '.3f')}", end="")


# node that draws from a random distribution
class NDistLeaf(Node):
    def __init__(self, mu, sigma):
        self.mu = mu
        self.sigma = sigma
        self.value = random.normalvariate(self.mu, self.sigma)

    def update(self, t):
        self.value = random.normalvariate(self.mu, self.sigma)

    def getValue(self):
        return self.value

    def printFormula(self):
        approx = u'\u2248'
        print(f"N({self.mu},{self.sigma}){approx}{format(self.value, '.3f')}", end="")


class OldValueLeaf(Node):
    def __init__(self, dataFrame, colName, lag, t):
        self.dataFrame = dataFrame
        self.colName = colName
        # the lag should always be one or higher
        if lag <= 0:
            raise ValueError
        self.lag = lag
        self.t = t
        self.value = 0
        self.update(self.t)

    def update(self, t):
        self.t = t
        # calculate time with respect to lag
        laggedTime = self.t - self.lag
        # check that time - lag >= 0
        if laggedTime >= 0:
            self.value = self.dataFrame.loc[laggedTime, self.colName]
        else:

            self.value = 0

    def getValue(self):
        return self.value

    def printFormula(self):
        sub = str(self.t).translate(SUB) + u'\u208B' + str(self.lag).translate(SUB)
        approx = u'\u2248'
        print(f"{self.colName}{sub}{approx}{format(self.value, '.3f')}", end="")


# function to create a random equation tree
def createRandomEquationTree(maxNumberOfElements, df, colNamesList):
    # creation variables
    randomleafmin = -10
    randomLeafMax = 10
    nDistLeafMu = 0
    nDistLeafSigma = 10
    oldValueLeafDataFrame = df
    oldValueLeafLagMax = 2
    leafConstValue = 1

    elementCounter = 0
    openSpotCounter = 0
    # more efficiency could be obtained with python module blist https://pypi.org/project/blist/
    openSpots = []

    twoChildFunctions = [plus, minus, multiplication]
    oneChildFunctions = [math.sqrt, math.exp]

    endLeafClasses = [Leaf, RandLeaf, NDistLeaf, OldValueLeaf]

    # init the tree with a root that is ether one or two child node
    if random.random() < 0.5:
        # draw random function form the function list
        fun = random.choice(oneChildFunctions)
        # create a root
        root = OneChildNode(fun)
        # safe root in openSpots cause the child is still open
        openSpots.append(root)
        # increment the counters
        elementCounter += 1
        openSpotCounter += 1
    else:
        # draw random function
        fun = random.choice(twoChildFunctions)
        # create the root
        root = TwoChildNode(fun)
        # safe root in openSpots cause the child is still open
        openSpots.append(root)
        # increment the counters
        elementCounter += 1
        openSpotCounter += 2

    # check if there is free space for a binary operation
    while elementCounter + openSpotCounter < maxNumberOfElements:
        # print the current tree
        print(f"\nelementCounter = {elementCounter} openSpotCounter = {openSpotCounter}")
        printAsFormula(root, True)
        # draw a random openSpot and delete it from the list
        print(openSpots)

        if len(openSpots) == 0:
            print(f"\none last time\nelementCounter = {elementCounter} openSpotCounter = {openSpotCounter}")

            break

        nodeToFill = openSpots.pop(random.randint(0, len(openSpots) - 1))
        # nodeToFill = random.choice(openSpots)
        # openSpots.remove(nodeToFill)

        # check if the node is a instance of twoChildNode
        if isinstance(nodeToFill, TwoChildNode):
            print("twochild")
            # only insert binary or unary
            if openSpotCounter < 1:
                # insert left
                if random.random() < 0.5:
                    fun = random.choice(twoChildFunctions)
                    tempNode = TwoChildNode(fun)
                    nodeToFill.left = tempNode
                    openSpots.append(tempNode)
                    elementCounter += 1
                    openSpotCounter += 1
                else:
                    fun = random.choice(oneChildFunctions)
                    tempNode = OneChildNode(fun)
                    nodeToFill.left = tempNode
                    openSpots.append(tempNode)
                    elementCounter += 1
                # right child
                if random.random() < 0.5:
                    fun = random.choice(twoChildFunctions)
                    tempNode = TwoChildNode(fun)
                    nodeToFill.right = tempNode
                    openSpots.append(tempNode)
                    elementCounter += 1
                    openSpotCounter += 1
                else:
                    fun = random.choice(oneChildFunctions)
                    tempNode = OneChildNode(fun)
                    nodeToFill.right = tempNode
                    openSpots.append(tempNode)
                    elementCounter += 1
            # insert binary unary or const
            else:
                # insert left
                if random.random() < 0.3:
                    fun = random.choice(twoChildFunctions)
                    tempNode = TwoChildNode(fun)
                    nodeToFill.left = tempNode
                    openSpots.append(tempNode)
                    elementCounter += 1
                    openSpotCounter += 1
                elif random.random() < 0.5:
                    fun = random.choice(oneChildFunctions)
                    tempNode = OneChildNode(fun)
                    nodeToFill.left = tempNode
                    openSpots.append(tempNode)
                    elementCounter += 1
                else:
                    tempClass = random.choice(endLeafClasses)
                    if tempClass is Leaf:
                        fun = random.choice(oneChildFunctions)
                        tempNode = tempClass(fun)
                        nodeToFill.left = tempNode
                    if tempClass is RandLeaf:
                        tempNode = RandLeaf(randomleafmin, randomLeafMax)
                        nodeToFill.left = tempNode
                    if tempClass is NDistLeaf:
                        tempNode = NDistLeaf(nDistLeafMu, nDistLeafSigma)
                        nodeToFill.left = tempNode
                    if tempClass is OldValueLeaf:
                        tempNode = OldValueLeaf(oldValueLeafDataFrame,random.choice(colNamesList), random.randint(0, oldValueLeafLagMax))
                        nodeToFill.left = tempNode
                    elementCounter += 1
                    openSpotCounter -= 1
                # right child
                if random.random() < 0.5:
                    fun = random.choice(twoChildFunctions)
                    tempNode = TwoChildNode(fun)
                    nodeToFill.right = tempNode
                    openSpots.append(tempNode)
                    elementCounter += 1
                    openSpotCounter += 1
                elif random.random() < 0.5:
                    fun = random.choice(oneChildFunctions)
                    tempNode = OneChildNode(fun)
                    nodeToFill.right = tempNode
                    openSpots.append(tempNode)
                    elementCounter += 1
                else:
                    tempClass = random.choice(endLeafClasses)
                    if tempClass is Leaf:
                        tempNode = tempClass(leafConstValue)
                        nodeToFill.right = tempNode
                    if tempClass is RandLeaf:
                        tempNode = RandLeaf(randomleafmin, randomLeafMax)
                        nodeToFill.right = tempNode
                    if tempClass is NDistLeaf:
                        tempNode = NDistLeaf(nDistLeafMu, nDistLeafSigma)
                        nodeToFill.right = tempNode
                    if tempClass is OldValueLeaf:
                        tempNode = OldValueLeaf(oldValueLeafDataFrame,random.choice(colNamesList), random.randint(0, oldValueLeafLagMax),0)
                        nodeToFill.right = tempNode
                    elementCounter += 1
                    openSpotCounter -= 1
        # if the node is a instance of OneChildNode do...
        #if (isinstance(nodeToFill, OneChildNode)):
            # if the open


    return root
