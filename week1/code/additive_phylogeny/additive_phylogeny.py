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
        node_ids = []
        while line:
            cleanline = line.rstrip()
            if len(cleanline) > 0:
                if idx == 0:
                    graph_size = int(cleanline)
                else:
                    graph.append([int(n) for n in cleanline.split()])

                idx += 1
                node_ids.append(idx-1)
            line = f.readline()

    if _debug_:
        print(graph_size)
        print(node_ids)
        print_graph(graph)
        print()

    return graph, node_ids, graph_size

def confirm_graph_consistency(graph, graph_name):
    for i in range(len(graph)):
        for j in range(i, len(graph)):
            if i == j: 
                if graph[i][j] != 0:
                    raise ValueError("Graph consistency - {0} - Expected 0 at {0}[{1}][{2}], got {3}".format(graph_name, str(i), str(j), str(graph[i][j])))
            else:
                if graph[i][j] != graph[j][i]:
                    raise ValueError("Graph consistency - {0} - Values must equal {0}[{1}][{2}] and {0}[{2}][{1}], got {3} != {4}".format(graph_name, str(i), str(j), str(graph[i][j]), str(graph[j][i])))

def print_graph(graph, tab_count=0):
    for r in graph:
        print("\t" * tab_count + " ".join([str(n).rjust(6) for n in r]))

def print_tree(tree, tab_count=0):
    for n in tree:
        print("\t"* tab_count + format_tree_node_output(n))

def calc_limb_length(graph, node_id):
    length = sys.maxsize
    graph_size = len(graph)
    if _debug_:
        print("node_id = {0}".format(node_id))
        print_graph(graph)
    for i in range(graph_size-1):
        for j in range(i+1, graph_size):
            if i != node_id and j != node_id:
                cur_val = int((graph[node_id][i] + graph[node_id][j] - graph[i][j]) / 2)
# 280
                if _debug_:
                    print("{0} {1} ({2} + {3} - {4}) / 2 = {5}.".format(str(i), str(j), str(graph[node_id][i]), str(graph[node_id][j]), str(graph[i][j]), str((graph[node_id][i] + graph[node_id][j] - graph[i][j]) / 2)))
                if cur_val < length:
                    length = cur_val    
    if _debug_:
        print(length)
    return length

def build_full_graph_from_graph_and_limb_lengths(graph, limb_lengths):
    full_graph = []
    full_graph_limb_lengths = []
    for i in range(len(graph)):
        full_graph_row = []
        for j in range(len(graph)):
            if j > 1:
                if limb_lengths[j] <= 0:
                    raise ValueError("expected all nodes to have limbs. {1} has limb_length == 0".format(str(j)))
                if j == i:
                    full_graph_row.append(limb_lengths[j]) # this is a weirdness, don't know the math rule for this yet
                else:
                    full_graph_row.append(graph[i][j] - limb_lengths[j])
            full_graph_row.append(graph[i][j])
        if i > 1:
            full_graph_inner_node_row = []
            for k in range(len(full_graph_row)):
                if full_graph_row[k] == 0:
                    full_graph_inner_node_row.append(limb_lengths[i])   # this is a weirdness, don't know the math rule for this yet, it's the column across the diagonal where the [nextrow][col] == 0.
                else:
                    full_graph_inner_node_row.append(full_graph_row[k] - limb_lengths[i])
            full_graph.append(full_graph_inner_node_row)
            full_graph_limb_lengths.append(-1)
        full_graph.append(full_graph_row)
        full_graph_limb_lengths.append(limb_lengths[i])

    return full_graph, full_graph_limb_lengths

def build_tree_from_graph(graph, node_ids):
    confirm_graph_consistency(graph, "graph")
    limb_lengths = []
    for g in range(len(graph)):
        limb_lengths.append(calc_limb_length(graph, g))

    full_graph, full_graph_limb_lengths = build_full_graph_from_graph_and_limb_lengths(graph, limb_lengths)
    confirm_graph_consistency(graph, "full graph")
    
    graph_to_tree_idx = []
    for i in range(len(full_graph)):
        graph_to_tree_idx.append(i)
    tree = build_tree_from_graph_and_limb_lengths(full_graph, full_graph_limb_lengths, node_ids, graph_to_tree_idx, 0)

    new_tree = []
    for n in tree:
        new_tree.append(n)
        new_tree.append((n[1], n[0], n[2]))
    new_tree.sort(key=lambda node: node[0]*100000 + node[1])

    return new_tree

