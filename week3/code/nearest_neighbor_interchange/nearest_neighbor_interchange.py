#! /usr/bin/python3

import sys
import time
import math

_verbose_ = False
_timed_output_ = False
_debug_ = False

_all_symbols_ = ['A','C','G','T']

class SPNode:
    def __init__(self, name, child=None, symbol=""):
        self.name = name
        self.children = []
        if child is not None:
            self.children.append(child)
        self.symbol = symbol
        self.isLeaf = len(self.symbol) > 0
        self.value_per_symbol = {}
        if self.isLeaf:
            self.value_per_symbol[self.symbol] = 0
        self.best_node_symbol_to_reach_target_symbol = {}
    
    def add_child(self, child):
        if child not in self.children:
            self.children.append(child)
        else:
            raise ValueError("Unexpected added child twice. " + str(child))
    
    def reset_node_calculations(self):
        if not self.isLeaf:
            self.symbol = ""
        self.value_per_symbol = {}
        if self.isLeaf:
            self.value_per_symbol[self.symbol] = 0
        self.best_node_symbol_to_reach_target_symbol = {}
    
    def to_str(self):
        useful_info = ""
        if len(self.symbol) > 0:
            useful_info += " symbol=" + self.symbol
        
        if len(self.value_per_symbol) > 0:
            useful_info += " values=[" + ", ".join([k + ":" + str(v) for k, v in self.value_per_symbol.items()]) + "]"
        
        if len(self.best_node_symbol_to_reach_target_symbol) > 0:
            useful_info += " nstrts=[" + ", ".join([k + ":" + v for k, v in self.best_node_symbol_to_reach_target_symbol.items()]) + "]"
        return "{0} {1}".format(self.name, useful_info)

def print_tree(node):
    print("print_tree")
    print_tree_recursive(node, 0)
    print()


def print_tree_recursive(node, indent):
    print("\t" * indent + node.to_str())
    for child in node.children:
        print("\t" * indent + node.to_str() + "->" + child.to_str())
    
    for child in node.children:
        print_tree_recursive(child, indent+1)

def print_tree_structure(node):
    print("print_tree_structure")
    print_tree_structure_recursive(node, 0)
    print()


def print_tree_structure_recursive(node, indent):
    print("\t" * indent + node.name)
    for child in node.children:
        print("\t" * indent + node.name + "->" + child.name)
    
    for child in node.children:
        print_tree_structure_recursive(child, indent+1)

def reset_new_tree_internal_calculations(root):
    if _debug_:
        print("reset new tree internal - start")
        print_tree(root)

    root.reset_node_calculations()
    children_to_process = root.children
    while len(children_to_process) > 0:
        new_children_to_process = []
        for child in children_to_process:
            child.reset_node_calculations()
            new_children_to_process += child.children
        children_to_process = new_children_to_process
    
    if _debug_:
        print("reset new tree internal - end")
        print_tree(root)
        

