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
        graph = {}
        while line:
            if idx == 0:
                output_size = int(line.rstrip())
            else:
                weight_split = line.rstrip().split(":")
                node_split = weight_split[0].split("->")

                weight = int(weight_split[1])
                node1 = int(node_split[0])
                node2 = int(node_split[1])

                if node1 not in graph:
                    graph[node1] = {}

                if node2 not in graph[node1]:
                    graph[node1][node2] = weight
                else:
                    raise ValueError("Duplicate node pair definition in input file: n1 {0} n2 {1} weight {2}.".format(str(node1), str(node2), str(weight)))

                if node1 > max_node:
                    max_node = node1
                if node2 > max_node:
                    max_node = node2

            idx += 1
            line = f.readline()

    return graph, output_size, max_node

def copy_reflected_graph_values(graph):
    for i in range(len(graph)):
        for j in range(i, len(graph[i])):
            if graph[i][j] == -1 and graph[j][i] != -1:
                graph[i][j] = graph[j][i]
            if graph[j][i] == -1 and graph[i][j] != -1:
                graph[j][i] = graph[i][j]
    return

def populate_initial_tree(graph_nodes, max_node):
    full_graph = []
    direct_connections_graph = []
    for n in range(max_node+1):
        full_graph.append([-1]*(max_node+1))
        direct_connections_graph.append([0]*(max_node+1))

    for idx in range(max_node+1):
        node = graph_nodes[idx]
        for k,v in node.items():
            full_graph[idx][k] = v
            direct_connections_graph[idx][k] = 1

    for i in range(len(full_graph)):
        full_graph[i][i] = 0

    copy_reflected_graph_values(full_graph)
    copy_reflected_graph_values(direct_connections_graph)
    if _verbose_:
        for d in full_graph:
            print(d)
        print()
        for d in direct_connections_graph:
            print(d)
        print()

    leaf_nodes = []
    for i in range(len(direct_connections_graph)):
        connections = 0
        for j in range(len(direct_connections_graph[i])):
            connections+=direct_connections_graph[i][j]
        if _debug_:
            print(connections)
        if connections == 1:
            leaf_nodes.append(i)

    return full_graph, leaf_nodes

def create_leaf_nodes_graph(full_graph, leaf_nodes):
    leaf_nodes_graph = []
    for i in range(len(leaf_nodes)):
        leaf_row_values = []
        for j in range(len(leaf_nodes)):
            leaf_row_values.append(full_graph[i][j])
        leaf_nodes_graph.append(leaf_row_values)

    if _verbose_:
        for d in leaf_nodes_graph:
            print(" ".join([str(z).rjust(4) for z in d]))
        print()

    return leaf_nodes_graph

def build_tree_and_build_matrix_from_tree(graph_nodes, output_size, max_node):
    full_graph, leaf_nodes = populate_initial_tree(graph_nodes, max_node)

    uncalculated_weights = True
    test_int = 2
    while uncalculated_weights:
        uncalculated_weights = False
        for i in range(len(full_graph)):
            for j in range(len(full_graph[i])):
                if full_graph[i][j] != -1:
                    for k in range(len(full_graph)):
                        if full_graph[k][i] != -1 and full_graph[k][j] == -1:
                            full_graph[k][j] = full_graph[k][i] + full_graph[i][j]
                else:
                    if _debug_:
                        print("-1 at {0},{1}".format(str(i), str(j)))
                    uncalculated_weights = True
                if _debug_:
                    print("i, j = {0}, {1}".format(str(i), str(j)))
                    for d in full_graph:
                        print(" ".join([str(z).rjust(4) for z in d]))
                    print()

        # test_int -= 1
        # if test_int < 1:
        #     uncalculated_weights = False
        copy_reflected_graph_values(full_graph)
        if _verbose_:
            for d in full_graph:
                print(" ".join([str(z).rjust(4) for z in d]))
            print()

    results_graph = create_leaf_nodes_graph(full_graph, leaf_nodes)

    return results_graph

if __name__ == '__main__':
    start = time.process_time()

    if len(sys.argv) < 2:
        print("Expected input:\n[str: filename path]\n\nfile contents:\n[int: output matrix size]\n[string: int1->int2:int3, connection between int1 and int2 of weight int3]\n")

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
    
    graph_nodes, output_size, max_node = organize_inputs(sys.argv[1])

    if output_size < 1:
        raise ValueError("output_size incorrect value {0}".format(str(output_size)))
    if max_node < 1:
        raise ValueError("max_node incorrect value {0}".format(str(max_node)))


    results = build_tree_and_build_matrix_from_tree(graph_nodes, output_size, max_node)

    for r in results:
        print(" ".join([str(n).ljust(4) for n in r]))

    end = time.process_time()
    print("Time: {0}".format(end-start))