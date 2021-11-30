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
    # assert divisor != 0
    return a / divisor


def power(base, exponent):
    return math.pow(base, exponent)


'''def uniformRandom(a, b):
    return random.uniform(a, b)


def normalDistribution(a, b):
    return random.normalvariate(a, b)
'''


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
    # binary
    "division": '/',
    "minus": '-',
    "plus": '+',
    "multiplication": '*',
    "power": "^",
    # unary
    "exp": "exp",
    "sqrt": "sqrt",
    "sin": "sin",
    "cos": "cos",
    "tan": "tan",
    "log2": "log2",
    "log10": "log10",

}
# helper translator to subscript
SUB = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")

# global list of all functions
twoChildFunctions = [plus, minus, multiplication, division, power]
oneChildFunctions = [math.sqrt, math.exp, math.sin, math.cos, math.tan, math.log2, math.log10]


# helper function for formula printing
def printAsFormula(root, verbose):
    if verbose:
        print("function: ", end="")
    root.printFormula()
    try:
        print(f" = {root.getValue()}")
    except ValueError:
        print(" = mathDomainError")
    except OverflowError:
        print(" = OverflowError = to big")
    except ZeroDivisionError:
        print(" = ZeroDivisionError")


# the two base classes for the tree
# the parent for all types of nodes
class Node:
    # add keyword pass cause we dont wont to add any other stuff to the class
    def update(self, t):
        pass

    def getValue(self):
        pass

    def printFormula(self):
        pass


# the parent for all types of leaves
class Leaf:
    # add keyword pass cause we dont wont to add any other stuff to the class
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


class ConstLeaf(Leaf):
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
class RandLeaf(Leaf):
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
class NDistLeaf(Leaf):
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


class OldValueLeaf(Leaf):
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


# define global list of all Leaf subclasses
endLeafClasses = [ConstLeaf, RandLeaf, NDistLeaf, OldValueLeaf]


# Implementation of algo 57 "subtree selection"
# 1. select from tree1 and tree2 a random Node
# 2. select child or at random left/right for each
# 3. swap the subtrees of the random node
def subtreeSwap(root1, root2, verbose):
    # count the number of nodes
    nodeCountRoot1 = countNodesOfTree(root1)
    nodeCountRoot2 = countNodesOfTree(root2)
    if verbose:
        print("\nroot Tree1: ", end="")
        printAsFormula(root1, True)
        print("root Tree2: ", end="")
        printAsFormula(root2, True)
        print(f"Nr. of Elements in Tree1 = {countElementsOfTree(root1)} and "
              f"Nr. of Elements in Tree2 = {countElementsOfTree(root2)}")
        print(f"Nr. of Nodes in Tree1 = {nodeCountRoot1} and Nr. of Nodes in Tree2 = {nodeCountRoot2}")

    # pick node at random form the trees
    n1 = random.randint(1, nodeCountRoot1)
    n2 = random.randint(1, nodeCountRoot2)
    if verbose:
        print(f"random Number for Tree1 = {n1} and random Number for Tree2 = {n2}")
    # get the two subtrees
    subTree1 = pickNode(root1, n1)
    subTree2 = pickNode(root2, n2)
    if verbose:
        print("subtree 1N: ", end="")
        printAsFormula(subTree1, True)
        print("subtree 2N: ", end="")
        printAsFormula(subTree2, True)
    # choose a random child

    # chose left == 0 or right == 1
    r = random.randint(0, 1)
    # swap the two subtrees
    assert (isinstance(subTree1, (OneChildNode, TwoChildNode)))
    assert (isinstance(subTree2, (OneChildNode, TwoChildNode)))

    # depending on the constellation of binary and unary class do differnet swap action
    # in the end its a simple swap with temp location
    if isinstance(subTree1, OneChildNode):
        if isinstance(subTree2, OneChildNode):
            tempChild = subTree1.child
            subTree1.child = subTree2.child
            subTree2.child = tempChild
        else:
            tempChild = subTree1.child
            # left
            if r == 0:
                subTree1.child = subTree2.left
                subTree2.left = tempChild
            # right
            else:
                subTree1.child = subTree2.right
                subTree2.left = tempChild
    elif isinstance(subTree1, TwoChildNode):
        if r == 0:
            tempChild = subTree1.left
            if isinstance(subTree2, OneChildNode):
                subTree1.left = subTree2.child
                subTree2.child = tempChild
            else:
                r = random.randint(0, 1)
                if r == 0:
                    subTree1.left = subTree2.left
                    subTree2.left = tempChild
                else:
                    subTree1.left = subTree2.right
                    subTree2.right = tempChild
        else:
            tempChild = subTree1.right
            if isinstance(subTree2, OneChildNode):
                subTree1.right = subTree2.child
                subTree2.child = tempChild
            else:
                r = random.randint(0, 1)
                if r == 0:
                    subTree1.right = subTree2.left
                    subTree2.left = tempChild