def this_node_is_on_the_path_to_anchor_2(tree, start_node, anchor_2, visited_nodes):
    found_path = False
    for node in tree:
        if not found_path:
            if (node[0] == start_node and node[1] not in visited_nodes) or (node[1] == start_node and node[0] not in visited_nodes):
                start_edge = node[0]
                end_edge = node[1]
                if node[1] == start_node:
                    start_edge = node[1]
                    end_edge = node[0]
                
                if end_edge == anchor_2:
                    found_path = True
                else:
                    new_visited_nodes = []
                    new_visited_nodes.extend(visited_nodes)
                    new_visited_nodes.append(start_edge)
                    found_path = this_node_is_on_the_path_to_anchor_2(tree, end_edge, anchor_2, new_visited_nodes)
    return found_path



def find_root_point_between_anchors(tree, anchor_1, anchor_2, distance_from_anchor_1, visited_nodes, tab_count=0):
    if _debug_:
        print("\t" * tab_count + "finding root point between anchors")
        print_tree(tree, tab_count)
        print(anchor_1)
        print(anchor_2)
        print(distance_from_anchor_1)
        print(visited_nodes)
        print()
    removed_node = None
    for node in tree:
        if node[1] <= node[0]:
            raise ValueError("Malformed edge descriptor {0}->{1}:{2}. Always need [node1] ({0}) to be less than [node2] ({1}).".format(str(node[0]), str(node[1]), str(node[2])))
        if node[2] <= 0:
            raise ValueError("Malformed edge descriptor {0}->{1}:{2}. Always need [weight] ({2}) to be more than 0.".format(str(node[0]), str(node[1]), str(node[2])))
        if (node[0] == anchor_1 and node[1] not in visited_nodes) or (node[1] == anchor_1 and node[0] not in visited_nodes):
            start_edge = node[0]
            end_edge = node[1]
            weight = node[2]
            if node[1] == anchor_1:
                start_edge = node[1]
                end_edge = node[0]

            if end_edge != anchor_2:
                on_the_path_visited_nodes = []
                on_the_path_visited_nodes.extend(visited_nodes)
                on_the_path_visited_nodes.append(start_edge)
                on_the_path_visited_nodes.append(end_edge)
                if not this_node_is_on_the_path_to_anchor_2(tree, end_edge, anchor_2, on_the_path_visited_nodes):
                    if _debug_:
                        print("\t" * tab_count + "skipping edge {0}<->{1}:{2} because destination node ({1}) isn't on the path to anchor_2 {3}.".format(str(start_edge), str(end_edge), str(weight), str(anchor_2)))
                    continue

            if weight == distance_from_anchor_1:
                root_point = end_edge
                max_node_idx = -1
                for n1 in tree:
                    if n1[1] > max_node_idx:
                        max_node_idx = n1[1]
                max_node_idx += 1
                if _debug_:
                    print("\t" * tab_count + "finding root point between anchors - result")
                    print_tree(tree, tab_count)
                    print("\t" * tab_count + "root_point {0}, max_node_idx {1}.".format(str(root_point), str(max_node_idx)))
                    print()
                return True, tree, root_point, max_node_idx
            elif weight < distance_from_anchor_1:
                if end_edge == anchor_2:
                    raise ValueError("Unexpected edge {0}<->{1}:{2}. This search expects the root to be between two anchors. Here we have reached the second anchor ({1}), but the remaining distance ({3}) is greater than the edge weight ({2}).".format(str(start_edge), str(end_edge), str(weight), str(distance_from_anchor_1)))
                new_visited_nodes = []
                new_visited_nodes.extend(visited_nodes)
                new_visited_nodes.append(start_edge)
                success, tree, root_point, max_node_idx = find_root_point_between_anchors(tree, end_edge, anchor_2, distance_from_anchor_1 - weight, new_visited_nodes, tab_count+1)
                if _debug_:
                    print("\t" * tab_count + "finding root point between anchors - result")
                    print_tree(tree, tab_count)
                    print("\t" * tab_count + "success {0}, root_point {1}, max_node_idx {2}.".format(str(success), str(root_point), str(max_node_idx)))
                    print()
                if success:
                    return True, tree, root_point, max_node_idx
            else:
                remove_node = node
                max_node_idx = -1
                for n1 in tree:
                    if n1[1] > max_node_idx:
                        max_node_idx = n1[1]
                max_node_idx += 1
                if start_edge < max_node_idx:
                    tree.append((start_edge, max_node_idx, distance_from_anchor_1))
                else:
                    tree.append((max_node_idx, start_edge, distance_from_anchor_1))
                if end_edge < max_node_idx:
                    tree.append((end_edge, max_node_idx, weight - distance_from_anchor_1))
                else:
                    tree.append((max_node_idx, end_edge, weight - distance_from_anchor_1))
                tree.remove(remove_node)

                if _debug_:
                    print()
                    print_tree(tree)
                    print()

                if _debug_:
                    print("\t" * tab_count + "finding root point between anchors - result")
                    print_tree(tree, tab_count)
                    print("\t" * tab_count + "root_point {0}, max_node_idx {1}.".format(str(max_node_idx), str(max_node_idx + 1)))
                    print()
                return True, tree, max_node_idx, max_node_idx+1

    return False, tree, -1, -1

        
