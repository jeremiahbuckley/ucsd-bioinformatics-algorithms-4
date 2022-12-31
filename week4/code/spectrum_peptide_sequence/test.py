#! /usr/bin/python3

import sys
import pytest
import math

import decode_ideal_spectrum

_test_base_dir_ = "decode_ideal_spectrum"

def init_test_from_file(path):

    weights = decode_ideal_spectrum.organize_inputs(path)

    graph = decode_ideal_spectrum.write_spectrum_graph_edges(weights)

    possible_peptides = decode_ideal_spectrum.generate_candidate_peptides(graph)

    peptides_spectrum_weights = decode_ideal_spectrum.generate_peptide_weights_from_peptides(possible_peptides)

    return decode_ideal_spectrum.filter_possible_peptides_by_observed_weight(possible_peptides, peptides_spectrum_weights, weights)

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
        if results[i] in assert_vals or results[i][::-1] in assert_vals:
            assert True
            print("found match")
        else:
            assert results[i] == "xyz"
    

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


