#! /usr/bin/python3

import sys
import time
import math

_verbose_ = False
_timed_output_ = False
_debug_ = False

def organize_inputs(input_file):
    output_size = -1
    max_node = -1

    with open(input_file) as f:
        line = f.readline()

        idx = 0
        graph = []
        while line:
            if idx == 0:
                graph_size = int(line.rstrip())
            elif idx == 1:
                leaf_id = int(line.rstrip())
            else:
                graph.append([int(n) for n in line.rstrip().split()])

            idx += 1
            line = f.readline()

    if _debug_:
        print(graph_size)
        print(leaf_id)
        for line in graph:
            print(" ".join([str(n).rjust(4) for n in line]))
        print()

    return graph_size, leaf_id, graph

def calc_leaf_limb_length(graph, graph_size, leaf_id):
    min_length = 1000000
    for i in range(graph_size-1):
        for j in range(i+1, graph_size):
            if i != leaf_id and j != leaf_id:
                if _debug_:
                    print("leaf_id={3} i={0} and j={1} min_length={2}".format(str(i), str(j), str(min_length), str(leaf_id)))
                    print(graph[leaf_id][i])
                    print(graph[leaf_id][j])
                    print(graph[i][0])
                    print(graph[i][j])
                    print()
                cur_val = int((graph[leaf_id][i] + graph[leaf_id][j] - graph[i][j]) / 2)
                if cur_val < min_length:
                    min_length = cur_val

            
    return min_length

if __name__ == '__main__':
    start = time.process_time()

    if len(sys.argv) < 2:
        print("Expected input:\n[str: filename path]\n\nfile contents:\n[int: output matrix size]\n[int: leaf to find]\n[string: int1->int2:int3, connection between int1 and int2 of weight int3]\n")

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
    
    graph_size, leaf_id, graph = organize_inputs(sys.argv[1])

    if graph_size < 1:
        raise ValueError("output_size incorrect value {0}".format(str(output_size)))
    if leaf_id < 1:
        raise ValueError("max_node incorrect value {0}".format(str(max_node)))


    results = calc_leaf_limb_length(graph, graph_size, leaf_id)

    print(results)

    end = time.process_time()
    print("Time: {0}".format(end-start))
