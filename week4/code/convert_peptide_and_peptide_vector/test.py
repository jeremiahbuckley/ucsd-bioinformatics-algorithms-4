#! /usr/bin/python3

import pytest
import math

import convert_peptide_and_peptide_vector

_test_base_dir_1_ = "convert_peptide_to_peptide_vector"
_test_base_dir_2_ = "convert_peptide_vector_to_peptide"


def init_test_from_file(path, peptide_to_vector):

    in_val = convert_peptide_and_peptide_vector.organize_inputs(path, peptide_to_vector)

    if peptide_to_vector:
        out_val1 = convert_peptide_and_peptide_vector.convert_peptide_to_peptide_vector(in_val)
        out_val = " ".join([str(i) for i in out_val1])
    else:
        out_val = convert_peptide_and_peptide_vector.convert_peptide_vector_to_peptide(in_val)
    
    return out_val

def file_based_test(in_file, assert_file, peptide_to_vector):
    results = init_test_from_file(in_file, peptide_to_vector)

    assert_vals = None
    with open(assert_file) as f:
        assert_vals = f.readline().rstrip()

    assert results == assert_vals
    
    

def _test_sample_n(n, peptide_to_vector):
    rt = ""
    if peptide_to_vector:
        rt = "test/{0}/".format(_test_base_dir_1_)
    else:
        rt = "test/{0}/".format(_test_base_dir_2_)
    file_based_test(rt + "input/sample_" + str(n) + ".txt", rt + "output/sample_" + str(n) + ".txt", peptide_to_vector)

def test_sample_0pv():
    _test_sample_n(0, True)

def test_sample_0vp():
    _test_sample_n(0, False)

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


