#! /usr/bin/python3

import pytest
import math

import graph_possible_spectra

_test_base_dir_ = "graph_possible_spectra"

def init_test_from_file(path):

    weights = graph_possible_spectra.organize_inputs(path)

    graph = graph_possible_spectra.decode_ideal_spectrum(weights)

    return graph_possible_spectra.write_graph_vectors(graph)

def file_based_test(in_file, assert_file):
    results = init_test_from_file(in_file)

    assert_vals = []
    with open(assert_file) as f:
        line = f.readline()
        while line:
            if len(line.rstrip()) > 0:
                assert_vals.append(line.rstrip())
            line = f.readline()

    assert len(results) == len(assert_vals)
    
    for i in range(len(results)):
        if results[i][len(results[i])-1] in ["I","L","K","Q"]:
            if results[i][len(results[i])-1] in ["I","L"]:
                if results[i][0:len(results[i])-1] + "I" == assert_vals[i] or results[i][0:len(results[i])-1] + "L" == assert_vals[i]:
                    assert True
                    print("got i/l")
                else:
                    assert results[i][0:len(results[i])-1] + "I/L" == assert_vals[i] 
            else:
                if results[i][0:len(results[i])-1] + "K" == assert_vals[i] or results[i][0:len(results[i])-1] + "Q" == assert_vals[i]:
                    assert True
                    print("got k/q")
                else:
                    assert results[i][0:len(results[i])-1] + "K/Q" == assert_vals[i] 
        else:
            assert results[i] == assert_vals[i]
    

def _test_sample_n(n):
    rt = "test/{0}/".format(_test_base_dir_)
    file_based_test(rt + "input/sample_" + str(n) + ".txt", rt + "output/sample_" + str(n) + ".txt")

def test_sample_0():
    _test_sample_n(0)

def test_sample_1():
    _test_sample_n(1)

# def test_sample_2():
#     _test_sample_n(2)

# def xtest_sample_3():
#     _test_sample_n(3)

# def xtest_sample_4():
#     _test_sample_n(4)

# def xtest_sample_5():
#     _test_sample_n(5)

# def xtest_sample_6():
#     _test_sample_n(6)


