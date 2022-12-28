#! /usr/bin/python3

import sys
import time
import math

_verbose_ = False
_timed_output_ = False
_debug_ = False

_amino_acid_by_mass_ = {57:"G", 71:"A", 87:"S", 97:"P", 99:"V", 101:"T", 103:"C", 113:"L", 114:"N", 115:"D", 128:"Q", 129:"E", 131:"M", 137:"H", 147:"F", 156:"R", 163:"Y", 186:"W"}
_mass_by_amino_acid_ = {"G":57, "A":71, "S":87, "P":97, "V":99, "T":101, "C":103, "L":113, "N":114, "D":115, "Q":128, "E":129, "M":131, "H":137, "F":147, "R":156, "Y":163, "W":186, "I":113, "K":128}

def organize_inputs(input_file):

    with open(input_file) as f:
        weights = [int(s) for s in f.readline().rstrip().split()]

    if _debug_:
        print(weights)
        print()

    return weights

def write_spectrum_graph_edges(weights):
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

def generate_candidate_peptides(graph):
    peptides = []

    peptides += generate_candidate_peptides_from_node(graph, 0, 0)

    if _debug_:
        print(peptides)
        print()

    return peptides

def generate_candidate_peptides_from_node(graph, node_idx, indent):
    peptides = []

    node = graph[node_idx]

    if len(node[1]) > 0:
        for follow_node in node[1]:
            follow_node_idx = -1
            for g in range(len(graph)):
                if graph[g][0] == follow_node[0]:
                    follow_node_idx = g
                    break
            candidates = generate_candidate_peptides_from_node(graph, follow_node_idx, indent+1)
            for c in candidates:
                peptides.append(follow_node[1] + c)
    else:
        peptides.append("")
    
    return peptides

def generate_peptide_weights_from_peptides(peptides):
    peptides_spectrum_weights = []
    for peptide in peptides:
        reverse_count = 0
        peptide_weights = []
        while reverse_count < 2:
            last_weight = 0
            for ch in peptide:
                weight = last_weight + _mass_by_amino_acid_[ch]
                if weight not in peptide_weights:
                    peptide_weights.append(weight)
                last_weight = weight
            peptide = peptide[::-1]
            reverse_count += 1
        peptides_spectrum_weights.append(peptide_weights)
    
    if _debug_:
        for i in range(len(peptides)):
            print(peptides[i])
            print(peptides_spectrum_weights[i])
            print()
    
    return peptides_spectrum_weights

def filter_possible_peptides_by_observed_weight(possible_peptides, peptides_spectrum_weights, weights):
    weights.sort()

    results = []

    if len(possible_peptides) != len(peptides_spectrum_weights):
        raise ValueError("Expected possible peptides list {0} and possible peptides weights list {1} to be equal length.".format(str(len(possible_peptides)), str(len(peptides_spectrum_weights))))

    for i in range(len(possible_peptides)):
        candidate_weights = peptides_spectrum_weights[i]

        if len(candidate_weights) != len(weights):
            continue

        candidate_weights.sort()

        match = True
        for compare in zip(weights, candidate_weights):
            if compare[0] != compare[1]:
                match = False
                break
        
        if match:
            results.append(possible_peptides[i])

    for r in results:
        if r[::-1] in results:
            del results[results.index(r)]

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

    graph = write_spectrum_graph_edges(weights)

    possible_peptides = generate_candidate_peptides(graph)

    peptides_spectrum_weights = generate_peptide_weights_from_peptides(possible_peptides)

    correct_peptides = filter_possible_peptides_by_observed_weight(possible_peptides, peptides_spectrum_weights, weights)

    for line in correct_peptides:
        print(line)

    end = time.process_time()
    print("Time: {0}".format(end-start))
