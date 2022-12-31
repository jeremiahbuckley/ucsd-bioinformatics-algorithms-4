#! /usr/bin/python3

import sys
import time
import math

_verbose_ = False
_timed_output_ = False
_debug_ = False

_amino_acid_by_mass_ = {57:"G", 71:"A", 87:"S", 97:"P", 99:"V", 101:"T", 103:"C", 113:"L", 114:"N", 115:"D", 128:"Q", 129:"E", 131:"M", 137:"H", 147:"F", 156:"R", 163:"Y", 186:"W"}
_mass_by_amino_acid_ = {"G":57, "A":71, "S":87, "P":97, "V":99, "T":101, "C":103, "L":113, "N":114, "D":115, "Q":128, "E":129, "M":131, "H":137, "F":147, "R":156, "Y":163, "W":186, "I":113, "K":128}

_fake_amino_acid_by_mass_ = {4:"X", 5:"Z"}
_fake_mass_by_amino_acid_ = {"X":4, "Z":5}

def organize_inputs(input_file):

    with open(input_file) as f:
        weights = [int(s) for s in f.readline().rstrip().split()]

    if _debug_:
        print(weights)
        print()

    return weights

def generate_peptide_vector_candidates(remaining_mass, aa_by_mass, min_possible_mass, found_vectors_by_weight, indent):
    if _debug_:
        print("\t" * indent + "rm=" + str(remaining_mass))
        print(found_vectors_by_weight)
        print()
    
    if remaining_mass < min_possible_mass:
        return []

    candidates = []

    for k in aa_by_mass.keys():
        klist = [0] * (k-1)
        klist.append(1)
        if k < remaining_mass:
            if remaining_mass - k in found_vectors_by_weight:
                cs = found_vectors_by_weight[remaining_mass - k][:]
            else:
                cs = generate_peptide_vector_candidates(remaining_mass - k, aa_by_mass, min_possible_mass, found_vectors_by_weight, indent+1)
            for c in cs:
                candidates.append(klist+c)
        elif k == remaining_mass:
            candidates.append(klist)

    found_vectors_by_weight[remaining_mass] = candidates[:]
    
    if _debug_:
        print("\t" * indent + "rm=" + str(remaining_mass))
        print(found_vectors_by_weight)
        print(candidates)
        print()

    return candidates

def generate_peptide_vector_candidates_su1(remaining_mass, aa_by_mass, min_possible_mass, found_vectors_by_weight, indent):
    if _debug_:
        print("\t" * indent + "s rm=" + str(remaining_mass))
        print(found_vectors_by_weight)
        print()
    
    if remaining_mass < min_possible_mass:
        return []

    candidates = []

    for k in aa_by_mass.keys():
        if k < remaining_mass:
            if remaining_mass - k in found_vectors_by_weight:
                cs = found_vectors_by_weight[remaining_mass - k][:]
            else:
                cs = generate_peptide_vector_candidates_su1(remaining_mass - k, aa_by_mass, min_possible_mass, found_vectors_by_weight, indent+1)
                # print("from nested call")
                # print(cs)
            for c in cs:
                new_list = [k]
                new_list += c[:]
                candidates.append(new_list)
        elif k == remaining_mass:
            candidates.append([k])

    found_vectors_by_weight[remaining_mass] = candidates[:]
    
    if _debug_:
        print("\t" * indent + "e rm=" + str(remaining_mass))
        print(found_vectors_by_weight)
        print(candidates)
        print()

    return candidates

def convert_su1_pvcs_into_orig_pvcs(candidates_su1):
    if _debug_:
        print(candidates_su1)

    candidates = []
    for c in candidates_su1:
        c_su1 = []
        for k in c:
        # klist = [0] * (k-1)
        # klist.append(1)
            new_list = [0] * (k-1)
            new_list.append(1)
            c_su1 += new_list[:]
        candidates.append(c_su1)

    if _debug_:
        print("convert su1 pvcs into orig pvcs")
        print(candidates_su1)
        print(candidates)
    return candidates

