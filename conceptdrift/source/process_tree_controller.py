from __future__ import annotations

import copy
import re
from random import randint

import pm4py
from pm4py.objects.bpmn.obj import BPMN
from pm4py.objects.process_tree.obj import ProcessTree, Operator
from pm4py.visualization.process_tree import visualizer as pt_visualizer
from pm4py.algo.simulation.tree_generator import algorithm as tree_gen
from pm4py.objects.process_tree.importer import importer as ptml_importer
from pm4py.objects.conversion.bpmn import converter as bpmn_converter
from pm4py.objects.conversion.wf_net import converter as wf_net_converter
from pm4py.objects.petri_net.importer import importer as pnml_importer

""" GENERAL ALGORITHMS FOR PROCESS TREES """


def add_activity_as_parent(tree, added_activiy, added_operator):
    tree_ad = ProcessTree(None, None, None, added_activiy)
    tree_pa = ProcessTree(added_operator, None, None, None)
    combine_three_trees(tree_pa, tree_ad, tree)
    return tree_pa


def generate_tree(parameters) -> ProcessTree:
    tree_on = tree_gen.apply(parameters=parameters)
    return tree_on


def visualise_tree(tree_on):
    gviz = pt_visualizer.apply(tree_on,
                               parameters={pt_visualizer.Variants.WO_DECORATION.value.Parameters.FORMAT: "png"})
    pt_visualizer.view(gviz)


def get_type_operator(operator):
    if operator == 'seq':
        return Operator.SEQUENCE
    elif operator == 'xor':
        return Operator.XOR
    elif operator == 'and':
        return Operator.PARALLEL
    elif operator == 'xor loop':
        return Operator.LOOP
    elif operator == 'or':
        return Operator.OR
    else:
        return None


def generate_tree_two_ac(activity_one, activity_two, operator):
    tree_one = ProcessTree(None, None, None, activity_one)
    tree_two = ProcessTree(None, None, None, activity_two)
    tree_op = ProcessTree(operator, None, None, None)
    combine_three_trees(tree_op, tree_one, tree_two)
    return tree_op


def combine_three_trees(tree_parent, tree_ch_one, tree_ch_two):
    tree_ch_one._set_parent(tree_parent)
    tree_ch_two._set_parent(tree_parent)
    tree_parent._set_children([tree_ch_one, tree_ch_two])


def count_leaf(leaves, leaf):
    count = 0
    for x in leaves:
        if x._get_label() == leaf or (x._get_label() is None and leaf == '*tau*'):
            count = count + 1
    return count


def count_real_acs(leaves):
    count = 0
    for leaf in leaves:
        if leaf._get_label() is not None:
            count = count + 1
    return count


def count_leaf_ran(leaves, leaf):
    count = 0
    for x in leaves:
        if x._get_label() == leaf:
            count = count + 1
    return count


def break_down_tree_fully(tree):
    operators_list = []
    all_tree_list_without_leaves = []
    tree_dict = {}
    if tree._get_children() == list():
        tree_dict[0] = tree
    else:
        j = 0
        operators_list.append(tree._get_operator())
        all_tree_list_without_leaves.append(tree)
        tree_list = []
        children_tree = tree._get_children()
        for x in children_tree:
            tree_list.append(x)
        for child in tree_list:
            if child._get_children() == list():
                tree_dict[j] = child._get_label()
                j = j + 1
            else:
                operators_list.append(child._get_operator())
                all_tree_list_without_leaves.append(child)
                for ch_child in child._get_children():
                    tree_list.append(ch_child)
    return operators_list, all_tree_list_without_leaves, tree_dict


