#!/usr/bin/python3

# B351/Q351 Fall 2024
# Professor Yijie Wang
# Do not share these assignments or their solutions outside of this class.

import math

# unique takes an iterable and returns
# - a set of each unique item from that iterable
# - a list of the counts of the number of times each item appeared in the original iterable
# ex: unique([5,3,5,2,3,4,2,5,4,2]) would return ([2,3,4,5] , [3,2,2,3])

def unique(iterable):
    items = list(iterable)
    unique_items = list(set(items))
    counts = [items.count(item) for item in unique_items]
    return unique_items, counts

##################################################
# Problem 1 - Entropy
##################################################
# Objective: Write a function that returns the entropy of a data set given its classifications
# (1) Count how many times each class in classifications occurs
# (2) Get the total number of classifications
# (3) Go through each count and get the probability distribution
# (4) Use the entropy formula used in class

# Notes:
# Arguments:
# - classifications is a list of the classifications assigned to data points
# Returns: a value representing the entropy

def calc_entropy(classifications):
    fill, classCounts = unique(classifications)
    total = sum(classCounts)
    E = 0
    for i in classCounts:
        p = i / total
        E -= p * math.log2(p)
    return E


##################################################
# Problem 2 - Information Gain
##################################################
# Objective: Write a function that returns the information gain from splitting by a given attribute
# (1) Get the total number of points
# (2) Get the weighted entropy by going through each value and
#       (a) getting the entropy at that value (the child entropy)
#       (b) finding the probability of that value occurring
# (3) Get the entropy of the parent
# (4) Use the information gain formula used in class

# Notes:
# Arguments:
# - parent_classifications is a list of the classifications of the points being used to train the parent
# - classifications_by_val is a dictionary of each unique value of an attribute mapped to
#                            a list of the classifications of each data point with that unique value
#   ex: From the sunburn example in class, {'Blonde': ['Burn', 'None', 'Burn', 'None'],
#                                           'Brown':  ['None', 'None', 'None'],
#                                           'Red':    ['Burn']}
# - val_freqs is a dictionary of each unique value of an attribute mapped to the number of times that value occurs
#                (how frequently it appears in the dataset)
# Returns: a value representing the information gain
# - It may be a good idea to look up dictionary methods

def calc_information_gain(parent_classifications, classifications_by_val, val_freqs):
    points = sum(val_freqs.values())
    parentE = calc_entropy(parent_classifications)
    weightedE = 0
    for i, child_classifications in classifications_by_val.items():
        childE = calc_entropy(child_classifications)
        P = val_freqs[i] / points
        weightedE += P * childE
    I = parentE - weightedE
    return I

##################################################
#                 OtherKey Class
#
# OtherKey is an object that represents any unexpected value for an attribute in question.
#
##################################################

class OtherKey:

    def __repr__(self):
        return 'OTHER'

# use OTHER when calling an OtherKey object
OTHER = OtherKey()

##################################################
#                 Node Class
#
# The Node class is a node in a decision tree. It typically represents an attribute that is split.
#
##################################################