def organize_inputs(input_file):

    max_node_id = 0
    leaf_count = 0
    proto_edges = {}
    cn1 = cn2 = None
    with open(input_file) as f:
        leaf_count = int(f.readline().rstrip())

        line = f.readline()
        while line:
            edge = line.rstrip().lstrip().split("->")

            if edge[0] not in proto_edges:
                proto_edges[edge[0]] = [edge[1]]
            else:
                proto_edges[edge[0]].append(edge[1])
            
            if edge[0].isdigit():
                if len(proto_edges[edge[0]]) > 3:
                    raise ValueError("Inner node {0} has more than 3 neighbors: [{1}]".format(edge[0], ",".join(proto_edges[edge[0]])))
            else:
                if len(proto_edges[edge[0]]) > 1:
                    raise ValueError("Leaf node {0} has more than 1 neighbor: [{1}]".format(edge[0], ",".join(proto_edges[edge[0]])))

            if edge[0].isdigit() and int(edge[0]) > max_node_id:
                max_node_id = int(edge[0])
            if edge[1].isdigit() and int(edge[1]) > max_node_id:
                max_node_id = int(edge[1])
            
            if not edge[0].isdigit():
                leaf_length = len(edge[0])
            
            if cn1 is None:
                cn1 = edge[0]
                cn2 = edge[1]
                if _debug_:
                    print("break edge - " + cn1 + "->" + cn2)

            line = f.readline()
    
    if _debug_:
        print(proto_edges)

    max_node_id = max_node_id + 1

    root = SPNode(str(max_node_id))

    child_nodes = [cn1, cn2]
    broken_edge_nodes = []
    for n in proto_edges[cn1]:
        if n != cn2:
            broken_edge_nodes.append(n)
    proto_edges[cn1] = broken_edge_nodes
    broken_edge_nodes = []
    for n in proto_edges[cn2]:
        if n != cn1:
            broken_edge_nodes.append(n)
    proto_edges[cn2] = broken_edge_nodes

    orig_root = build_tree(root, child_nodes, proto_edges)
    if len(orig_root.children) != 2:
        raise ValueError("Expected 2 children for root. root children count = {0}. {1}".format(str(len(orig_root.children)), ";".join(orig_root.children)))

    if _debug_:
        print("organize inputs check")
        print_tree(orig_root)
        print()

    # create a bunch of parallel trees for different indices
    orig_root.name = str(orig_root.name + ":0")
    roots = build_out_roots_collection_from_orig_root(orig_root)

    return roots

def build_out_roots_collection_from_orig_root(orig_root):
    roots = []
    root_name_root = orig_root.name.split(":")[0]
    roots.append(orig_root)

    leaf_length = 0
    children_to_search = orig_root.children
    while len(children_to_search) > 0 and leaf_length == 0:
        new_children_to_search = []
        for child in children_to_search:
            if child.isLeaf:
                leaf_length = len(child.name)
                new_children_to_search = []
                break
            else:
                new_children_to_search += child.children
        children_to_search = new_children_to_search


    if _debug_:
        print(orig_root.name)
        print(root_name_root)
        print(leaf_length)
        print()

    for i in range(1, leaf_length):
        new_root = SPNode(root_name_root + ":" + str(i))
        copy_tree(orig_root, new_root, i)
        roots.append(new_root)
    
    if _debug_:
        for root_node in roots:
            print_tree(root_node)
        print()

    return roots

def build_tree(node, child_nodes, proto_edges):

    for child in child_nodes:
        if child.isdigit():
            new_child_nodes = [] 
            for ccnode in proto_edges[child]:
                if ccnode != node.name:
                    new_child_nodes.append(ccnode)            
            cnode = build_tree(SPNode(child), new_child_nodes, proto_edges)
        else:
            cnode = SPNode(child, child=None, symbol=child[0])
        node.add_child(cnode)

    return node

def copy_tree(orig_root, new_root, leaf_index):
    for child in orig_root.children:
        if child.isLeaf:
            new_child = SPNode(child.name, None, child.name[leaf_index])
            new_root.add_child(new_child)
        else:
            new_child = SPNode(child.name)
            new_root.add_child(new_child)
            copy_tree(child, new_child, leaf_index)

    return



def calc_one_symbol_hamming_distance(symbol1, symbol2):
    return 0 if symbol1 == symbol2 else 1

def calc_two_string_hamming_distance(str1, str2):
    if len(str1) != len(str2):
        raise ValueError("Must have same-length strings for comparisson. String lengths are {0} and {1} for strings {2} and {3}".format(str(len(str1)), str(len(str2)), str1, str2))

    distance = 0
    for i in range(len(str1)):
        distance += 0 if str1[i] == str2[i] else 1
    
    return distance

