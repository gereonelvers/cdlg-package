from random import randint

import numpy as nmp

from conceptdrift.source.process_tree_controller import count_real_acs, randomize_tree_one, randomize_tree_two, \
    randomize_tree_three, randomize_tree_more


def evolve_tree_randomly(drift_tree, evolution_stage):
    """ Random change of the process tree

    :param drift_tree: tree to be changed
    :param evolution_stage: percentage of activities to be affected by the change
    :return: randomly evolved process tree version
    """
    acs = count_real_acs(drift_tree._get_leaves())
    changed_acs = []
    rounds = int(round(acs * evolution_stage + 0.001))
    if rounds == 0:
        rounds = int(nmp.ceil(acs * evolution_stage))
    i = 0
    count = 1
    happen = "Control-flow changes: "
    while i < rounds:
        happen_be = ""
        ran = randint(1, rounds - i)
        if i == 1:
            ran = randint(1, rounds - i)
        if ran == 1:
            happen_be, worked, count = randomize_tree_one(drift_tree, happen_be, changed_acs, count)
            while not worked:
                happen_be, worked, count = randomize_tree_one(drift_tree, happen_be, changed_acs, count)
        elif ran == 2:
            happen_be, worked, count = randomize_tree_two(drift_tree, happen_be, changed_acs, count)
            while not worked:
                happen_be, worked, count = randomize_tree_two(drift_tree, happen_be, changed_acs, count)
        elif ran == 3:
            happen_be, worked, count = randomize_tree_three(drift_tree, happen_be, ran, changed_acs, count)
            while not worked:
                ran = randint(1, rounds - i)
                if ran == 1:
                    ran = randint(1, rounds - i)
                if ran == 1:
                    happen_be, worked, count = randomize_tree_one(drift_tree, happen_be, changed_acs, count)
                elif ran == 2:
                    happen_be, worked, count = randomize_tree_two(drift_tree, happen_be, changed_acs, count)
                else:
                    happen_be, worked, count = randomize_tree_three(drift_tree, happen_be, ran, changed_acs, count)
        else:
            happen_be, worked, count = randomize_tree_more(drift_tree, happen_be, ran, changed_acs, count)
            while not worked:
                ran = randint(1, rounds - i)
                if ran == 1:
                    ran = randint(1, rounds - i)
                if ran == 1:
                    happen_be, worked, count = randomize_tree_one(drift_tree, happen_be, changed_acs, count)
                elif ran == 2:
                    happen_be, worked, count = randomize_tree_two(drift_tree, happen_be, changed_acs, count)
                elif ran == 3:
                    happen_be, worked, count = randomize_tree_three(drift_tree, happen_be, ran, changed_acs, count)
                else:
                    happen_be, worked, count = randomize_tree_more(drift_tree, happen_be, ran, changed_acs, count)
        happen_spl = happen_be.split(";")
        last = len(happen_spl)
        happen = happen + happen_spl[last - 2] + "; "
        i = i + ran
    return drift_tree


def evolve_tree_randomly_gs(drift_tree, evolution_stage):
    """ Random change of the process tree for gold standard

    :param drift_tree: tree to be changed
    :param evolution_stage: percentage of activities to be affected by the change
    :return: randomly evolved process tree version
    """
    acs = count_real_acs(drift_tree._get_leaves())
    changed_acs = []
    added_acs = []
    deleted_acs = []
    moved_acs = []
    rounds = int(round(acs * evolution_stage + 0.001))
    if rounds == 0:
        rounds = int(nmp.ceil(acs * evolution_stage))
    i = 0
    count = 1
    happen = ""
    while i < rounds:
        happen_be = ""
        ran = randint(1, rounds - i)
        if i == 1:
            ran = randint(1, rounds - i)
        if ran == 1:
            happen_be, worked, count = randomize_tree_one(drift_tree, happen_be, changed_acs, count)
            while not worked:
                happen_be, worked, count = randomize_tree_one(drift_tree, happen_be, changed_acs, count)
        elif ran == 2:
            happen_be, worked, count = randomize_tree_two(drift_tree, happen_be, changed_acs, count)
            while not worked:
                happen_be, worked, count = randomize_tree_two(drift_tree, happen_be, changed_acs, count)
        elif ran == 3:
            happen_be, worked, count = randomize_tree_three(drift_tree, happen_be, ran, changed_acs, count)
            while not worked:
                ran = randint(1, rounds - i)
                if ran == 1:
                    ran = randint(1, rounds - i)
                if ran == 1:
                    happen_be, worked, count = randomize_tree_one(drift_tree, happen_be, changed_acs, count)
                elif ran == 2:
                    happen_be, worked, count = randomize_tree_two(drift_tree, happen_be, changed_acs, count)
                else:
                    happen_be, worked, count = randomize_tree_three(drift_tree, happen_be, ran, changed_acs, count)
        else:
            happen_be, worked, count = randomize_tree_more(drift_tree, happen_be, ran, changed_acs, count)
            while not worked:
                ran = randint(1, rounds - i)
                if ran == 1:
                    ran = randint(1, rounds - i)
                if ran == 1:
                    happen_be, worked, count = randomize_tree_one(drift_tree, happen_be, changed_acs, count)
                elif ran == 2:
                    happen_be, worked, count = randomize_tree_two(drift_tree, happen_be, changed_acs, count)
                elif ran == 3:
                    happen_be, worked, count = randomize_tree_three(drift_tree, happen_be, ran, changed_acs, count)
                else:
                    happen_be, worked, count = randomize_tree_more(drift_tree, happen_be, ran, changed_acs, count)
        happen_spl = happen_be.split(";")
        last = len(happen_spl)
        happen = happen + happen_spl[last - 2] + "; "
        i = i + ran
        happen_ac = happen.split(';')
        if happen_ac[len(happen_ac)-2].strip() == "activity replaced":
            deleted_acs.append(changed_acs[len(changed_acs)-2])
            added_acs.append(changed_acs[len(changed_acs)-1])
        elif happen_ac[len(happen_ac)-2].strip() == "activity deleted":
            deleted_acs.append(changed_acs[len(changed_acs)-1])
        elif happen_ac[len(happen_ac)-2].strip() == "tree fragment deleted":
            deleted_acs.extend(changed_acs[len(changed_acs)-ran:len(changed_acs)])
        elif happen_ac[len(happen_ac)-2].strip() == "activity added":
            added_acs.append(changed_acs[len(changed_acs)-1])
        elif happen_ac[len(happen_ac)-2].strip() == "activity and operator added":
            added_acs.append(changed_acs[len(changed_acs)-1])
            moved_acs.extend(changed_acs[len(changed_acs)-ran:len(changed_acs)-1])
        else:
            moved_acs.extend(changed_acs[len(changed_acs)-ran:len(changed_acs)])
    return drift_tree, deleted_acs, added_acs, moved_acs