def generate_specific_trees(str_clp='middle'):
    """ Generation of a random process tree with different complexity

    :param str_clp: complexity of process tree ['simple','middle','complex']
    :return: randomly generated process tree
    """
    if str_clp == 'simple':
        parameters = {'mode': 10, 'min': 8, 'max': 12, 'sequence': 0.25, 'choice': 0.25, 'parallel': 0.25, 'loop': 0.2,
                      'or': 0, 'silent': 0, 'duplicate': 0, 'lt_dependency': 0, 'infrequent': 0.25, 'no_models': 10,
                      'unfold': 10, 'max_repeat': 10}
        tree_ran = generate_tree(parameters)
    elif str_clp == 'middle':
        parameters = {'mode': 18, 'min': 14, 'max': 20, 'sequence': 0.25, 'choice': 0.3, 'parallel': 0.25, 'loop': 0.25,
                      'or': 0, 'silent': 0, 'duplicate': 0, 'lt_dependency': 0, 'infrequent': 0.25, 'no_models': 10,
                      'unfold': 10, 'max_repeat': 10}
        tree_ran = generate_tree(parameters)
    else:
        parameters = {'mode': 25, 'min': 20, 'max': 30, 'sequence': 0.25, 'choice': 0.3, 'parallel': 0.25, 'loop': 0.3,
                      'or': 0, 'silent': 0, 'duplicate': 0, 'lt_dependency': 0, 'infrequent': 0.25, 'no_models': 10,
                      'unfold': 10, 'max_repeat': 10}
        tree_ran = generate_tree(parameters)
    return tree_ran


def generate_child_list(children, tree_ac, position):
    child_sx = []
    l = 0
    for y in children:
        if l < position:
            child_sx.append(y)
            l = l + 1
    child_sx.append(tree_ac)
    k = 0
    for y in children:
        if k >= position:
            child_sx.append(y)
            k = k + 1
        else:
            k = k + 1
    return child_sx


def get_subtree_acs(trees, loc):
    activities = []
    for x in loc:
        for ac in get_leaves_of_part_tree(trees[x]):
            activities.append(ac)
    return activities


def check_operator_multiple(trees, operator):
    count = 0
    loc = []
    for x in trees:
        if x == list():
            count = count + 1
            continue
        else:
            if x._get_operator() == get_type_operator(operator):
                loc.append(count)
                count = count + 1
            else:
                count = count + 1
    return loc


def get_position_in_children(children, child):
    position = 0
    for x in children:
        if x == child:
            break
        else:
            position = position + 1
    return position


def check_same_parent(part_one, part_two):
    same_parent = False
    for te in get_leaves_of_part_tree(part_two):
        if te in get_leaves_of_part_tree(part_one):
            same_parent = True
            break
    for te in get_leaves_of_part_tree(part_one):
        if te in get_leaves_of_part_tree(part_two):
            same_parent = True
            break
    return same_parent


def check_parent_of(part_one, part_two):
    same_parent = False
    for te in get_leaves_of_part_tree(part_two):
        if te in get_leaves_of_part_tree(part_one):
            same_parent = True
            break
    if same_parent != True and (
            part_two._get_operator() == get_type_operator("xor loop") and len(part_two.children) >= 3):
        same_parent = True
    return same_parent


def check_num_leaves(tree_list, length, changed_acs, operator=None):
    correct = False
    for x in tree_list:
        if check_tree_part(x, length, changed_acs, operator):
            correct = True
            break
    return correct


def check_tree_part(x, length, changed_acs, operator=None):
    correct = False
    if count_real_acs(get_leaves_of_part_tree(x)) == length and ((operator is None) or (
            operator is not None and (operator != 'xor loop' or (operator == 'xor loop' and len(x.children) < 3)))):
        correct = True
        for ac in get_leaves_of_part_tree(x):
            if ac in changed_acs:
                correct = False
                break
    return correct


def get_right_rand_ac(count, tree):
    leaves = tree._get_leaves()
    leaves_la = []
    for x in leaves:
        leaves_la.append(x._get_label())
    while "Random activity " + str(count) in leaves_la:
        count = count + 1
    return count