def find_peptide_with_best_weighting(peptide_vector_candidates, amplitudes, aa_by_mass):
    if _debug_:
        print("find peptide with best weighting start")
        print(amplitudes)
        print(peptide_vector_candidates)
        print(aa_by_mass)
        print()

    max_weighting = 0
    max_weight_pvc = None
    for pvc in peptide_vector_candidates:
        if len(pvc) != len(amplitudes):
            raise ValueError("Unexpected difference. pvc length {0} should equal amplitudes length {1}.".format(str(len(pvc)), str(len(amplitudes))))
        weight = 0
        for v,a in zip(pvc, amplitudes):
            weight += v * a
        
        if weight > max_weighting:
            max_weighting = weight
            max_weight_pvc = pvc
    
    peptide = ""
    current_amino_acid_weight = 0
    for val in max_weight_pvc:
        if val == 0:
            current_amino_acid_weight += 1
        else:
            current_amino_acid_weight += 1
            ch = aa_by_mass[current_amino_acid_weight]
            current_amino_acid_weight = 0
            peptide += ch
    
    if current_amino_acid_weight != 0:
        raise ValueError("Expected current_amino_acid_weight {0} = 0.".format(str(current_amino_acid_weight)))
    
    return peptide

def find_peptide_with_best_weighting_su2(peptide_vector_candidates, amplitudes, aa_by_mass):
    if _debug_:
        print("find peptide with best weighting start")
        print(amplitudes)
        print(peptide_vector_candidates)
        print(aa_by_mass)
        print()

    max_weighting = 0
    max_weight_pvc = None
    for pvc in peptide_vector_candidates:
        weight = 0

        a_idx = -1
        for a_weight in pvc:
            a_idx += a_weight
            weight += amplitudes[a_idx]

        if weight > max_weighting:
            max_weighting = weight
            max_weight_pvc = pvc
    
    peptide = ""
    for val in max_weight_pvc:
        ch = aa_by_mass[val]
        peptide += ch
    
    return peptide


if __name__ == '__main__':
    start = time.process_time()

    if len(sys.argv) < 2:
        print("Expected input:\n[str: filename path]\n\nfile contents:\n[int: graph size]\n[string: one row of graph [1...n]]\n")

    fake_amino_acids = False
    speed_up_1 = False
    speed_up_2 = False
    for a_idx in  range(2,5,1):
        if len(sys.argv) > a_idx:
            if sys.argv[a_idx] == "-f":
                fake_amino_acids = True
            if sys.argv[a_idx] == "-s":
                speed_up_1 = True
            if sys.argv[a_idx] == "-ss":
                speed_up_1 = True
                speed_up_2 = True
            if sys.argv[a_idx] == "-v":
                _verbose_ = True
            if sys.argv[a_idx] == "-vv":
                _verbose_ = True
                _timed_output_ = True
            if sys.argv[a_idx] == "-vvv":
                _verbose_ = True
                _timed_output_ = True
                _debug_ = True

    a_b_m = _amino_acid_by_mass_
    min_possible_mass = 57
    if fake_amino_acids:
        a_b_m = _fake_amino_acid_by_mass_
        min_possible_mass = 4
    
    if _debug_:
        print(a_b_m)

    amplitudes = organize_inputs(sys.argv[1])

    if speed_up_1:
        pvcs_su1 = generate_peptide_vector_candidates_su1(len(amplitudes), a_b_m, min_possible_mass, {}, 0)
        if speed_up_2:
            pvcs = pvcs_su1
        else:
            pvcs = convert_su1_pvcs_into_orig_pvcs(pvcs_su1)
    else: 
        pvcs = generate_peptide_vector_candidates(len(amplitudes), a_b_m, min_possible_mass, {}, 0)

    if _verbose_:
        print("pvcs count = {0}".format(str(len(pvcs))))
        v_end = time.process_time()
        print("pvc time: {0}".format(v_end-start))

    if speed_up_2:
        peptide = find_peptide_with_best_weighting_su2(pvcs, amplitudes, a_b_m)
    else:
        peptide = find_peptide_with_best_weighting(pvcs, amplitudes, a_b_m)

    print(peptide)

    end = time.process_time()
    if _verbose_:
        print("find peptide w best weight time: {0}".format(end - v_end))
    
    if _verbose_:
        if not speed_up_1:
            print("original algorithm")
        else:
            if not speed_up_2:
                print("speed up 1 algorithm")
            else:
                print("speed up 1 & 2  algorithm")
    print("Time: {0}".format(end-start))
