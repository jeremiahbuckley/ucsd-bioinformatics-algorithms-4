#! /usr/bin/python3

import pytest
import math

import rootless_small_parsimony

def init_test_from_file(path):

    graph = rootless_small_parsimony.organize_inputs(path)

    return rootless_small_parsimony.build_tree_from_graph(graph)


def file_based_test(in_file, assert_file):
    results = init_test_from_file(in_file)
    with open(assert_file) as f:
        assert_vals = f.readlines()
    
    weights = []
    for av in assert_vals:
        if len(av.rstrip()) > 0:
            values = av.rstrip().split(":")
            weights.append(float(values[1]))

    assert len(results) == len(weights)

    results_dict = {}
    for node in results:
        rw = round(node[2], 3)
        if rw not in results_dict:
            results_dict[rw] = 0
        results_dict[rw] += 1
    
    weights_dict = {}
    for weight in weights:
        if weight not in weights_dict:
            weights_dict[weight] = 0
        weights_dict[weight] += 1

    assert len(results_dict) == len(weights_dict)
    print(results_dict)
    print(weights_dict)
    for k, v in results_dict.items():
        if k in weights_dict:
            assert results_dict[k] == weights_dict[k]
        else:
            print(k)
            assert False


def _test_sample_n(n):
    rt = "test/upgma/"
    file_based_test(rt + "input/sample_" + str(n) + ".txt", rt + "output/sample_" + str(n) + ".txt")

def test_sample_0():
    _test_sample_n(0)