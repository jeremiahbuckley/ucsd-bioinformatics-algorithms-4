#! /usr/bin/python3

import sys
import time
import math

_verbose_ = False
_timed_output_ = False
_debug_ = False

def organize_inputs(input_file):

    edges = {}
    with open(input_file) as f:
        target_edge_nodes = f.readline().rstrip().split(" ")

        line = f.readline()
        while line:
            edge = line.rstrip().lstrip().split("->")

            if edge[0] not in edges:
                edges[edge[0]] = [edge[1]]
            else:
                edges[edge[0]].append(edge[1])
            
            line = f.readline()
    
    if _debug_:
        print(target_edge_nodes)
        print(edges)
        print_edges(edges)
        print()

    return edges, target_edge_nodes

def print_edges(edges):
    for k,v in edges.items():
        for endpoint in v:
            print("{0}->{1}".format(k, endpoint))

def swap_edges(edges, target_edge_nodes):

    # 1  3
    # 2  4

    # 1  3
    # 4  2

    # 1  2
    # 3  4




    # 3  1
    # 2  4

    # 4  3
    # 2  1

    # 2  3
    # 1  4

    first_swap = []
    second_swap = []
    ec = edges[target_edge_nodes[0]]
    for c in ec:
        if c != target_edge_nodes[1]:
            first_swap.append(c)
            second_swap.append(c)
            break

    if _debug_:
        print("first_swap, second_swap")
        print(first_swap)
        print(second_swap)

    
    ec = edges[target_edge_nodes[1]]
    found_first_swap = False
    for c in ec:
        if c != target_edge_nodes[0]:
            if not found_first_swap:
                first_swap.append(c)
                found_first_swap = True
            else:
                second_swap.append(c)
                break
    
    if _debug_:
        print("first_swap, second_swap")
        print(first_swap)
        print(second_swap)

    new_edges = {}
    for k,v in edges.items():
        if k in first_swap:
            other_ends = []
            for end in v:
                if end == target_edge_nodes[0]:
                    other_ends.append(target_edge_nodes[1])
                elif end == target_edge_nodes[1]:
                    other_ends.append(target_edge_nodes[0])
                else:
                    other_ends.append(end)
            new_edges[k] = other_ends
        elif k in target_edge_nodes:
            other_ends = []
            for end in v:
                if end == first_swap[0]:
                    other_ends.append(first_swap[1])
                elif end == first_swap[1]:
                    other_ends.append(first_swap[0])
                else:
                    other_ends.append(end)
            new_edges[k] = other_ends
        else:
            new_edges[k] = v

    new_edges_2 = {}
    for k,v in edges.items():
        if k in second_swap:
            other_ends = []
            for end in v:
                if end == target_edge_nodes[0]:
                    other_ends.append(target_edge_nodes[1])
                elif end == target_edge_nodes[1]:
                    other_ends.append(target_edge_nodes[0])
                else:
                    other_ends.append(end)
            new_edges_2[k] = other_ends
        elif k in target_edge_nodes:
            other_ends = []
            for end in v:
                if end == second_swap[0]:
                    other_ends.append(second_swap[1])
                elif end == second_swap[1]:
                    other_ends.append(second_swap[0])
                else:
                    other_ends.append(end)
            new_edges_2[k] = other_ends
        else:
            new_edges_2[k] = v

    return new_edges, new_edges_2
            


if __name__ == '__main__':
    start = time.process_time()

    if len(sys.argv) < 2:
        print("Expected input:\n[str: filename path]\n\nfile contents:\n[int: leaf node count]\n[string: one leaf node [1...n]]\n[string: one inner node edge [1...n]\n")

    for a_idx in  range(2,3,1):
        if len(sys.argv) > a_idx:
            if sys.argv[a_idx] == "-v":
                _verbose_ = True
            if sys.argv[a_idx] == "-vv":
                _verbose_ = True
                _timed_output_ = True
            if sys.argv[a_idx] == "-vvv":
                _verbose_ = True
                _timed_output_ = True
                _debug_ = True
    
    edges, target_edge_nodes = organize_inputs(sys.argv[1])

    results = swap_edges(edges, target_edge_nodes)

    print_edges(results[0])
    print()
    print_edges(results[1])

    end = time.process_time()
    print("Time: {0}".format(end-start))