class Node:

    # The representation of a node
    def __init__(self, attribute=None, children=None, classification=None):
        self.attribute = attribute
        if children is None:
            self.children = {}
        else:
            self.children = children
        self.classification = classification

    # A function to explain how the node is made
    def __repr__(self):
        if self.classification is not None:
            return f'Node(classification={self.classification!r})'
        if self.attribute is not None:
            child_reprs = {val: repr(child).replace('\n','\n    ') for val, child in self.children.items()}
            repr_string = f'Node(attribute={self.attribute!r}, children={{\n'
            for val, rep in child_reprs.items():
                repr_string += f'    {val!r}: {rep},\n'
            repr_string += '  })'
            return repr_string
        return 'Node()'

    ##################################################
    # Problem 3 - Classify
    ##################################################
    # Objective: Write a function that classifies a given point going through the decision tree process
    # (1) If the Node has a classification, return that classification
    # Otherwise,
    # (2) Get the value of the node's attribute at the point
    # (3) If this value maps to one of the node's child nodes, get the child node corresponding to the value
    # (4) Otherwise, get the child node corresponding to OTHER
    # (5) Call the appropriate child's classify method on the point and return the classification provided

    # Notes:
    # a point is a dictionary of each attribute for the point mapped to the attribute's value

    def classify_point(self, point):
        if self.classification is not None:
            return self.classification
        attr = point.get(self.attribute)
        child = self.children.get(attr, self.children.get(OTHER))
        if child:
            return child.classify_point(point)
        
        return None

    ##################################################

    # A function that trains the decision tree
    def train(self, points, labels):
        # are we a leaf?
        unique_labels, label_counts = unique(labels)
        if len(unique_labels) == 1:
            self.classification = unique_labels[0]
            return

        # consider all possible attributes to split by!
        # note that there are a lot of things to keep track of.
        best_attr = None
        best_vals = None
        best_points_by_val = None
        best_labels_by_val = None
        best_ig = None
        for attribute in points[0].keys():
            vals = set()
            points_by_val = {}
            labels_by_val = {}
            val_freqs = {}
            for point, label in zip(points, labels):
                val = point[attribute]

                if not val in vals:
                    vals.add(val)
                    val_freqs[val] = 0
                    points_by_val[val] = []
                    labels_by_val[val] = []

                val_freqs[val] += 1
                points_by_val[val].append(point)
                labels_by_val[val].append(label)

            least_frequent = min(vals, key=val_freqs.get)

            vals.remove(least_frequent)
            vals.add(OTHER)
            points_by_val[OTHER] = points_by_val.pop(least_frequent)
            labels_by_val[OTHER] = labels_by_val.pop(least_frequent)
            val_freqs[OTHER] = val_freqs.pop(least_frequent)

            information_gain = information_gain(labels, labels_by_val, val_freqs)

            if best_attr is None or information_gain > best_ig:
                best_attr = attribute
                best_vals = vals
                best_points_by_val = points_by_val
                best_labels_by_val = labels_by_val
                best_ig = information_gain

        # what if all of the points are the same?
        if len(best_vals) == 1:
            _, self.classification = max(zip(label_counts, unique_labels))
            return

        self.attribute = best_attr
        for val in best_vals:
            child = Node()
            child.train(best_points_by_val[val], best_labels_by_val[val])
            self.children[val] = child



##################################################
# Problem 3 - K-Nearest Neighbors
##################################################
# Objective: Finish the implementation of the K-Nearest Neighbor Classifier
class KNN_Classifier:
    def __init__(self, k):
        self.k = k

    ##################################################
    # Problem 3a - Euclidean Distance
    ##################################################
    # Objective: Return the euclidean distance distance between two points
    def calc_euclidean_distance(self, point_a, point_b):
        euclideanDistance = 0
        for i in point_a:
            euclideanDistance += (point_a[i] - point_b[i]) ** 2
        return math.sqrt(euclideanDistance)

    ##################################################
    # Problem 3b - Pick Label
    ##################################################
    # Objective: Choose the most frequent label out of the labels for the k nearest neighbors
    def get_top_label(self, top_k_labels):
        buff = {}
        for i in top_k_labels:
            if i in buff:
                 buff[i] += 1
            else:
                buff[i] = 1
        freqLabel = max(buff, key=buff.get)
        return freqLabel

    ##################################################
    # Problem 3c- Classify
    ##################################################
    # Objective: Run the KNN classification algorithm
    #
    # Notes:
    #  - sample points and sample_labels correspond with each other
    #  - you may find heappush/pop to be useful to keep track of the k closet neighbors here
    def classify_point(self, point, training_points, training_labels):
        arr = []
        for i, j in zip(training_points, training_labels):
            euclideanDistance = self.calc_euclidean_distance(point, i)
            arr.append((euclideanDistance, j))
        arr.sort()
        labels = [i for _, i in arr[:self.k]]
        
        return self.get_top_label(labels)