def score_node(node, node_target_symbol, indent):
    if _debug_:
        print("\t" * indent + node.name + " target=" + node_target_symbol)
    if len(node.children) == 0:
        if _debug_:
            print("\t" * indent + "node.symbol=" + node.symbol + " node_target_symbol=" + node_target_symbol)
        return 0 if node.symbol == node_target_symbol else sys.maxsize

    if len(node.value_per_symbol) > 0 and node_target_symbol in node.value_per_symbol:
        return node.value_per_symbol[node_target_symbol]

    min_val = 0
    for child in node.children:
        min_val_for_target_symbol_for_child = sys.maxsize
        if child.best_node_symbol_to_reach_target_symbol is None:
            child.best_node_symbol_to_reach_target_symbol = {}
        for n_target_symbol in _all_symbols_:
            s = score_node(child, n_target_symbol, indent+1) + calc_one_symbol_hamming_distance(n_target_symbol, node_target_symbol)
            if s < min_val_for_target_symbol_for_child:
                min_val_for_target_symbol_for_child = s
                child.best_node_symbol_to_reach_target_symbol[node_target_symbol] = n_target_symbol
        min_val += min_val_for_target_symbol_for_child
    
    if node.value_per_symbol is None:
        node.value_per_symbol = {}
    node.value_per_symbol[node_target_symbol] = min_val
    
    if _debug_:
        print("\t" * indent + "min_val for " + node_target_symbol + "=" + str(min_val))
        print("\t" * indent + "[" + " ".join([k + ":" + str(v) for k,v in node.value_per_symbol.items()]) + "]")
        print("\t" * indent + "[" + " ".join([k + ":" + str(v) for k,v in node.best_node_symbol_to_reach_target_symbol.items()]) + "]")

    return node.value_per_symbol[node_target_symbol]

def score_trees(roots):
    for root in roots:
        min_val = sys.maxsize
        sym = ""
        for target_symbol in _all_symbols_:
            val = score_node(root, target_symbol, 0)
            if val < min_val:
                min_val = val
                sym = target_symbol
        root.symbol = sym

    if _debug_:
        print("after score_trees")
        for root in roots:
            print_tree(root)

def choose_best_node_values(roots):
    for root in roots:
        if root.symbol is None:
            raise ValueError("Expected root " + root.name + " to have a symbol.")

        for child in root.children:
            choose_best_node_values_recursive(child, root.symbol, 1)

    if _debug_:
        print("after choose_best_node_values")
        for root in roots:
            print_tree(root)
            

def choose_best_node_values_recursive(node, target_symbol, indent):
    if _debug_:
        print("\t" * indent + "cbns start n=" + node.name + " target=" + target_symbol)
    if node.symbol is None or len(node.symbol) == 0:
        if node.best_node_symbol_to_reach_target_symbol is None:
            raise ValueError("Expected field best_node_symbol_to_reach_target_symbol to be populated. Node=" + node.name)
        if target_symbol not in node.best_node_symbol_to_reach_target_symbol:
            raise ValueError("Expected field best_node_symbol_to_reach_target_symbol to have key. Node=" + node.name + ", key=" + target_symbol)
        node.symbol = node.best_node_symbol_to_reach_target_symbol[target_symbol]
        for child in node.children:
            choose_best_node_values_recursive(child, node.symbol, indent+1)
    if _debug_:
        print("\t" * indent + "cbns end  n=" + node.name + " target=" + target_symbol + " symbol=" + node.symbol)

def format_tree_node_output(result_root):
    output = ""
    output += str(result_root.value_per_symbol[result_root.symbol]) + "\n"
    if _debug_:
        print(output)
    
    edges_to_traverse = []
    # for child in result_root.children:
    #     edges_to_traverse.append((result_root, child))
    edges_to_traverse.append((result_root.children[0], result_root.children[1]))
    while len(edges_to_traverse) > 0:
        new_edges_to_traverse = []

        for edge in edges_to_traverse:
            str_hamming_distance = str(calc_two_string_hamming_distance(edge[0].symbol, edge[1].symbol))
            output += "{0}->{1}:{2}\n".format(edge[0].symbol, edge[1].symbol, str_hamming_distance)
            output += "{1}->{0}:{2}\n".format(edge[0].symbol, edge[1].symbol, str_hamming_distance)
            for child in edge[1].children:
                new_edges_to_traverse.append((edge[1], child))

        if _debug_:
            print(output)
        edges_to_traverse = new_edges_to_traverse

    return output