# recursive depth first search to count elements
def countElementsOfTree(root):
    if root is None:
        return 0
    stack = [root]
    c = 0
    while len(stack) > 0:
        currentElement = stack.pop()
        c += 1
        if isinstance(currentElement, Leaf):
            continue
        if isinstance(currentElement, OneChildNode):
            stack.append(currentElement.child)
        if isinstance(currentElement, TwoChildNode):
            stack.append(currentElement.right)
            stack.append(currentElement.left)
    return c


# iterative search for the i's element in the tree using pre-order https://en.wikipedia.org/wiki/Tree_traversal
def pickElement(root, i):
    if root is None:
        return None
    stack = [root]
    c = 0
    while len(stack) > 0:
        currentNode = stack.pop()
        c += 1
        if c == i:
            return currentNode
        if isinstance(currentNode, OneChildNode):
            stack.append(currentNode.child)
        if isinstance(currentNode, TwoChildNode):
            stack.append(currentNode.right)
            stack.append(currentNode.left)


def countNodesOfTree(root):
    if root is None:
        return 0
    stack = [root]
    c = 0
    while len(stack) > 0:
        currentElement = stack.pop()
        if isinstance(currentElement, Leaf):
            continue
        c += 1
        if isinstance(currentElement, OneChildNode):
            stack.append(currentElement.child)
        if isinstance(currentElement, TwoChildNode):
            stack.append(currentElement.right)
            stack.append(currentElement.left)
    return c


# iterative search for the i's node in the tree using pre-order
# basically same pick element only that here we skip Elements of type Leaf
def pickNode(root, i):
    if root is None:
        return None
    stack = [root]
    c = 0
    while len(stack) > 0:
        currentNode = stack.pop()
        if isinstance(currentNode, Leaf):
            continue
        c += 1
        if c == i:
            return currentNode
        if isinstance(currentNode, OneChildNode):
            stack.append(currentNode.child)
        if isinstance(currentNode, TwoChildNode):
            stack.append(currentNode.right)
            stack.append(currentNode.left)


def countElementsOfTreeOfSpecificClass(root, classOfInterest):
    if root is None:
        return 0
    stack = [root]
    c = 0
    while len(stack) > 0:
        currentElement = stack.pop()
        if isinstance(currentElement, Leaf):
            if isinstance(currentElement, classOfInterest):
                c += 1
            continue
        if isinstance(currentElement, OneChildNode):
            stack.append(currentElement.child)
        if isinstance(currentElement, TwoChildNode):
            stack.append(currentElement.right)
            stack.append(currentElement.left)
    return c


# iterative search for the i's element in the tree using pre-order https://en.wikipedia.org/wiki/Tree_traversal
def pickSpecificClass(root, i, classOfInterest):
    if root is None:
        return None
    stack = [root]
    c = 0
    while len(stack) > 0:
        currentNode = stack.pop()

        if isinstance(currentNode, classOfInterest):
            c += 1
            if c == i:
                return currentNode
        if isinstance(currentNode, OneChildNode):
            stack.append(currentNode.child)
        if isinstance(currentNode, TwoChildNode):
            stack.append(currentNode.right)
            stack.append(currentNode.left)


# dissipation see in mutateTree()
def subtreeMutate(root, dataFrame, colNameList, maxLag, maxLength):
    # determine length of Subtree
    length = random.randint(1, maxLength)
    # create a random Subtree
    subTree = createRandomEquationTree(length, False, 0, 10, 10, 1, dataFrame, colNameList, maxLag, 1)
    # select subtree where root is a Node
    subRoot = pickNode(root, random.randint(1, countNodesOfTree(root)))
    # check if unary or binary
    if isinstance(subRoot, OneChildNode):
        subRoot.child = subTree
    else:
        # fifty-fifty left or right
        if random.random() < 0.5:
            subRoot.left = subTree
        else:
            subRoot.right = subTree
    return root