def import_process_model(str_cf):
    """ Imports process model and changes it to a process tree

    :param str_cf: filepath as string
    :return: process tree
    """
    if re.fullmatch('.*\.ptml', str_cf):
        return ptml_importer.apply(str_cf)
    elif re.fullmatch('.*\.bpmn', str_cf):
        bpmn_tree = pm4py.read_bpmn(str_cf)
        net, im, fm = bpmn_converter.apply(bpmn_tree)
        return wf_net_converter.apply(net, im, fm)
    else:
        net, im, fm = pnml_importer.apply(str_cf)
        return wf_net_converter.apply(net, im, fm)


def change_process_model(model):
    """ Changes process model to a process tree

    :param model: process model (BPMN/ process tree)
    :return: process tree
    """
    if isinstance(model, ProcessTree):
        return model
    elif isinstance(model, BPMN):
        net, im, fm = bpmn_converter.apply(model)
        return wf_net_converter.apply(net, im, fm)


def get_part_tree_depth(tree, depth):
    trees_one = [tree]
    trees_two = [tree]
    trees_in_depth = []
    step = 0
    first = True
    hin = 0
    while step < depth:
        k = 0
        j = 0
        len_tree = len(trees_two)
        trees_in_depth = []
        for x in trees_two:
            if (k >= (len_tree - hin) and step < depth) or first:
                chi_trees = x.children
                for child in chi_trees:
                    trees_one.append(child)
                    trees_in_depth.append(child)
                    j = j + 1
                    first = False
            else:
                k = k + 1
        trees_two = copy.copy(trees_one)
        hin = j
        step = step + 1
    return trees_in_depth


def get_leaves_of_part_tree(tree):
    leaves = []
    trees = []
    children = tree.children
    for child in children:
        if child.children == list():
            leaves.append(child)
        else:
            trees.append(child)
    for child in trees:
        if child.children == list():
            leaves.append(child)
        else:
            for x in child.children:
                trees.append(x)
    return leaves


def get_position_in_child_list(x, ac, operator):
    parent = x.parent
    children = parent.children
    position = 0
    breaker = False
    for child in children:
        if child.children == list():
            position = position + 1
        else:
            loc = check_operator_multiple(children, operator)
            if len(loc) > 1:
                if child._get_operator() == get_type_operator(operator):
                    leaves = get_leaves_of_part_tree(child)
                    for leaf in leaves:
                        if leaf._get_label() == ac:
                            breaker = True
                            break
                    if breaker:
                        break
                    else:
                        position = position + 1
                else:
                    position = position + 1
            else:
                if child._get_operator() == get_type_operator(operator):
                    break
                else:
                    position = position + 1
    return position


def check_condition_empty_trace_one(tree, tree_part):
    first_check=  ((tree._get_operator() != get_type_operator('xor') and tree._get_operator() != get_type_operator(
        'xor loop') and tree._get_operator() != get_type_operator('or')) or (
                    tree_part._get_parent()._get_operator() != get_type_operator(
                'xor') and tree_part._get_parent()._get_operator() != get_type_operator(
                'xor loop') and tree_part._get_parent()._get_operator() != get_type_operator('or')))
    second_check = True
    parent = tree_part._get_parent()
    children = parent.children
    count = 0
    for x in children:
        if x.children == list():
            if x._get_label() is None:
                count = count + 1
    if count + 1 == len(children):
        second_check = False
    return first_check and second_check


def check_condition_empty_trace_two(tree, tree_part, operator):
    first_check=  ((tree._get_operator() != get_type_operator('xor') and tree._get_operator() != get_type_operator(
        'xor loop') and tree._get_operator() != get_type_operator('or')) or (
                    operator != get_type_operator(
                'xor') and operator != get_type_operator(
                'xor loop') and operator != get_type_operator('or')))
    second_check = True
    children = tree_part.children
    count = 0
    for x in children:
        if x.children == list():
            if x._get_label() is None:
                count = count + 1
    if count + 1 == len(children):
        second_check = False
    return first_check or second_check


""" ALGORITHMS FOR RANDOM EVOLUTION """