def assemble_scores(parallel_nodes):
    node_str = ""
    node_val = 0
    for node in parallel_nodes:
        # if _debug_:
        #     print(node.name)
        #     print(node.symbol)
        #     print(node.value_per_symbol)
        node_str += node.symbol
        node_val += node.value_per_symbol[node.symbol]
    
    new_node = SPNode(parallel_nodes[0].name, None, node_str)
    new_node.value_per_symbol[node_str] = node_val

    if not parallel_nodes[0].isLeaf:
        c_count = len(parallel_nodes[0].children)
        for node in parallel_nodes:
            if len(node.children) != c_count:
                raise ValueError("Unexpected child count for node: " + node.name + ". Expected=" + str(c_count) + " found=" + len(node.children) + ".")
        
        child_node_sets = []
        for i in range(c_count):
            child_node_set = []
            for node in parallel_nodes:
                child_node_set.append(node.children[i])
            child_node_sets.append(child_node_set)

        for c_n_s in child_node_sets:
            child_node = assemble_scores(c_n_s)
            new_node.children.append(child_node)
        
    return new_node

def calc_hamming_distance(roots):
    score_trees(roots)
    choose_best_node_values(roots)
    result_tree = assemble_scores(roots)

    if _debug_:
        print(result_tree)
        print_tree(result_tree)
    return result_tree

def list_tree_edge_pairs(root):
    if _debug_:
        print("list tree edge pairs")
        print_tree_structure(root)

    edge_pairs = []
    for child in root.children:
        edge_pairs += list_tree_edge_pairs_recursive(child, root.name)

    if _debug_:
        print("edge_pairs")
        print(edge_pairs)
    return edge_pairs

def list_tree_edge_pairs_recursive(node, root_name):
    edge_pairs = []
    for child in node.children:
        if child.isLeaf:
            continue
        if node.name != root_name:
            edge_pairs.append((node.name, child.name))
        edge_pairs += list_tree_edge_pairs_recursive(child, root_name)
    return edge_pairs

def edge_pairs_swap(root, edge_pair, swap_iteration):
    new_tree = SPNode(root.name)
    copy_tree(root, new_tree, 0)
    if _debug_:
        print("edge pair")
        print(edge_pair)
        print("here, trees should be same")
        print("old tree")
        print_tree_structure(root)
        print("new tree")
        print_tree_structure(new_tree)

    children_to_search = new_tree.children
    simple_swap_focus_nodes = []
    while len(children_to_search) > 0:
        new_children_to_search = []
        for child in children_to_search:
            if child.name == edge_pair[0]:
                simple_swap_focus_nodes.append(child)
                for nc in child.children:
                    if nc.name == edge_pair[1]:
                        simple_swap_focus_nodes.append(nc)
                new_children_to_search = []
                break
            else:
                if child.isLeaf:
                    continue
                else:
                    new_children_to_search += child.children
        children_to_search = new_children_to_search

    swap_focus_nodes = []
    for child in new_tree.children:
        if child.name == simple_swap_focus_nodes[0].name:
            swap_focus_nodes.append(new_tree)
            swap_focus_nodes.append(simple_swap_focus_nodes[0])
            swap_focus_nodes.append(simple_swap_focus_nodes[1])

    children_to_search = new_tree.children
    while len(children_to_search) > 0 and len(swap_focus_nodes) < len(simple_swap_focus_nodes):
        new_children_to_search = []
        for child in children_to_search:
            if not child.isLeaf:
                for gchild in child.children:
                    if gchild.name == simple_swap_focus_nodes[0].name:
                        swap_focus_nodes.append(child)
                        swap_focus_nodes.append(simple_swap_focus_nodes[0])
                        swap_focus_nodes.append(simple_swap_focus_nodes[1])
                new_children_to_search += child.children
        children_to_search = new_children_to_search


    gchild = swap_focus_nodes[2].children[0]
    if swap_iteration == 0:
        for sibling in swap_focus_nodes[1].children:
            if sibling.name != swap_focus_nodes[2].name:
                del swap_focus_nodes[2].children[0]
                swap_focus_nodes[1].children.append(gchild)
                del swap_focus_nodes[1].children[swap_focus_nodes[1].children.index(sibling)]
                swap_focus_nodes[2].children.append(sibling)
                break
        return new_tree
    else:
        swap_focus_nodes[0].children.append(swap_focus_nodes[2])
        swap_focus_nodes[2].children.append(swap_focus_nodes[1])
        del swap_focus_nodes[0].children[swap_focus_nodes[0].children.index(swap_focus_nodes[1])]
        del swap_focus_nodes[1].children[swap_focus_nodes[1].children.index(swap_focus_nodes[2])]
        swap_focus_nodes[1].children.append(gchild)
        del swap_focus_nodes[2].children[0]
        return new_tree

    