def build_tree_from_graph_and_limb_lengths(full_graph, full_graph_limb_lengths, node_ids, graph_idx_to_tree_node, tab_count = 0):
    if len(full_graph) < 2:
        raise ValueError("graph size {0} < 2".format(str(len(full_graph))))

    if _debug_:
        print("\t" * tab_count + "build tree from graph and limb lengths - start")
        print_graph(full_graph, tab_count)
        print()
        print(full_graph_limb_lengths)
        print()

    tree = []
    if len(full_graph) == 2:
        tree.append((0, 1, full_graph[0][1]))
        # graph_idx_to_tree_node.append(0)
        # graph_idx_to_tree_node.append(1)
        if _debug_:
            print("\t" * tab_count + "build_tree_from_graph_and_limb_lenghts result:")
            print_graph(full_graph)
            print_tree(tree)
            print(graph_idx_to_tree_node)
        return tree

    node_id = len(full_graph) - 2
    limb_length = full_graph_limb_lengths[node_id+1]

    # first, deep-copy graph to (a) a graph with just a stub, no limb, (b) a graph where the whole column is truncated
    full_graph_without_limb = []
    full_graph_without_last_column_and_row = []
    for i in range(len(full_graph) - 1): # don't want last row, also sometimes don't want 2nd-to-last row
        row_without_limb = []
        row_without_last_column = []
        for j in range(len(full_graph) - 1):
            row_without_limb.append(full_graph[i][j])
            if j != len(full_graph) - 2:
                row_without_last_column.append(full_graph[i][j])

        full_graph_without_limb.append(row_without_limb)
        if i != len(full_graph) - 2:
            full_graph_without_last_column_and_row.append(row_without_last_column)

    new_tree = build_tree_from_graph_and_limb_lengths(full_graph_without_last_column_and_row, full_graph_limb_lengths, node_ids[0:len(node_ids)-1], graph_idx_to_tree_node, tab_count+1)

    if (_debug_):
        print("\t" * tab_count + "finding node anchor point")
        print("\t" * tab_count + "full_graph_without_limb")
        print_graph(full_graph_without_limb, tab_count)
        print()
        print("\t" * tab_count + "full_graph_without_last_column_and_row")
        print_graph(full_graph_without_last_column_and_row, tab_count)
        print()
        print("\t" * tab_count + "graph idx to tree node idx mapping")
        print(graph_idx_to_tree_node)
        print()
        print(node_id)
        print()

    found_anchor_leaves = False
    anchor_1 = -1
    anchor_2 = -1
    distance_from_anchor_1 = -1
    inner_edge_branch_len = -1

# 280 - there were breaks

    if _debug_ and limb_length == 280:
        print("looking for an exact match")
    for i in range(len(full_graph_without_limb) - 2):
        for j in range(len(full_graph_without_limb) - 2, i, -1):
#        for j in range(i+1, len(full_graph_without_limb) - 1)   :
            if _debug_: #280
                print("i={0} j={1} node_id={2} {3} == {4} + {5} ? {6}.".format(str(i), str(j), str(node_id), str(full_graph_without_limb[i][j]), str(full_graph_without_limb[i][node_id]), str(full_graph_without_limb[j][node_id]), str(full_graph_without_limb[i][j] == full_graph_without_limb[i][node_id] + full_graph_without_limb[j][node_id])))
            if full_graph_without_limb[i][j] == full_graph_without_limb[i][node_id] + full_graph_without_limb[j][node_id]:
# 280 unnecessary if breaks are in place
                if not found_anchor_leaves:
                    anchor_1 = graph_idx_to_tree_node[i]
                    anchor_2 = graph_idx_to_tree_node[j]
                    distance_from_anchor_1 = full_graph_without_limb[i][node_id]
                    found_anchor_leaves = True
#280
#                break
        
