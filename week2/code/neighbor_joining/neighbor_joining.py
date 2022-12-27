#! /usr/bin/python3

import sys
import time
import math

_verbose_ = False
_timed_output_ = False
_debug_ = False

def organize_inputs(input_file):
    graph_size = -1

    with open(input_file) as f:
        line = f.readline()

        idx = 0
        graph = []
        while line:
            cleanline = line.rstrip()
            if len(cleanline) > 0:
                if idx == 0:
                    graph_size = int(cleanline)
                else:
                    graph.append([int(n) for n in cleanline.split()])

                idx += 1
            line = f.readline()

    if _debug_:
        print_graph(graph)
        print()

    return graph

def confirm_graph_consistency(graph, graph_name):
    for i in range(len(graph)):
        for j in range(i, len(graph)):
            if i == j: 
                if graph[i][j] != 0:
                    print_graph(graph)
                    raise ValueError("Graph consistency - {0} - Expected 0 at {0}[{1}][{2}], got {3}".format(graph_name, str(i), str(j), str(graph[i][j])))
            else:
                if graph[i][j] != graph[j][i]:
                    print_graph(graph)
                    raise ValueError("Graph consistency - {0} - Values must equal {0}[{1}][{2}] and {0}[{2}][{1}], got {3} != {4}".format(graph_name, str(i), str(j), str(graph[i][j]), str(graph[j][i])))

def print_graph(graph, tab_count=0):
    for r in graph:
        print("\t" * tab_count + " ".join([str(n).rjust(6) for n in r]))

def print_tree(tree, tab_count=0):
    for n in tree:
        print("\t"* tab_count + format_tree_node_output(n))

def format_tree_node_output(node):
    return format_tree_node_elements_output(node[0], node[1], node[2])
    # return format_tree_node_elements_output(node[0], node[1], node[2], node[3])

def format_tree_node_elements_output(from_node, to_node, weight, total_weight=-1):
    return "{0}->{1}:{2}".format(str(from_node), str(to_node), str(round(weight, 3)))
    # return "{0}->{1}:{2}      ({3})".format(str(from_node), str(to_node), str(round(weight, 3)), str(total_weight))

def build_tree_from_graph(graph):

    tree = []
    tree, current_max_node_idx = build_tree_from_graph_recursive(graph, tree, [-1] * len(graph), -1, 0)
    return format_for_desired_output(tree)

def build_tree_from_graph_recursive(graph, tree, graph_idx_to_node_idx_map, current_max_tree_idx, depth):
    if _debug_:
        print("\t" * depth + "build tree from graph recursive - start")
        print_graph(graph, depth)
        print()
        print_tree(tree, depth)
        print()
        print("\t" * depth + "graph to node map=[{0}], current_max_node_idx={1}".format(", ".join([str(k) for k in graph_idx_to_node_idx_map]), str(current_max_tree_idx)))

    if len(graph) < 2:
        raise ValueError("Unexpected graph size < 2.")

    if len(graph) == 2:
        new_tree = []
        if graph_idx_to_node_idx_map[0] == -1:
            current_max_tree_idx += 1
            graph_idx_to_node_idx_map[0] = current_max_tree_idx
        if graph_idx_to_node_idx_map[1] == -1:
            current_max_tree_idx += 1
            graph_idx_to_node_idx_map[1] = current_max_tree_idx
        new_tree.append((graph_idx_to_node_idx_map[0], graph_idx_to_node_idx_map[1], graph[0][1]))

        return new_tree, current_max_tree_idx


    distance_graph, sum_distances = build_distance_graph(graph, depth)
    if _debug_:
        print_graph(distance_graph, depth)
        print()

    vert_idx, horz_idx, min_distance = find_nearest_neighbor(distance_graph)
    if _debug_:
        print("\t" * depth + "vert_idx={0} horz_idx={1}.".format(str(vert_idx), str(horz_idx)))
    if graph_idx_to_node_idx_map[vert_idx] == -1:
        current_max_tree_idx += 1
        graph_idx_to_node_idx_map[vert_idx] = current_max_tree_idx
    if graph_idx_to_node_idx_map[horz_idx] == -1:
        current_max_tree_idx += 1
        graph_idx_to_node_idx_map[horz_idx] = current_max_tree_idx

    if vert_idx >= horz_idx:
        raise ValueError("Unexpected, vert_idx ({0}) >= horz_idx ({1}).".format(str(vert_idx), str(horz_idx)))

    distance_delta = (sum_distances[vert_idx] - sum_distances[horz_idx]) / (len(graph) - 2)
    limb_length_vert = (graph[vert_idx][horz_idx] + distance_delta) / 2
    limb_length_horz = (graph[vert_idx][horz_idx] - distance_delta) / 2

    new_graph, new_graph_idx_to_node_idx_map, new_current_max_tree_idx = chop_down_graph(graph, vert_idx, horz_idx, limb_length_vert, limb_length_horz, graph_idx_to_node_idx_map, current_max_tree_idx, depth)

    new_tree, new_current_max_tree_idx = build_tree_from_graph_recursive(new_graph, tree, new_graph_idx_to_node_idx_map, new_current_max_tree_idx, depth+1)

    new_tree.append((graph_idx_to_node_idx_map[vert_idx], new_graph_idx_to_node_idx_map[len(new_graph_idx_to_node_idx_map)-1], limb_length_vert))
    new_tree.append((graph_idx_to_node_idx_map[horz_idx], new_graph_idx_to_node_idx_map[len(new_graph_idx_to_node_idx_map)-1], limb_length_horz))

    if _debug_:
        print("\t" * depth + "build tree from graph recursive - end")
        print_graph(graph, depth)
        print()
        print_graph(new_graph, depth)
        print()
        print_tree(new_tree, depth)
        print()

    return new_tree, new_current_max_tree_idx

