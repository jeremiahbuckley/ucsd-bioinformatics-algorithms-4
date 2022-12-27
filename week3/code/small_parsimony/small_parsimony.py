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
    print("\t" * indent + str(node))
    print("\t" * indent + node.to_str())
    for child in node.children:
        print("\t" * indent + str(child))
        print("\t" * indent + node.to_str() + "->" + child.to_str())
    
    for child in node.children:
        print_tree_recursive(child, indent+1)




def organize_inputs(input_file):
    graph_size = -1

    init_roots = {}
    leafs_found = 0
    leaf_length = 0
    with open(input_file) as f:
        leaf_count = int(f.readline().rstrip())

        line = f.readline()

        while line:
            edge = line.rstrip().lstrip().split("->")
            
            node0 = node1 = None
            rname0 = edge[0]
            if rname0 in init_roots:
                node0 = init_roots[rname0]
            else:
                node0 = SPNode(rname0)
                init_roots[rname0] = node0

            if edge[1].isdigit():
                rname1 = edge[1]
                if rname1 in init_roots:
                    node1 = init_roots[rname1]
                    node0.add_child(node1)
                    del init_roots[rname1]
                else:
                    node1 = SPNode(rname1)
                    node0.add_child(node1)
                    print_tree(node0)
            else:
                leaf_length = len(edge[1])
                node1 = SPNode(edge[1], child=None, symbol=edge[1][0])
                node0.add_child(node1)
                leafs_found += 1

            line = f.readline()

        if leaf_count != leafs_found:
            raise ValueError("Leafs found ({0}) does not equal expected leaf count ({1})".format(str(leafs_found), str(leaf_count)))
        
        if len(init_roots) != 1:
            raise ValueError("Expected 1 root at this juncture. Got " + str(len(init_roots)))

    if _debug_:
        for root_node in init_roots.values():
            print_tree(root_node)
        print()

    # create a bunch of parallel trees for different indices
    orig_root = None
    for r in init_roots.values():
        orig_root = r
    root_name_root = orig_root.name
    orig_root.name = str(orig_root.name + ":0")
    roots = []
    roots.append(orig_root)

    for i in range(1, leaf_length):
        new_root = SPNode(root_name_root + ":" + str(i))
        copy_tree(orig_root, new_root, i)
        roots.append(new_root)
    
    if _debug_:
        for root_node in roots:
            print_tree(root_node)
        print()

    return roots

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
    output += str(result_root.children[0].value_per_symbol[result_root.children[0].symbol]) + "\n"
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


def print_tree_recursive(node, indent):
    print("\t" * indent + str(node))
    print("\t" * indent + node.to_str())
    for child in node.children:
        print("\t" * indent + str(child))
        print("\t" * indent + node.to_str() + "->" + child.to_str())
    
    for child in node.children:
        print_tree_recursive(child, indent+1)


def calc_hamming_distance(roots):
    score_trees(roots)
    choose_best_node_values(roots)
    result_tree = assemble_scores(roots)

    if _debug_:
        print(result_tree)
        print_tree(result_tree)
    return result_tree

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


    results = calc_hamming_distance(roots)

    print(format_tree_node_output(results))

    end = time.process_time()
    print("Time: {0}".format(end-start))