def swap_two_existing_activities_ran(tree, activity_one, activity_two):
    leaves = tree._get_leaves()
    first = True
    second = True
    for leaf in leaves:
        if (leaf._get_label() == activity_one or (leaf._get_label() is None and activity_one == '*tau*')) and first:
            leaf._set_label(activity_two)
            first = False
        elif (leaf._get_label() == activity_two or (leaf._get_label() is None and activity_two == '*tau*')) and second:
            leaf._set_label(activity_one)
            second = False


def change_random_operator_num(tree, wish_operator, length, changed_acs):
    operators_list, all_tree_operator_list, tree_dict = break_down_tree_fully(tree)
    if check_num_leaves(all_tree_operator_list, length, changed_acs, wish_operator):
        i = randint(0, len(operators_list) - 1)
        while not check_tree_part(all_tree_operator_list[i], length, changed_acs, wish_operator):
            i = randint(0, len(operators_list) - 1)
        if check_condition_empty_trace_two(tree, all_tree_operator_list[i], wish_operator) and wish_operator != all_tree_operator_list[i]._get_operator():
            leaves = get_leaves_of_part_tree(all_tree_operator_list[i])
            for leaf in leaves:
                if leaf._get_label() is None:
                    continue
                else:
                    changed_acs.append(leaf)
            all_tree_operator_list[i]._set_operator(wish_operator)
            return True
        else:
            return False
    else:
        return False


def delete_random_tree_part(tree, length, changed_acs):
    operators_list, all_tree_operator_list, tree_dict = break_down_tree_fully(tree)
    if check_num_leaves(all_tree_operator_list, length, changed_acs):
        i = randint(1, len(operators_list) - 1)
        while not check_tree_part(all_tree_operator_list[i], length, changed_acs):
            i = randint(0, len(operators_list) - 1)
        if check_condition_empty_trace_one(tree, all_tree_operator_list[i]):
            leaves = get_leaves_of_part_tree(all_tree_operator_list[i])
            for leaf in leaves:
                if leaf._get_label() is None:
                    continue
                else:
                    changed_acs.append(copy.deepcopy(leaf))
            emp = ProcessTree(None, None, None, None)
            parent = all_tree_operator_list[i]._get_parent()
            children = parent.children
            position = 0
            for x in children:
                if x == all_tree_operator_list[i]:
                    break
                else:
                    position = position + 1
            emp._set_parent(parent)
            children[position] = emp
            parent._set_children(children)
            return True
        else:
            return False
    else:
        return False


def replace_activity_ran(tree, activity_old, activity_new, changed_acs):
    leaves = tree._get_leaves()
    worked = False
    if activity_old is not None:
        for leaf in leaves:
            if leaf._get_label() == activity_old:
                changed_acs.append(copy.deepcopy(leaf))
                leaf._set_label(activity_new)
                changed_acs.append(leaf)
                worked = True
                break
    return worked


def delete_activity_ran(tree, activity, changed_acs):
    leaves = tree._get_leaves()
    worked = False
    for leaf in leaves:
        if leaf._get_label() == activity and check_condition_empty_trace_one(tree, leaf):
            changed_acs.append(copy.deepcopy(leaf))
            leaf._set_label(None)
            worked = True
            break
    return worked


def add_random_activity(tree, ac, changed_acs):
    operators_list, all_tree_operator_list, tree_dict = break_down_tree_fully(tree)
    position = randint(0, len(operators_list) - 1)
    while all_tree_operator_list[position]._get_operator() == get_type_operator('xor loop') and len(
            all_tree_operator_list[position].children) >= 3:
        position = randint(0, len(operators_list) - 1)
    tree_ac = ProcessTree(None, None, None, ac)
    children = all_tree_operator_list[position].children
    children.append(tree_ac)
    tree_ac._set_parent(all_tree_operator_list[position])
    all_tree_operator_list[position]._set_children(children)
    changed_acs.append(tree_ac)


