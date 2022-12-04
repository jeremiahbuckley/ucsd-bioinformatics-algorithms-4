#! /usr/bin/python3

import pytest

import calculate_limb_length

def init_test_from_file(path):

    graph_size, leaf_id, graph = calculate_limb_length.organize_inputs(path)

    return calculate_limb_length.calc_leaf_limb_length(graph, graph_size, leaf_id)


def file_based_test(in_file, assert_file):
    result = init_test_from_file(in_file)
    with open(assert_file) as f:
        assert_val = int(f.readline().rstrip())

    assert result == assert_val



def test_sample_0():
    rt = "test/calculate_limb_length/"
    file_based_test(rt + "input/sample_0.txt", rt + "output/sample_0.txt")


def test_sample_1():
    rt = "test/calculate_limb_length/"
    file_based_test(rt + "input/sample_1.txt", rt + "output/sample_1.txt")

