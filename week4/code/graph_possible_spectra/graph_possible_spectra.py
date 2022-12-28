#! /usr/bin/python3

import sys
import time
import math

_verbose_ = False
_timed_output_ = False
_debug_ = False

_amino_acid_by_mass_ = {57:"G", 71:"A", 87:"S", 97:"P", 99:"V", 101:"T", 103:"C", 113:"L", 114:"N", 115:"D", 128:"Q", 129:"E", 131:"M", 137:"H", 147:"F", 156:"R", 163:"Y", 186:"W"}

def organize_inputs(input_file):

    with open(input_file) as f:
        weights = [int(s) for s in f.readline().rstrip().split()]

    if _debug_:
        print(weights)
        print()

    return weights

def decode_ideal_spectrum(weights):
    decoded_weights = [(0,[])]

    for weight in weights:
        for dw in decoded_weights:
            delta = weight - dw[0]
            if delta in _amino_acid_by_mass_:
                dw[1].append((weight, _amino_acid_by_mass_[delta]))

                if len([node for node in decoded_weights if node[0] == weight]) == 0:
                    decoded_weights.append((weight,[]))
    
    if _debug_:
        print(decoded_weights)
        print()

    return decoded_weights

def write_graph_vectors(graph):
    results = []
    for node in graph:
        for endpoint in node[1]:
            results.append("{0}->{1}:{2}".format(str(node[0]), str(endpoint[0]), endpoint[1]))

    return results


if __name__ == '__main__':
    start = time.process_time()

    if len(sys.argv) < 2:
        print("Expected input:\n[str: filename path]\n\nfile contents:\n[int: graph size]\n[string: one row of graph [1...n]]\n")

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
    
    weights = organize_inputs(sys.argv[1])

    graph = decode_ideal_spectrum(weights)

    printable_results = write_graph_vectors(graph)

    for line in printable_results:
        print(line)

    end = time.process_time()
    print("Time: {0}".format(end-start))