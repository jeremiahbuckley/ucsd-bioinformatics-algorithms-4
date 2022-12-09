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

def print_node_lookup_dictionary(dict, tab_count=0):
    for k, v in dict.items():
        print("\t" * tab_count + "{0} : {1}".format(str(k), str(v)))



def format_tree_node_output(node):
    return format_tree_node_elements_output(node[0], node[1], node[2], node[3])

def format_tree_node_elements_output(from_node, to_node, weight, total_weight=-1):
    return "{0}->{1}:{2}".format(str(from_node), str(to_node), str(round(weight, 3)))
    # return "{0}->{1}:{2}      ({3})".format(str(from_node), str(to_node), str(round(weight, 3)), str(total_weight))

def add_new_nodes_to_tree(tree, distance, vert_idx, horz_idx, max_current_node, node_lookup, last_graph_idx, depth):
    if _debug_:
        print("\t" * depth + "add nodes to tree - start")
        print_tree(tree, depth)
        print_node_lookup_dictionary(node_lookup, depth)
        print("\t" * depth + "vert: {0} horz: {1} distance: {2} max_current_node: {3} last_graph_idx: {4}".format(str(vert_idx), str(horz_idx), str(distance), str(max_current_node), str(last_graph_idx)))
        print()

    new_node = max_current_node+1
    number_of_leaves_in_new_node = node_lookup[vert_idx][1] + node_lookup[horz_idx][1]
    node_lookup[last_graph_idx+1] = (new_node, number_of_leaves_in_new_node)
    # node_lookup[new_node] = "[{0}.{1} {0}.{2}] -> {3}.{4}".format(str(depth), str(vert_idx), str(horz_idx), str(depth+1), str(last_graph_idx-1))
    distance_already_covered = 0
    half_distance = distance / 2.0
    for node in tree:
        if node[1] == node_lookup[vert_idx][0]:
            distance_already_covered = node[3]
    tree.append((node_lookup[vert_idx][0], new_node, half_distance - distance_already_covered, half_distance))
    distance_already_covered = 0
    for node in tree:
        if node[1] == node_lookup[horz_idx][0]:
            distance_already_covered = node[3]
    tree.append((node_lookup[horz_idx][0], new_node, half_distance - distance_already_covered, half_distance))

    if _debug_:
        print("\t" * depth + "add nodes to tree - return")
        print_tree(tree, depth)
        print_node_lookup_dictionary(node_lookup, depth)
        print()
        
    return tree, new_node, node_lookup

def reshape_graph(graph, vert_idx, horz_idx, node_lookup, depth):
    if _debug_:
        print("\t" * depth + "reshape graph - start")
        print_graph(graph, depth)
        print_node_lookup_dictionary(node_lookup, depth)
        print("\t" * depth + "vert_idx={0} horz_idx={1}".format(str(vert_idx), str(horz_idx)))
        print()
    
    if horz_idx <= vert_idx:
        raise ValueError("Expect vert_idx {0} to be < horz_idx.".format(str(vert_idx), str(horz_idx)))

    number_of_leaves_in_new_node = node_lookup[vert_idx][1] + node_lookup[horz_idx][1]

    for row in graph:
        row.append(((row[vert_idx] * node_lookup[vert_idx][1]) + (row[horz_idx] * node_lookup[horz_idx][1])) / number_of_leaves_in_new_node)
    
    new_row = []
    for i in range(len(graph[0])):
        new_row.append(((graph[vert_idx][i] * node_lookup[vert_idx][1]) + (graph[horz_idx][i] * node_lookup[horz_idx][1])) / number_of_leaves_in_new_node)
    graph.append(new_row)

    graph[len(graph)-1][len(graph)-1] = 0

    del graph[horz_idx]
    del graph[vert_idx]
    for row in graph:
        del row[horz_idx]
        del row[vert_idx]
    
    confirm_graph_consistency(graph, "graph-depth-" + str(depth))

    delete_list = []
    for k in node_lookup.keys():
        if k == vert_idx or k == horz_idx:
            delete_list.append(k)

    new_item_list = []
    for k,v in node_lookup.items():
        new_item_idx = k
        if k != vert_idx and k != horz_idx:
            if k > vert_idx:
                new_item_idx -= 1
            if k > horz_idx:
                new_item_idx -= 1
            if new_item_idx < k:
                new_item_list.append((new_item_idx, node_lookup[k]))
                if k not in delete_list:
                    delete_list.append(k)

    for key in delete_list:
        del node_lookup[key]

    for pair in new_item_list:
        node_lookup[pair[0]] = (pair[1][0], pair[1][1])
    
    if _debug_:
        print("\t" * depth + "reshape graph - end")
        print_graph(graph, depth)
        print_node_lookup_dictionary(node_lookup, depth)
        print()
    return graph
    