# dissipation see in mutateTree()
def eraseNodeMutate(root):
    # select a Node to delete from tree
    parentOfNodeToDelete = pickNode(root, random.randint(1, countNodesOfTree(root)))
    # check if unary or binary
    if isinstance(parentOfNodeToDelete, OneChildNode):
        # check child delete target
        if isinstance(parentOfNodeToDelete.child, OneChildNode):
            parentOfNodeToDelete.child = parentOfNodeToDelete.child.child
        elif isinstance(parentOfNodeToDelete.child, TwoChildNode):
            if random.random() < 0.5:
                parentOfNodeToDelete.child = parentOfNodeToDelete.child.left
            else:
                parentOfNodeToDelete.child = parentOfNodeToDelete.child.right

    elif isinstance(parentOfNodeToDelete, TwoChildNode):
        # left
        if random.random() < 0.5:
            if isinstance(parentOfNodeToDelete.left, OneChildNode):
                parentOfNodeToDelete.left = parentOfNodeToDelete.left.child
            elif isinstance(parentOfNodeToDelete.left, TwoChildNode):
                if random.random() < 0.5:
                    parentOfNodeToDelete.left = parentOfNodeToDelete.left.left
                else:
                    parentOfNodeToDelete.left = parentOfNodeToDelete.left.right
        # right
        else:
            if isinstance(parentOfNodeToDelete.right, OneChildNode):
                parentOfNodeToDelete.right = parentOfNodeToDelete.right.child
            elif isinstance(parentOfNodeToDelete.right, TwoChildNode):
                if random.random() < 0.5:
                    parentOfNodeToDelete.right = parentOfNodeToDelete.right.left
                else:
                    parentOfNodeToDelete.right = parentOfNodeToDelete.right.right
    return root


# dissipation see in mutateTree()
def exchangeNodeMutation(root, nodesToExchange):
    # use global function lists
    global oneChildFunctions
    global twoChildFunctions
    # repeat it n times
    while nodesToExchange > 0:
        # pick a random node
        node = pickNode(root, random.randint(1, countNodesOfTree(root)))
        # exchange the operator of ether the binary or unary node
        if isinstance(node, OneChildNode):
            node.operation = random.choice(oneChildFunctions)
        else:
            node.operation = random.choice(twoChildFunctions)
        nodesToExchange -= 1
    return root


# dissipation see in mutateTree()
def leafValueMutation(root, nChanges, mu, sigma):
    # make sure that there are enough constLeaves to mutate
    n = countElementsOfTreeOfSpecificClass(root, ConstLeaf)
    # if there are no ConstLeaves exit immediately
    if n == 0:
        return root
    # if there are less constLeaves than specified by function input -> only change all constLeaves in the tree
    if nChanges > n:
        nChanges = n
    # repeat n times
    while nChanges > 0:
        # draw a new random value form normal distribution
        newValue = random.normalvariate(mu, sigma)
        # random position for the const leaf
        r = random.randint(1, countElementsOfTreeOfSpecificClass(root, ConstLeaf))
        # pick a random const Leaf
        chosenLeaf = pickSpecificClass(root, r, ConstLeaf)
        chosenLeaf.value = newValue
        nChanges -= 1
    return root


