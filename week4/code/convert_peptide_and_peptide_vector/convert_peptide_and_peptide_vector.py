#! /usr/bin/python3

import sys
import time
import math

_verbose_ = False
_timed_output_ = False
_debug_ = False

_amino_acid_by_mass_ = {4:"X", 5:"Z", 57:"G", 71:"A", 87:"S", 97:"P", 99:"V", 101:"T", 103:"C", 113:"L", 114:"N", 115:"D", 128:"Q", 129:"E", 131:"M", 137:"H", 147:"F", 156:"R", 163:"Y", 186:"W"}
_mass_by_amino_acid_ = {"X":4, "Z":5, "G":57, "A":71, "S":87, "P":97, "V":99, "T":101, "C":103, "L":113, "N":114, "D":115, "Q":128, "E":129, "M":131, "H":137, "F":147, "R":156, "Y":163, "W":186, "I":113, "K":128}
# _amino_acid_by_mass_ = {4:"X", 5:"Z"}
# _mass_by_amino_acid_ = {"X":4, "Z":5}

def organize_inputs(input_file, peptide_to_vector):

    with open(input_file) as f:
        if peptide_to_vector:
            in_val = f.readline().rstrip()
        else:
            in_val = [int(s) for s in f.readline().rstrip().split()]

    if _debug_:
        print_code_type(peptide_to_vector)
        print(in_val)
        print()

    return in_val

def print_code_type(peptide_to_vector):
    outstr = "peptide to vector" if peptide_to_vector else "vector to peptide"
    print(outstr)

def convert_peptide_to_peptide_vector(peptide):
    vect = []
    for ch in peptide:
        for i in range(_mass_by_amino_acid_[ch] - 1):
            vect.append(0)
        vect.append(1)
    return vect

def convert_peptide_vector_to_peptide(peptide_vector):
    pep = ""
    weight_ct = 0
    for i in peptide_vector:
        if i == 0:
            weight_ct += 1
        if i == 1:
            weight_ct += 1
            if weight_ct in _amino_acid_by_mass_:
                pep += _amino_acid_by_mass_[weight_ct]
                weight_ct = 0
            else:
                raise ValueError("Unexpected weight {0} not found in _amino_acid_by_mass_".format(str(weight_ct)))
    
    if weight_ct > 0:
        raise ValueError("Unexpected exited loop and found weight_ct {0} != 0".format(str(weight_ct)))
    
    return pep

if __name__ == '__main__':
    start = time.process_time()

    if len(sys.argv) < 2:
        print("Expected input:\n[str: filename path]\n\nfile contents:\n[int: graph size]\n[string: one row of graph [1...n]]\n")

    peptide_to_vector = True
    for a_idx in  range(2,3,1):
        if len(sys.argv) > a_idx:
            if sys.argv[a_idx] == "-vp":
                peptide_to_vector = False
            if sys.argv[a_idx] == "-v":
                _verbose_ = True
            if sys.argv[a_idx] == "-vv":
                _verbose_ = True
                _timed_output_ = True
            if sys.argv[a_idx] == "-vvv":
                _verbose_ = True
                _timed_output_ = True
                _debug_ = True
    
    in_val = organize_inputs(sys.argv[1], peptide_to_vector)

    if peptide_to_vector:
        out_val = convert_peptide_to_peptide_vector(in_val)
        print(" ".join([str(i) for i in out_val]))
    else:
        out_val = convert_peptide_vector_to_peptide(in_val)
        print(out_val)

    end = time.process_time()
    print("Time: {0}".format(end-start))