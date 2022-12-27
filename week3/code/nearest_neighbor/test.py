#! /usr/bin/python3

import pytest
import math

import large_parsimony

def init_test_from_file(path):

    edges, target_edge_nodes = large_parsimony.organize_inputs(path)

    edges_collection = large_parsimony.swap_edges(edges, target_edge_nodes)

    outstr_set = []
    for e in edges_collection:
        outstr_set.append(large_parsimony.print_edges_strings(e))
    
    return outstr_set


def file_based_test(in_file, assert_file):
    print(in_file)
    print(assert_file)
    
    results_sets = init_test_from_file(in_file)
    print(results_sets)

    assert_sets = []
    with open(assert_file) as f:
        line = f.readline()
        assert_set = []
        while line:
            if len(line.rstrip()) == 0:
                assert_sets.append(assert_set)
                assert_set = []
            else:
                assert_set.append(line.rstrip())

            line = f.readline()
    if len(assert_set) > 0:
        assert_sets.append(assert_set)
    
    print(assert_sets)

    if len(assert_sets) > 1:
        for i in range(1, len(assert_sets)):
            assert len(assert_sets[i-1]) == len(assert_sets[i])

    assert_sets_verified_indexes = []
    for results in results_sets:
        matched_result_set_with_asset_set = False
        for assert_set_idx in range(len(assert_sets)):
            if assert_set_idx not in assert_sets_verified_indexes:
                aset = assert_sets[assert_set_idx]

                assert len(results) == len(aset)

                seen_it = {}
                found_mismatch = False
                for edge in results:
                    if edge not in seen_it and edge in aset:
                        seen_it[edge]=True
                    else:
                        found_mismatch = True
            
                if not found_mismatch:
                    matched_result_set_with_asset_set = True
                    assert_sets_verified_indexes.append(assert_set_idx)

        if not matched_result_set_with_asset_set:
            print("No match for:")
            print(results)
            assert matched_result_set_with_asset_set == True



def _test_sample_n(n):
    rt = "test/large_parsimony/"
    file_based_test(rt + "input/sample_" + str(n) + ".txt", rt + "output/sample_" + str(n) + ".txt")

def test_sample_0():
    _test_sample_n(0)

def test_sample_1():
    _test_sample_n(1)

def test_sample_2():
    _test_sample_n(2)

# def xtest_sample_3():
#     _test_sample_n(3)

# def xtest_sample_4():
#     _test_sample_n(4)

# def xtest_sample_5():
#     _test_sample_n(5)

# def xtest_sample_6():
#     _test_sample_n(6)