#280
        # if found_anchor_leaves:
        #     break
    
    if _debug_:
        if found_anchor_leaves:
            print("success! {0} {1} {2}".format(str(anchor_1), str(anchor_2), str(distance_from_anchor_1)))
        else:
            print("no match")
    
    if anchor_1 < 0:
        min_inner_branch = sys.maxsize
        for i in range(len(full_graph_without_limb) - 2):
            for j in range(i+1, len(full_graph_without_limb) - 1):
                #280
                if _debug_:
                    print("{0} {1} min_inner_branch = {2} (Dij + Dkj - Dik) / 2 <? min_inner_branch -> ({3} + {4} - {5}) / 2 [{6}] <? {7}".format(str(i), str(j), str(min_inner_branch), str(full_graph_without_limb[i][node_id]), str(full_graph_without_limb[j][node_id]), str(full_graph_without_limb[i][j]), str(int((full_graph_without_limb[i][node_id] + full_graph_without_limb[j][node_id] - full_graph_without_limb[i][j])/2)), str(min_inner_branch)))
                if ( full_graph_without_limb[i][node_id] + full_graph_without_limb[j][node_id] - full_graph_without_limb[i][j] ) % 2 == 0 and \
                   (( full_graph_without_limb[i][node_id] + full_graph_without_limb[j][node_id] - full_graph_without_limb[i][j] ) / 2) < min_inner_branch:
                    min_inner_branch = int(( full_graph_without_limb[i][node_id] + full_graph_without_limb[j][node_id] - full_graph_without_limb[i][j]) / 2)
                    anchor_1 = graph_idx_to_tree_node[i]
                    anchor_2 = graph_idx_to_tree_node[j]
                    distance_from_anchor_1 = full_graph_without_limb[i][node_id] - min_inner_branch
        inner_edge_branch_len = min_inner_branch
    
    if anchor_2 <= anchor_1:
        raise ValueError("anchor_1 {0} is expected to be less than anchor_2 {1}".format(str(anchor_1), str(anchor_2)))
    if _debug_:
        print("\t" * tab_count + "data to find stump root point")
        print("\t" * tab_count + "anchor_1 = {0} anchor_2 = {1} distance_from_anchor_1 = {2} inner_edge_branch_len = {3} limb_length = {4}.".format(str(anchor_1), str(anchor_2), str(distance_from_anchor_1), str(inner_edge_branch_len), str(limb_length)))
    
    if _debug_:
        print("\t" * tab_count + "about to find a stump root point")
        print_graph(full_graph, tab_count)
        print()
        print_graph(full_graph_without_limb, tab_count)
        print()
        print_graph(full_graph_without_last_column_and_row, tab_count)
        print_tree(new_tree, tab_count)
        print("\t" * tab_count + "anchor_1 = {0} anchor_2 = {1} distance_from_anchor_1 = {2} inner_edge_branch_len = {3} limb_length = {4}.".format(str(anchor_1), str(anchor_2), str(distance_from_anchor_1), str(inner_edge_branch_len), str(limb_length)))
        print()

    search_success, n_tree, stump_root_id, limb_end_id = find_root_point_between_anchors(new_tree, anchor_1, anchor_2, distance_from_anchor_1, [], tab_count + 1)


    if _debug_:
        print("\t" * tab_count + "build_tree_from_graph_and_limb_lenghts before stump limb addition:")
        print_graph(full_graph, tab_count)
        print_tree(new_tree, tab_count)
        print(stump_root_id)
        print(limb_end_id)
        print()

    new_tree = n_tree
    limb_start = stump_root_id
    limb_end = limb_end_id
    if inner_edge_branch_len > -1:
        new_tree.append((stump_root_id, limb_end, inner_edge_branch_len))
        limb_start = limb_end_id
        graph_idx_to_tree_node[node_id] = limb_end
        limb_end = limb_end + 1
    else:
        graph_idx_to_tree_node[node_id] = limb_start

    if limb_length > 0:
        new_tree.append((limb_start, limb_end, limb_length))
        graph_idx_to_tree_node[node_id+1] = limb_end
    
    if _debug_:
        print("\t" * tab_count + "build_tree_from_graph_and_limb_lenghts result:")
        print_graph(full_graph, tab_count)
        print_tree(new_tree, tab_count)
        print("\t" * tab_count + "graph to tree idx mapping:")
        print(graph_idx_to_tree_node)
        print()

    return new_tree

def format_tree_node_output(node):
    return format_tree_node_elements_output(node[0], node[1], node[2])

def format_tree_node_elements_output(from_node, to_node, weight):
    return "{0}->{1}:{2}".format(str(from_node), str(to_node), str(weight))

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
    
    graph, node_ids, graph_size = organize_inputs(sys.argv[1])

    if graph_size < 1:
        raise ValueError("output_size incorrect value {0}".format(str(graph_size)))


    results = build_tree_from_graph(graph, node_ids)

    for r in results:
        print(format_tree_node_output(r))

    end = time.process_time()
    print("Time: {0}".format(end-start))