def iterated_nearest_neighbors_to_find_best_tree(roots):
    score_trees(roots)
    choose_best_node_values(roots)
    result_tree = assemble_scores(roots)
    previous_best_value = result_tree.value_per_symbol[result_tree.symbol]
    previous_best_tree = result_tree
    previous_best_roots = roots
    current_best_value = sys.maxsize
    current_best_tree = None
    current_best_roots = None

    if _verbose_:
        print("prev best value = {0} cur best value = {1} ".format(str(previous_best_value), str(current_best_value)))


    if _debug_:
        print_tree_structure(roots[0])

    possibility_of_better_score = True
    skip_first_tree = True
    while possibility_of_better_score:
        edge_pairs = list_tree_edge_pairs(previous_best_roots[0])
        for edge_pair in edge_pairs:
            for swap_event in [0, 1]:
                new_tree = edge_pairs_swap(previous_best_roots[0], edge_pair, swap_event)
                reset_new_tree_internal_calculations(new_tree)
                new_roots = build_out_roots_collection_from_orig_root(new_tree)
                score_trees(new_roots)
                choose_best_node_values(new_roots)
                new_result_tree = assemble_scores(new_roots)

                if new_result_tree.value_per_symbol[new_result_tree.symbol] < current_best_value:
                    current_best_value = new_result_tree.value_per_symbol[new_result_tree.symbol]
                    current_best_tree = new_result_tree
                    current_best_roots = new_roots

        if current_best_value < previous_best_value:
            if _verbose_:
                print("prev best value = {0} cur best value = {1} ".format(str(previous_best_value), str(current_best_value)))

            if skip_first_tree:
                skip_first_tree = False
            else:
                print(format_tree_node_output(previous_best_tree))

            previous_best_value = current_best_value
            previous_best_tree = current_best_tree
            previous_best_roots = current_best_roots
        else:
            possibility_of_better_score = False
    
    if _verbose_:
        print("prev best value = {0} cur best value = {1} ".format(str(previous_best_value), str(current_best_value)))

    print(format_tree_node_output(current_best_tree))
    print()




        # new_tree = edge_pairs_swap(roots[0], edge_pair, 0)
        # print("new tree changed")
        # print_tree_structure(new_tree)
        # new_tree = edge_pairs_swap(roots[0], edge_pair, 1)
        # print("new tree changed")
        # print_tree_structure(new_tree)
        

    return result_tree


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
    
    roots = organize_inputs(sys.argv[1])

    if len(roots) < 1:
        raise ValueError("output_size incorrect value {0}".format(str(len(roots))))


    results = iterated_nearest_neighbors_to_find_best_tree(roots)
    # results = calc_hamming_distance(roots)

    # print(format_tree_node_output(results))

    end = time.process_time()
    print("Time: {0}".format(end-start))