def chop_down_graph(graph, vert_idx, horz_idx, limb_length_vert, limb_length_horz, graph_idx_to_node_idx_map, current_max_tree_idx, depth):
    if _debug_:
        print("\t" * depth + "chop down graph - start")
        print_graph(graph, depth)
        print("\t" * depth + "vert_idx={0} horz_idx={1} vert_limb_length={2} horz_limb_length={3}".format(str(vert_idx), str(horz_idx), str(limb_length_vert), str(limb_length_horz)))
        print()

    new_graph = []

    for i in range(len(graph)):
        new_row = []
        for j in range(len(graph)):
            new_row.append(graph[i][j])
        new_graph.append(new_row)

    new_row = []
    new_graph_idx_to_tree_idx_map = []
    for i in range(len(graph)):
        if i == vert_idx or i == horz_idx:
            new_graph[i].append(0)
            new_row.append(0)
        else:
            new_distance = (graph[vert_idx][i] + graph[horz_idx][i] - limb_length_vert - limb_length_horz) / 2
            new_graph[i].append(new_distance)
            new_row.append(new_distance)
            new_graph_idx_to_tree_idx_map.append(graph_idx_to_node_idx_map[i])
    new_row.append(0)
    new_graph.append(new_row)

    current_max_tree_idx += 1
    new_graph_idx_to_tree_idx_map.append(current_max_tree_idx)

    for row in new_graph:
        del row[horz_idx]
        del row[vert_idx]
    del new_graph[horz_idx]
    del new_graph[vert_idx]

    if _debug_:
        print("\t" * depth + "chop down graph - return")
        print_graph(new_graph, depth)
        print()
    return new_graph, new_graph_idx_to_tree_idx_map, current_max_tree_idx

def build_distance_graph(graph, depth):
    if _debug_:
        print("\t" * depth + "build distance graph - start")
        print_graph(graph, depth)
        print()

    graph_size_less_2 = len(graph) - 2

    sum_distances = []
    for row in graph:
        sum_distances.append(sum(row))

    if _debug_:
        print("\t" * depth +  "[{0}]".format(", ".join([str(n) for n in sum_distances])))

    distance_graph = [] 
    for i in range(len(graph)):
        distance_row = []
        for j in range(len(graph)):
            if j <= i:
                distance_row.append(0)
            else:
                distance_row.append(graph[i][j] * graph_size_less_2 - sum_distances[i] - sum_distances[j])
        distance_graph.append(distance_row)

    for i in range(len(graph) - 1):
        for j in range(i+1, len(graph)):
            distance_graph[j][i] = distance_graph[i][j]

    if _debug_:
        print("\t" * depth + "build distance graph - end")
        print_graph(distance_graph, depth)
        print()
    confirm_graph_consistency(distance_graph, "distance_graph_" + str(depth))
    return distance_graph, sum_distances


def format_for_desired_output(tree):
    formatted_tree = []
    for node in tree:
        formatted_tree.append((node[0], node[1], node[2]))
        formatted_tree.append((node[1], node[0], node[2]))

    formatted_tree.sort(key=lambda node: node[0] * 10000 + node[1])

    return formatted_tree

def find_nearest_neighbor(distance_graph):
    min_distance = sys.maxsize
    vert_idx = -1
    horz_idx = -1

    for i in range(len(distance_graph) - 1):
        for j in range(i+1, len(distance_graph)):
            if distance_graph[i][j] < min_distance:
                min_distance = distance_graph[i][j]
                vert_idx = i
                horz_idx = j
    
    return vert_idx, horz_idx, min_distance
    
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
    
    graph = organize_inputs(sys.argv[1])

    if len(graph) < 1:
        raise ValueError("output_size incorrect value {0}".format(str(len(graph))))


    results = build_tree_from_graph(graph)

    for r in results:
        print(format_tree_node_output(r))

    end = time.process_time()
    print("Time: {0}".format(end-start))