def swap_random_tree_part(tree, length, changed_acs):
    operators_list, all_tree_operator_list, tree_dict = break_down_tree_fully(tree)
    l = randint(1, length - 2)
    j = length - l
    i_one = randint(0, len(operators_list) - 1)
    i_two = randint(0, len(operators_list) - 1)
    while i_one == i_two:
        i_two = randint(0, len(operators_list) - 1)
    if check_num_leaves(all_tree_operator_list, l, changed_acs) and check_num_leaves(all_tree_operator_list, j,
                                                                                     changed_acs):
        while not check_tree_part(all_tree_operator_list[i_one], l, changed_acs):
            i_one = randint(0, len(operators_list) - 1)
        while not check_tree_part(all_tree_operator_list[i_two], j, changed_acs):
            i_two = randint(0, len(operators_list) - 1)
        if check_same_parent(all_tree_operator_list[i_one], all_tree_operator_list[i_two]):
            return False
        else:
            leaves_one = get_leaves_of_part_tree(all_tree_operator_list[i_one])
            leaves_two = get_leaves_of_part_tree(all_tree_operator_list[i_two])
            for leaf in leaves_one:
                if leaf._get_label() is None:
                    continue
                else:
                    changed_acs.append(leaf)
            for leaf in leaves_two:
                if leaf._get_label() is None:
                    continue
                else:
                    changed_acs.append(leaf)
            parent_one = all_tree_operator_list[i_one]._get_parent()
            parent_two = all_tree_operator_list[i_two]._get_parent()
            children_one = parent_one.children
            children_two = parent_two.children
            position_one = get_position_in_children(children_one, all_tree_operator_list[i_one])
            position_two = get_position_in_children(children_two, all_tree_operator_list[i_two])
            all_tree_operator_list[i_one]._set_parent(parent_two)
            children_two[position_two] = all_tree_operator_list[i_one]
            parent_two._set_children(children_two)
            all_tree_operator_list[i_two]._set_parent(parent_one)
            children_one[position_one] = all_tree_operator_list[i_two]
            parent_one._set_children(children_one)
            return True
    else:
        return False


def swap_random_ac_with_tree_part(tree, length, ac, changed_acs):
    operators_list, all_tree_operator_list, tree_dict = break_down_tree_fully(tree)
    if check_num_leaves(all_tree_operator_list, length - 1, changed_acs):
        i = randint(1, len(operators_list) - 1)
        while not check_tree_part(all_tree_operator_list[i], length - 1, changed_acs):
            i = randint(0, len(operators_list) - 1)
        if ac in get_leaves_of_part_tree(all_tree_operator_list[i]) or (
                ac._get_parent() == all_tree_operator_list[i]._get_parent()
                and (ac._get_parent()._get_operator() != get_type_operator('seq')
                     or ac._get_parent()._get_operator() != get_type_operator('xor loop'))):
            return False
        else:
            changed_acs.append(ac)
            leaves = get_leaves_of_part_tree(all_tree_operator_list[i])
            for leaf in leaves:
                if leaf._get_label() is None:
                    continue
                else:
                    changed_acs.append(leaf)
            parent_one = ac._get_parent()
            parent_two = all_tree_operator_list[i]._get_parent()
            children_one = parent_one.children
            children_two = parent_two.children
            position_one = get_position_in_children(children_one, ac)
            position_two = get_position_in_children(children_two, all_tree_operator_list[i])
            ac._set_parent(parent_two)
            children_two[position_two] = ac
            parent_two._set_children(children_two)
            all_tree_operator_list[i]._set_parent(parent_one)
            children_one[position_one] = all_tree_operator_list[i]
            parent_one._set_children(children_one)
            return True
    else:
        return False