def build_tree_from_graph_recursively(graph, tree, distance, vert_idx, horz_idx, max_current_node, node_lookup, depth):
    if _debug_:
        print("\t" * depth + "build tree from graph - start")
        print_graph(graph, depth)
        print_tree(tree, depth)
        print_node_lookup_dictionary(node_lookup, depth)
        print("\t" * depth + "vert_idx={0} horz_idx={1} distance={2} max_current_node={3}".format(str(vert_idx), str(horz_idx), str(distance), str(max_current_node)))
        print()

    if len(graph) < 2:
        raise ValueError("Unexpected graph size < 2.")
    if len(graph) == 2:
        new_tree, new_max_current_node, new_node_lookup = add_new_nodes_to_tree(tree, distance, vert_idx, horz_idx, max_current_node, node_lookup, len(graph) -  1, depth)

        if _debug_:
            print("\t" * depth + "build tree from graph - return")
            print_graph(graph, depth)
            print_tree(tree, depth)
            print_node_lookup_dictionary(node_lookup, depth)
            print()
        
        return tree, node_lookup, graph

    else:
        if depth == 0:
            new_tree = []
            new_graph = graph
            new_distance, new_vert_idx, new_horz_idx = find_smallest_distance(graph)
            new_node_lookup = {}
            new_node_lookup[new_vert_idx] = (0, 1)
            new_node_lookup[new_horz_idx] = (1, 1)
            new_max_current_node = 1
        else:
            new_tree, new_max_current_node, new_node_lookup = add_new_nodes_to_tree(tree, distance, vert_idx, horz_idx, max_current_node, node_lookup, len(graph) - 1, depth)
            new_graph = reshape_graph(graph, vert_idx, horz_idx, new_node_lookup, depth)
            new_distance, new_vert_idx, new_horz_idx = find_smallest_distance(graph)
            if new_vert_idx not in node_lookup:
                new_max_current_node += 1
                node_lookup[new_vert_idx] = (new_max_current_node, 1)
            if new_horz_idx not in node_lookup:
                new_max_current_node += 1
                node_lookup[new_horz_idx] = (new_max_current_node, 1)
        tree, node_lookup, graph = build_tree_from_graph_recursively(new_graph, new_tree, new_distance, new_vert_idx, new_horz_idx, new_max_current_node, new_node_lookup, depth+1)

        if _debug_:
            print("\t" * depth + "build tree from graph - return")
            print_graph(graph, depth)
            print_tree(tree, depth)
            print_node_lookup_dictionary(node_lookup, depth)
            print()
            
        return tree, node_lookup, graph


def build_tree_from_graph(graph):
    tree = []
    node_lookup = {}

    tree, node_lookup, graph = build_tree_from_graph_recursively(graph, tree, -1, -1, -1, 0, node_lookup, 0)

    formatted_tree = format_for_desired_output(tree)
    return formatted_tree

def format_for_desired_output(tree):
    formatted_tree = []
    for node in tree:
        formatted_tree.append((node[0], node[1], node[2], node[3]))
        formatted_tree.append((node[1], node[0], node[2], node[3]))

    formatted_tree.sort(key=lambda node: node[0] * 10000 + node[1])

    return formatted_tree

def find_smallest_distance(graph):
    smallest_i = -1
    smallest_j = -1
    smallest_distance = sys.maxsize
    for i in range(len(graph)-1):
        for j in range(i+1, len(graph)):
            if graph[i][j] < smallest_distance:
                smallest_distance = graph[i][j] 
                smallest_i = i
                smallest_j = j

    return smallest_distance, smallest_i, smallest_j

    
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