# dissipation see in mutateTree()
def exchangeLeafMutation(root, leavesToExchange, dataFrame, colNameList, maxLag, constMU, constSigma,
                         randMin, randMax, nMu, nSigma):
    # use global leaf sub classes list
    global endLeafClasses
    # count the number of Leaves
    n = countElementsOfTreeOfSpecificClass(root, tuple(endLeafClasses))
    # if there are less leaves than changes requested adjust the the changes down
    if leavesToExchange > n:
        leavesToExchange = n

    # number of nodes in the tree
    nodeCount = countNodesOfTree(root)
    # repeat n times the
    while leavesToExchange > 0:
        # pick a random node
        node = pickNode(root, random.randint(1, nodeCount))
        # if it's unary
        if isinstance(node, OneChildNode):
            if isinstance(node.child, tuple(endLeafClasses)):
                newLeafClass = random.choice(endLeafClasses)
                if newLeafClass is ConstLeaf:
                    newLeaf = newLeafClass(random.normalvariate(constMU, constSigma))
                if newLeafClass is RandLeaf:
                    newLeaf = RandLeaf(randMin, randMax)
                if newLeafClass is NDistLeaf:
                    newLeaf = NDistLeaf(nMu, nSigma)
                else:
                    newLeaf = OldValueLeaf(dataFrame, random.choice(colNameList),
                                           random.randint(1, maxLag), 0)
                node.child = newLeaf
                leavesToExchange -= 1
            else:
                continue
        # if it's binary
        if isinstance(node, TwoChildNode):
            # left
            if random.random() < 0.5:
                if isinstance(node.left, tuple(endLeafClasses)):
                    newLeafClass = random.choice(endLeafClasses)
                    if newLeafClass is ConstLeaf:
                        newLeaf = newLeafClass(random.normalvariate(constMU, constSigma))
                    if newLeafClass is RandLeaf:
                        newLeaf = RandLeaf(randMin, randMax)
                    if newLeafClass is NDistLeaf:
                        newLeaf = NDistLeaf(nMu, nSigma)
                    else:
                        newLeaf = OldValueLeaf(dataFrame, random.choice(colNameList),
                                               random.randint(1, maxLag), 0)
                    node.left = newLeaf
                    leavesToExchange -= 1
                else:
                    continue
            else:
                if isinstance(node.right, tuple(endLeafClasses)):
                    newLeafClass = random.choice(endLeafClasses)
                    if newLeafClass is ConstLeaf:
                        newLeaf = newLeafClass(random.normalvariate(constMU, constSigma))
                    if newLeafClass is RandLeaf:
                        newLeaf = RandLeaf(randMin, randMax)
                    if newLeafClass is NDistLeaf:
                        newLeaf = NDistLeaf(nMu, nSigma)
                    else:
                        newLeaf = OldValueLeaf(dataFrame, random.choice(colNameList),
                                               random.randint(1, maxLag), 0)
                    node.right = newLeaf
                    leavesToExchange -= 1
                else:
                    continue
    return root


# main mutation function
def mutateTree(root, dataFrame, colNameList, maxLag):
    # Subtree mutation
    # pick a random subtree and replace it with a new randomly created Subtree (max element count = 15)
    printAsFormula(root, False)
    mutated1Root = subtreeMutate(root, dataFrame, colNameList, maxLag, 10)
    printAsFormula(mutated1Root, False)
    # erase node mutation
    # take a node and replace it with one of its child's
    mutated2Root = eraseNodeMutate(mutated1Root)
    printAsFormula(mutated2Root, False)
    # binary and unary swap mutation,
    # change the operator of a Node (e.g.: plus -> minus, sqrt -> exp)
    nodesToExchange = 2
    # oneChildFunctions = [math.sqrt, math.exp, math.sin, math.cos, math.tan, math.log2, math.log10]
    # twoChildFunctions = [plus, minus, multiplication, division, power]
    mutated3Root = exchangeNodeMutation(mutated2Root, nodesToExchange)
    printAsFormula(mutated3Root, False)
    # Leaf value mutation
    # change value of ConstLeaves (e.g.: ConstLeaf(42) -> ConstLeaf(69), RandLeaf(1,9) -> RandLeaf(3,6)
    mutated4Root = leafValueMutation(mutated3Root, 2, 9, 1)
    printAsFormula(mutated4Root, False)
    # Leaf type mutation
    # change the type (class) of a leaf (e.g.: ConstLeaf(42) -> RandLeaf(3,6)
    # note we need for the OldValueLeaf creation the dataframe, the column name list and max lag
    mutated5Root = exchangeLeafMutation(mutated4Root, 2, dataFrame, colNameList, maxLag,
                                        constMU=10, constSigma=1, randMin=1, randMax=10, nMu=10, nSigma=1)

    printAsFormula(mutated5Root, False)
    return mutated5Root


# NOTICE:
# the creation of a random tree could be accomplished much more elegant and compact using recursion
# algo 53 "The Grow Algorithm" in Essentials of Metaheuristics