def swap_random_ops(tree, length, changed_acs):
    operators_list, all_tree_operator_list, tree_dict = break_down_tree_fully(tree)
    l = randint(1, length - 2)
    j = length - l
    i_one = randint(0, len(operators_list) - 1)
    i_two = randint(0, len(operators_list) - 1)
    while i_one == i_two:
        i_two = randint(0, len(operators_list) - 1)
    if check_num_leaves(all_tree_operator_list, l, changed_acs) and check_num_leaves(all_tree_operator_list, j,
                                                                                     changed_acs):
        while not check_tree_part(all_tree_operator_list[i_one], l, changed_acs):
            i_one = randint(0, len(operators_list) - 1)
        while not check_tree_part(all_tree_operator_list[i_two], j, changed_acs):
            i_two = randint(0, len(operators_list) - 1)
        if all_tree_operator_list[i_one]._get_operator() == all_tree_operator_list[i_two]._get_operator() or ((all_tree_operator_list[i_one]._get_operator() == get_type_operator('xor loop')
                                                                                                               and len(all_tree_operator_list[i_two].children) > 3)
                                                                                                              or (all_tree_operator_list[i_two]._get_operator() == get_type_operator(
                                                                                                                  'xor loop') and len(
                                                                                                                  all_tree_operator_list[i_one].children) > 3)) \
                or not check_condition_empty_trace_two(tree, all_tree_operator_list[i_one], all_tree_operator_list[i_two]._get_operator()) \
                or not check_condition_empty_trace_two(tree, all_tree_operator_list[i_two], all_tree_operator_list[i_one]._get_operator()):
            return False
        else:
            leaves_one = get_leaves_of_part_tree(all_tree_operator_list[i_one])
            leaves_two = get_leaves_of_part_tree(all_tree_operator_list[i_two])
            for leaf in leaves_one:
                if leaf._get_label() is None:
                    continue
                else:
                    changed_acs.append(leaf)
            for leaf in leaves_two:
                if leaf not in changed_acs:
                    if leaf._get_label() is None:
                        continue
                    else:
                        changed_acs.append(leaf)
            operator_one = all_tree_operator_list[i_one]._get_operator()
            operator_two = all_tree_operator_list[i_two]._get_operator()
            all_tree_operator_list[i_one]._set_operator(operator_two)
            all_tree_operator_list[i_two]._set_operator(operator_one)
            return True
    else:
        return False


def move_random_tree_fragment(tree, length, changed_acs):
    operators_list, all_tree_operator_list, tree_dict = break_down_tree_fully(tree)
    if check_num_leaves(all_tree_operator_list, length, changed_acs):
        i = randint(1, len(operators_list) - 1)
        while not check_tree_part(all_tree_operator_list[i], length, changed_acs):
            i = randint(1, len(operators_list) - 1)
        y = randint(0, len(operators_list) - 1)
        while y == i or all_tree_operator_list[i].parent == all_tree_operator_list[y]:
            y = randint(0, len(operators_list) - 1)
        if check_parent_of(all_tree_operator_list[i], all_tree_operator_list[y]) or not check_condition_empty_trace_one(tree,
                                                                                                                        all_tree_operator_list[
                                                                                                               i]):
            return False
        else:
            leaves = get_leaves_of_part_tree(all_tree_operator_list[i])
            for leaf in leaves:
                if leaf._get_label() is None:
                    continue
                else:
                    changed_acs.append(leaf)
            parent = all_tree_operator_list[i].parent
            parent_children = parent.children
            position = get_position_in_children(parent_children, all_tree_operator_list[i])
            emp_tree = ProcessTree(None, None, None, None)
            emp_tree._set_parent(parent)
            parent_children[position] = emp_tree
            parent._set_children(parent_children)
            children = all_tree_operator_list[y].children
            children.append(all_tree_operator_list[i])
            all_tree_operator_list[i]._set_parent(all_tree_operator_list[y])
            return True
    else:
        return False


