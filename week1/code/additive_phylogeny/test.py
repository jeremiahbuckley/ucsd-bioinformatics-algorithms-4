#! /usr/bin/python3

import pytest

import additive_phylogeny

def init_test_from_file(path):

    graph = additive_phylogeny.organize_inputs(path)

    return additive_phylogeny.build_tree_from_graph(graph)


def file_based_test(in_file, assert_file):
    results = init_test_from_file(in_file)
    with open(assert_file) as f:
        assert_vals = f.readlines()
    
    weights = []
    for av in assert_vals:
        if len(av.rstrip()) > 0:
            values = av.rstrip().split(":")
            weights.append(int(values[1]))

    assert len(results) == len(weights)

    matched_indexes = []
    for i in range(len(results)):
        print(i)

        found_match = False
        for j in range(len(weights)):
            if j not in matched_indexes and weights[j] == results[i][2] and not found_match:
                print(j)
                matched_indexes.append(j)
                found_match = True
        
        assert found_match == True


def _test_sample_n(n):
    rt = "test/additive_phylogeny/"
    file_based_test(rt + "input/sample_" + str(n) + ".txt", rt + "output/sample_" + str(n) + ".txt")

def test_sample_0():
    _test_sample_n(0)

def test_sample_1():
    _test_sample_n(1)

def test_sample_2():
    _test_sample_n(2)

def test_sample_3():
    _test_sample_n(3)

def test_sample_4():
    _test_sample_n(4)

def test_sample_5():
    _test_sample_n(5)

def test_sample_6():
    _test_sample_n(6)


