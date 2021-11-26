# base node for the tree
# the parent for all other types of nodes
class Node:
    # add keyword pass cause we dont wont to add any other stuff to the class
    pass


class OneChildNode(Node):
    def __init__(self, operation):
        # the child
        self.left = None
        # function that only takes one input
        self.operation = operation

    # insert new child
    def insert(self, child):
        self.left = child

    # calculate the value of the subtree and return it
    # if tree empty use zero
    def getValue(self):
        if self.left is None:
            return self.operation(0)
        else:
            return self.operation(self.left.getValue())


class TwoChildNode(Node):
    def __init__(self, operation):
        self.left = Node
        self.right = Node
        self.operation = operation