def add_random_op_ac(tree, ac, op, length, changed_acs):
    operators_list, all_tree_operator_list, tree_dict = break_down_tree_fully(tree)
    if check_num_leaves(all_tree_operator_list, length - 1, changed_acs):
        i = randint(1, len(operators_list) - 1)
        while not check_tree_part(all_tree_operator_list[i], length - 1, changed_acs):
            i = randint(0, len(operators_list) - 1)
        leaves = get_leaves_of_part_tree(all_tree_operator_list[i])
        for leaf in leaves:
            if leaf._get_label() is None:
                continue
            else:
                changed_acs.append(leaf)
        parent = all_tree_operator_list[i]._get_parent()
        tree_ac = ProcessTree(None, None, None, ac)
        tree_op = ProcessTree(get_type_operator(op), None, None, None)
        combine_three_trees(tree_op, tree_ac, all_tree_operator_list[i])
        children = parent.children
        position = 0
        for x in children:
            if x == all_tree_operator_list[i]:
                break
            else:
                position = position + 1
        children[position] = tree_op
        tree_op._set_parent(parent)
        parent._set_children(children)
        changed_acs.append(tree_ac)
        return True
    else:
        return False


def randomize_tree_one(tree_one, happen, changed_acs, count):
    i = randint(0, 1)
    leaves = tree_one._get_leaves()
    worked = True
    if i == 0:
        ran = randint(0, len(leaves) - 1)
        while leaves[ran]._get_label() is None or leaves[ran] in changed_acs:
            ran = randint(0, len(leaves) - 1)
        happen = happen + "activity deleted; "
        worked = delete_activity_ran(tree_one, leaves[ran]._get_label(), changed_acs)
    elif i == 1:
        happen = happen + "activity added; "
        count = get_right_rand_ac(count, tree_one)
        add_random_activity(tree_one, 'Random activity ' + str(count), changed_acs)
        count = count + 1
    return happen, worked, count


def randomize_tree_two(tree_one, happen, changed_acs, count):
    length = 2
    i = randint(0, 4)
    leaves = tree_one._get_leaves()
    worked = True
    if i == 2:
        i = randint(0, 4)
    if i == 0:
        if len(leaves) > 2:
            ran_one = randint(0, len(leaves) - 1)
            ran_two = randint(0, len(leaves) - 1)
            while ran_one == ran_two or leaves[ran_one] in changed_acs or leaves[
                ran_two] in changed_acs or (
                    leaves[ran_one]._get_label() is None or leaves[ran_two]._get_label() is None):
                ran_one = randint(0, len(leaves) - 1)
                ran_two = randint(0, len(leaves) - 1)
            if leaves[ran_one]._get_parent() == leaves[ran_two]._get_parent() and (
                    leaves[ran_one]._get_parent()._get_operator() != get_type_operator('xor loop') or leaves[
                ran_one]._get_parent()._get_operator() != get_type_operator('seq')) or leaves[ran_one]._get_label() == \
                    leaves[ran_two]._get_label() \
                    or count_leaf_ran(tree_one._get_leaves(), leaves[ran_one]._get_label()) > 1 < count_leaf_ran(
                tree_one._get_leaves(), leaves[ran_two]._get_label()):
                worked = False
            else:
                changed_acs.append(leaves[ran_one])
                changed_acs.append(leaves[ran_two])
                happen = happen + "activities swapped; "
                swap_two_existing_activities_ran(tree_one, leaves[ran_one]._get_label(), leaves[ran_two]._get_label())
    elif i == 1:
        opera_list = ['seq', 'xor', 'xor loop', 'and']
        ran_op = randint(0, len(opera_list) - 1)
        happen = happen + "operator replaced; "
        worked = change_random_operator_num(tree_one, get_type_operator(opera_list[ran_op]), length, changed_acs)
    elif i == 2:
        happen = happen + "tree fragment deleted; "
        worked = delete_random_tree_part(tree_one, length, changed_acs)
    elif i == 3:
        happen = happen + "tree fragment moved; "
        worked = move_random_tree_fragment(tree_one, length, changed_acs)
    elif i == 4:
        ran = randint(0, len(leaves) - 1)
        while leaves[ran] in changed_acs:
            ran = randint(0, len(leaves) - 1)
        happen = happen + "activity replaced; "
        count = get_right_rand_ac(count, tree_one)
        worked = replace_activity_ran(tree_one, leaves[ran]._get_label(), 'Random activity ' + str(count), changed_acs)
        count = count + 1
    return happen, worked, count


