#!/usr/bin/env python
"""A short and simple example experiment for the two real-world suites.
"""
from __future__ import division, print_function
import cocoex
from numpy.random import rand
from pyDOE import *                       # alg = lhs
from cocoex.solvers import random_search  # alg = rs
import cma                                # alg = cma


def run_experiment(suite_name,
                   suite_options='',
                   observer_name='bbob',
                   observer_options='',
                   add_observer_name='rw',
                   add_observer_options='log_only_better: 0 log_variables: all',
                   alg='cma',
                   budget_multiplier=10):

    # prepare
    output_folder = suite_name + '-' + alg + '-' + observer_name
    if suite_name not in cocoex.known_suite_names:
        cocoex.known_suite_names.append(suite_name)
    suite = cocoex.Suite(suite_name, '', suite_options)
    observer = cocoex.Observer(observer_name, 'result_folder: {} {}'
                               ''.format(output_folder, observer_options))
    add_observer = None
    if add_observer_name != '':
        output_folder = suite_name + '-' + alg + '-' + add_observer_name
        add_observer = cocoex.Observer(add_observer_name, 'result_folder: {} {}'
                                                          ''.format(output_folder,
                                                                    add_observer_options))

    minimal_print = cocoex.utilities.MiniPrint()

    # go
    for problem in suite:
        problem.observe_with(observer)  # generates the data for cocopp post-processing
        if add_observer:
            problem.observe_with(add_observer)
        if alg == 'cma':
            x0 = problem.initial_solution
            # apply restarts while neither the problem is solved nor the budget is exhausted
            while problem.evaluations < problem.dimension * budget_multiplier:
                # CMA-ES
                cma.fmin(problem, x0, 0.1, options=dict(maxfevals=problem.dimension * budget_multiplier -
                                                                problem.evaluations,
                                                        bounds=[problem.lower_bounds,
                                                                problem.upper_bounds],
                                                        verbose=-9))
                x0 = problem.lower_bounds + ((rand(problem.dimension) + rand(problem.dimension)) *
                                             (problem.upper_bounds - problem.lower_bounds) / 2)
        elif alg == 'rs':
            # Use COCO's implementation of random search
            random_search(problem, problem.lower_bounds, problem.upper_bounds,
                          problem.dimension * budget_multiplier)
        elif alg == 'lhs':
            # Use Latin Hypercubes to sample the space
            data = lhs(n=problem.dimension, samples=problem.dimension * budget_multiplier)
            chunk_num = 0
            while problem.evaluations < problem.dimension * budget_multiplier:
                chunk_size = min(500, problem.dimension * budget_multiplier - problem.evaluations)
                chunk = data[chunk_num * chunk_size:(chunk_num + 1) * chunk_size]
                c = problem.lower_bounds + (problem.upper_bounds - problem.lower_bounds) * chunk
                [problem(x) for x in c]
        else:
            ValueError('Unknown algorithm')

        minimal_print(problem, final=problem.index == len(suite) - 1)

# export LD_LIBRARY_PATH='path_to_rw_top_trumps_library'
if __name__ == '__main__':
    run_experiment('rw-top-trumps', 'instance_indices: 1-3 dimensions: 128',
                   add_observer_name='rw',
                   add_observer_options='log_only_better: 0 log_variables: all precision_x: 1',
                   alg='cma', budget_multiplier=50)
    #run_experiment('rw-top-trumps-biob', 'instance_indices: 1-3 dimensions: 128',
    #               add_observer_name='rw',
    #               add_observer_options='log_only_better: 0 log_variables: all precision_x: 1',
    #               alg='cma', budget_multiplier=50)
    run_experiment('rw-gan-mario',
                   'function_indices: 3,6,9,12,15,18,21,24,27,30,33,36,39,42 instance_indices: 1 dimensions: 10',
                   alg='rs', budget_multiplier=20)
    run_experiment('rw-gan-mario',
                   'function_indices: 3,6,9,12,15,18,21,24,27,30,33,36,39,42 instance_indices: 1 dimensions: 10',
                   alg='cma', budget_multiplier=50)