# function to create a random equation tree
def createRandomEquationTree(maxNumberOfElements, verbose, randomleafmin, randomLeafMax, nDistLeafMu,
                             nDistLeafSigma, oldValueLeafDataFrame, colNamesList, oldValueLeafLagMax, leafConstValue):
    # keeps track of the fixed elements that are all ready in the tree (e.g.: the twoChildNode or a Leaf
    elementCounter = 0
    # keeps track of the amount of branches that are currently empty and need to expanded for a correct tree
    # ergo always when a Node still lacks a child or two
    openSpotCounter = 0
    # more efficiency could be obtained with python module blist https://pypi.org/project/blist/
    openSpots = []
    # use global function lists
    global twoChildFunctions
    global oneChildFunctions
    # the four possible types of Leaves
    global endLeafClasses

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
    while len(openSpots) > 0:
        # chose a random node that doesn't has child/ren and take it out of the openSpots list
        nodeToFill = openSpots.pop(random.randint(0, len(openSpots) - 1))
        # print if verbose true
        if verbose:
            # print the current tree
            print(
                f"\nelementCounter = {elementCounter} openSpotCounter = {openSpotCounter} length of openSpots {len(openSpots)}")
            printAsFormula(root, True)
            # draw a random openSpot and delete it from the list
            print(openSpots)
            print(f"we chose {nodeToFill}")

        # if the node is a instance of twoChildNode do...
        if isinstance(nodeToFill, TwoChildNode):
            # list to store the possible children types in
            # note the types cann be inside more than once because:
            # draws without replacement first for left and then for right child , effectively drawing two times
            options = []
            # this means they hit together the max and we only want to add no expanding elements ergo const and co.
            if elementCounter + openSpotCounter >= maxNumberOfElements:
                # add two times cause we need to fill to childes
                options.append("eL")
                options.append("eL")
            else:
                # check if there is space for both to be binary operator -> this implies also space for unary
                if elementCounter + openSpotCounter + 4 <= maxNumberOfElements:
                    # add two times cause we
                    options.append("bL")
                    options.append("bL")
                    options.append("uL")
                    options.append("uL")
                    # if there are other open spots still available the End leaves should also be open to option
                    if len(openSpots) > 0:
                        options.append("eL")
                        options.append("eL")
                # check if only space for a binary and one unitary
                elif elementCounter + openSpotCounter + 3 <= maxNumberOfElements:
                    options.append("bL")
                    options.append("uL")
                    options.append("uL")
                    # if there are other open spots still available the End leaves should also be open to option
                    if len(openSpots) > 0:
                        options.append("eL")
                        options.append("eL")
                # cause of ambiguity of binary+end and unary+unary we only take unary as an option
                elif elementCounter + openSpotCounter + 2 <= maxNumberOfElements:
                    options.append("uL")
                    options.append("uL")
                    # if there are other open spots still available the End leaves should also be open to option
                    if len(openSpots) > 0:
                        options.append("eL")
                        options.append("eL")
                #
                # only possible to add one unitary and one end
                elif elementCounter + openSpotCounter + 1 <= maxNumberOfElements:
                    options.append("uL")
                    options.append("eL")
                    # here we dont need to check if there are any spots left cause
                # this should never happen
                else:
                    print("we messed up bro in binary")
                    raise ValueError

            if verbose:
                print("options1 are ", options)
            # choose a type for the child for left
            # we draw a option form the option list without putting it back in
            choice = options.pop(random.randint(0, len(options) - 1))
            if verbose:
                print(f"the choice1 is {choice}")
            # depending on the choice add the type chosen to the left
            if choice == "bL":
                fun = random.choice(twoChildFunctions)
                tempNode = TwoChildNode(fun)
                nodeToFill.left = tempNode
                openSpots.append(tempNode)
                elementCounter += 1
                openSpotCounter += 1
            if choice == "uL":
                fun = random.choice(oneChildFunctions)
                tempNode = OneChildNode(fun)
                nodeToFill.left = tempNode
                openSpots.append(tempNode)
                elementCounter += 1
            if choice == "eL":
                # draw a random Leaf Class and do in case of each create the leaf and
                # insert into the child of the nodeToFill
                tempClass = random.choice(endLeafClasses)
                if tempClass is ConstLeaf:
                    tempNode = tempClass(leafConstValue)
                    nodeToFill.left = tempNode
                if tempClass is RandLeaf:
                    tempNode = RandLeaf(randomleafmin, randomLeafMax)
                    nodeToFill.left = tempNode
                if tempClass is NDistLeaf:
                    tempNode = NDistLeaf(nDistLeafMu, nDistLeafSigma)
                    nodeToFill.left = tempNode
                if tempClass is OldValueLeaf:
                    tempNode = OldValueLeaf(oldValueLeafDataFrame, random.choice(colNamesList),
                                            random.randint(1, oldValueLeafLagMax), 0)
                    nodeToFill.left = tempNode
                elementCounter += 1
                openSpotCounter -= 1
            # same for right
            if verbose:
                print("options before pop2", options)
            # choose a type for the child for right
            # we draw a option form the option list without putting it back in
            choice = options.pop(random.randint(0, len(options) - 1))
            if verbose:
                print(f"the choice2 is {choice}")
            # depending on the choice add the type chosen to the right
            if choice == "bL":
                fun = random.choice(twoChildFunctions)
                tempNode = TwoChildNode(fun)
                nodeToFill.right = tempNode
                openSpots.append(tempNode)
                elementCounter += 1
                openSpotCounter += 1
            if choice == "uL":
                fun = random.choice(oneChildFunctions)
                tempNode = OneChildNode(fun)
                nodeToFill.right = tempNode
                openSpots.append(tempNode)
                elementCounter += 1
            if choice == "eL":
                # draw a random Leaf Class and do in case of each create the leaf and
                # insert into the child of the nodeToFill
                tempClass = random.choice(endLeafClasses)
                if tempClass is ConstLeaf:
                    tempNode = tempClass(leafConstValue)
                    nodeToFill.right = tempNode
                if tempClass is RandLeaf:
                    tempNode = RandLeaf(randomleafmin, randomLeafMax)
                    nodeToFill.right = tempNode
                if tempClass is NDistLeaf:
                    tempNode = NDistLeaf(nDistLeafMu, nDistLeafSigma)
                    nodeToFill.right = tempNode
                if tempClass is OldValueLeaf:
                    tempNode = OldValueLeaf(oldValueLeafDataFrame, random.choice(colNamesList),
                                            random.randint(1, oldValueLeafLagMax), 0)
                    nodeToFill.right = tempNode
                elementCounter += 1
                openSpotCounter -= 1

        # if the node is a instance of OneChildNode do...
        if isinstance(nodeToFill, OneChildNode):
            # list to store the possible children types in a list
            # note the types can only be once in there cause we only draw once
            options = []
            # this means they hit together the max and we only want to add no expanding elements ergo const and co.
            if elementCounter + openSpotCounter >= maxNumberOfElements:
                options.append("eL")
            else:
                # check if there is space for a binary operator -> this implies also space for unary
                if elementCounter + openSpotCounter + 2 <= maxNumberOfElements:
                    options.append("bL")
                    options.append("uL")
                    if len(openSpots) > 0:
                        options.append("eL")
                # check if only space for unary operator
                elif elementCounter + openSpotCounter + 1 <= maxNumberOfElements:
                    options.append("uL")
                    if len(openSpots) > 0:
                        options.append("eL")
                # this should never happen
                else:
                    print("we messed up bro")
                    raise ValueError
            if verbose:
                print("options =", options)
            # take a random option
            # note here we draw with replacement cause we only draw once and thous it doesn't matters
            choice = random.choice(options)
            if verbose:
                print(f"choice = {choice}")
            # depending on the choice we add a children of that type as child
            # endLeaf is the choice
            if choice == "eL":
                # draw a random Leaf Class and do in case of each create the leaf and
                # insert into the child of the nodeToFill
                tempClass = random.choice(endLeafClasses)
                if tempClass is ConstLeaf:
                    tempNode = tempClass(leafConstValue)
                    nodeToFill.child = tempNode
                if tempClass is RandLeaf:
                    tempNode = RandLeaf(randomleafmin, randomLeafMax)
                    nodeToFill.child = tempNode
                if tempClass is NDistLeaf:
                    tempNode = NDistLeaf(nDistLeafMu, nDistLeafSigma)
                    nodeToFill.child = tempNode
                if tempClass is OldValueLeaf:
                    tempNode = OldValueLeaf(oldValueLeafDataFrame, random.choice(colNamesList),
                                            random.randint(1, oldValueLeafLagMax), 0)
                    nodeToFill.child = tempNode
                elementCounter += 1
                openSpotCounter -= 1
            # unary node is choice
            if choice == "uL":
                fun = random.choice(oneChildFunctions)
                tempNode = OneChildNode(fun)
                nodeToFill.child = tempNode
                openSpots.append(tempNode)
                elementCounter += 1
            # binary node is choice
            if choice == "bL":
                fun = random.choice(twoChildFunctions)
                tempNode = TwoChildNode(fun)
                nodeToFill.child = tempNode
                openSpots.append(tempNode)
                elementCounter += 1
                openSpotCounter += 1
    if verbose:
        printAsFormula(root, True)
    return root