def randomize_tree_three(tree_one, happen, length, changed_acs, count):
    i = randint(0, 4)
    worked = True
    if i == 1:
        i = randint(0, 4)
    if i == 0:
        opera_list = ['seq', 'xor', 'xor loop', 'and']
        ran_op = randint(0, len(opera_list) - 1)
        happen = happen + "operator replaced; "
        worked = change_random_operator_num(tree_one, get_type_operator(opera_list[ran_op]), length, changed_acs)
    elif i == 1:
        happen = happen + "tree fragment deleted; "
        worked = delete_random_tree_part(tree_one, length, changed_acs)
    elif i == 2:
        happen = happen + "activity and operator added; "
        opera_list = ['seq', 'xor', 'xor loop', 'and']
        ran_op = randint(0, len(opera_list) - 1)
        count = get_right_rand_ac(count, tree_one)
        worked = add_random_op_ac(tree_one, 'Random activity ' + str(count), opera_list[ran_op], length,
                                          changed_acs)
        if worked:
            count = count + 1
    elif i == 3:
        leaves = tree_one._get_leaves()
        ran_do = randint(0, len(leaves) - 1)
        while leaves[ran_do]._get_label() is None or leaves[ran_do] in changed_acs:
            ran_do = randint(0, len(leaves) - 1)
        happen = happen + "activity with tree fragment swapped; "
        worked = swap_random_ac_with_tree_part(tree_one, length, leaves[ran_do], changed_acs)
    elif i == 4:
        happen = happen + "tree fragment moved; "
        worked = move_random_tree_fragment(tree_one, length, changed_acs)
    return happen, worked, count


def randomize_tree_more(tree_one, happen, length, changed_acs, count):
    i = randint(0, 6)
    worked = True
    if i == 1:
        i = randint(0, 6)
    if i == 0:
        opera_list = ['seq', 'xor', 'xor loop', 'and']
        ran_op = randint(0, len(opera_list) - 1)
        happen = happen + "operator replaced; "
        worked = change_random_operator_num(tree_one, get_type_operator(opera_list[ran_op]), length, changed_acs)
    elif i == 1:
        happen = happen + "tree fragment deleted; "
        worked = delete_random_tree_part(tree_one, length, changed_acs)
    elif i == 2:
        happen = happen + "activity and operator added; "
        opera_list = ['seq', 'xor', 'xor loop', 'and']
        ran_op = randint(0, len(opera_list) - 1)
        count = get_right_rand_ac(count, tree_one)
        worked = add_random_op_ac(tree_one, 'Random activity ' + str(count), opera_list[ran_op], length,
                                          changed_acs)
        if worked:
            count = count + 1
    elif i == 3:
        leaves = tree_one._get_leaves()
        ran_do = randint(0, len(leaves) - 1)
        while leaves[ran_do]._get_label() is None or leaves[ran_do]._get_label() in changed_acs:
            ran_do = randint(0, len(leaves) - 1)
        happen = happen + "activity with tree fragment swapped; "
        worked = swap_random_ac_with_tree_part(tree_one, length, leaves[ran_do], changed_acs)
    elif i == 4:
        happen = happen + "tree fragments swapped; "
        worked = swap_random_tree_part(tree_one, length, changed_acs)
        if not worked:
            worked = swap_random_tree_part(tree_one, length, changed_acs)
    elif i == 5:
        happen = happen + "operators swapped; "
        worked = swap_random_ops(tree_one, length, changed_acs)
        if not worked:
            worked = swap_random_ops(tree_one, length, changed_acs)
    elif i == 6:
        happen = happen + "tree fragment moved; "
        worked = move_random_tree_fragment(tree_one, length, changed_acs)
    return happen, worked, count
