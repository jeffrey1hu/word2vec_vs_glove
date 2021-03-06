#!/usr/bin/env python

import glob
import random
import numpy as np
import os.path as op
import cPickle as pickle
from utils.general_utils import Progbar, save_params


def load_saved_params():
    """
    A helper function that loads previously saved parameters and resets
    iteration start.
    """
    st = 0
    for f in glob.glob("saved_params_*.npy"):
        iter = int(op.splitext(op.basename(f))[0].split("_")[2])
        if (iter > st):
            st = iter

    if st > 0:
        with open("saved_params_%d.npy" % st, "r") as f:
            params = pickle.load(f)
            state = pickle.load(f)
        return st, params, state
    else:
        return st, None, None

def sgd(f, x0, lr, iterations, postprocessing=None, useSaved=False, save_every=False, save_path='./'):
    """ Stochastic Gradient Descent

    Implement the stochastic gradient descent method in this function.

    Arguments:
    f -- the function to optimize, it should take a single
         argument and yield two outputs, a cost and the gradient
         with respect to the arguments
    x0 -- the initial point to start SGD from
    step -- the step size for SGD
    iterations -- total iterations to run SGD for
    postprocessing -- postprocessing function for the parameters
                      if necessary. In the case of word2vec we will need to
                      normalize the word vectors to have unit length.
    PRINT_EVERY -- specifies how many iterations to output loss

    Return:
    x -- the parameter value after SGD finishes
    """

    # Anneal learning rate every several iterations
    ANNEAL_EVERY = 20000
    # auto save if save every is true
    SAVE_EVERY = 10000

    if useSaved:
        start_iter, oldx, state = load_saved_params()
        if start_iter > 0:
            x0 = oldx
            lr *= lr ** (start_iter / ANNEAL_EVERY)

        if state:
            random.setstate(state)
    else:
        start_iter = 0

    x = x0

    if not postprocessing:
        postprocessing = lambda x: x

    expcost = None
    prog = Progbar(target=iterations)
    for iter in xrange(start_iter + 1, iterations + 1):
        # Don't forget to apply the postprocessing after every iteration!
        # You might want to print the progress every few iterations.
        cost, grad = f(x)
        x -= grad * lr
        postprocessing(grad)

        if not expcost:
            expcost = cost
        else:
            expcost = .95 * expcost + .05 * cost

        prog.update(iter, [("expcost", expcost)])

        if save_every and iter % SAVE_EVERY == 0:
            save_params(save_path, iter, x)

        if iter % ANNEAL_EVERY == 0:
            lr *= 0.5

    return x


def sanity_check():
    quad = lambda x: (np.sum(x ** 2), x * 2)

    print "Running sanity checks..."
    t1 = sgd(quad, 0.5, 0.01, 1000, PRINT_EVERY=100)
    print "test 1 result:", t1
    assert abs(t1) <= 1e-6

    t2 = sgd(quad, 0.0, 0.01, 1000, PRINT_EVERY=100)
    print "test 2 result:", t2
    assert abs(t2) <= 1e-6

    t3 = sgd(quad, -1.5, 0.01, 1000, PRINT_EVERY=100)
    print "test 3 result:", t3
    assert abs(t3) <= 1e-6

    print ""


def your_sanity_checks():
    """
    Use this space add any additional sanity checks by running:
        python q3_sgd.py
    This function will not be called by the autograder, nor will
    your additional tests be graded.
    """
    print "Running your sanity checks..."
    ### YOUR CODE HERE
    ### END YOUR CODE


if __name__ == "__main__":
    sanity_check()
    your_sanity_checks()
