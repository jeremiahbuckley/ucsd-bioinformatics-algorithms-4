#! /usr/bin/python3

import pytest

import distance_between_leaves

def init_test_from_file(path):

    graph_nodes, output_size, max_node = distance_between_leaves.organize_inputs(path)

    return distance_between_leaves.build_tree_and_build_matrix_from_tree(graph_nodes, output_size, max_node)


def file_based_test(in_file, assert_file):
    results = init_test_from_file(in_file)
    with open(assert_file) as f:
        assert_vals = f.readlines()

    assert len(results) == len(assert_vals)

    for i in range(len(results)):
        result_row = results[i]
        # result_row = [int(n)  for n in results[i].split()]
        assert_row = [int(n) for n in assert_vals[i].split()]
        
        assert len(result_row) == len(assert_row)

        for j in range(len(result_row)):
            assert result_row[j] == assert_row[j]


def test_sample_0():
    rt = "test/distance_between_leaves/"
    file_based_test(rt + "input/sample_0.txt", rt + "output/sample_0.txt")


def test_sample_1():
    rt = "test/distance_between_leaves/"
    file_based_test(rt + "input/sample_1.txt", rt + "output/sample_1.txt")

