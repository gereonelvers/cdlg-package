import copy

from pm4py.objects.process_tree import semantics
from pm4py.objects.log.obj import EventLog

from conceptdrift.source.control_flow_controller import evolve_tree_randomly_gs
from conceptdrift.source.event_log_controller import combine_two_logs


def incremental_drift(trees, traces):
    """ Generation of an event log with an incremental drift
    :param trees: process tree model versions in a list
    :param traces: number traces for each version at same position of list
    :return: event log with incremental drift
    """
    i = 0
    result = EventLog()
    while i < len(trees):
        log = semantics.generate_log(trees[i], traces[i])
        result = combine_two_logs(result, log)
        i = i + 1
    return result


def incremental_drift_gs(tree_one, start_point, end_point, nu_traces, nu_models, proportion_random_evolution):
    """ Generation of an event log with an incremental drift for gold standard conceptdrift

    :param proportion_random_evolution: proportion of the process model version to be evolved
    :param tree_one: initial model
    :param start_point: starting point for the incremental drift
    :param end_point: ending point for the incremental drift
    :param nu_traces: number traces in event log
    :param nu_models: number of intermediate models
    :return: event log with incremental drift
    """
    deleted_acs = []
    added_acs = []
    moved_acs = []
    start_traces = int(round((nu_traces * start_point) + 0.0001))
    drift_traces = int(round(((nu_traces - start_traces - (nu_traces * (1 - end_point))) / (nu_models - 1)) + 0.0001))
    end_traces = nu_traces - start_traces - (drift_traces * (nu_models - 1))
    result = semantics.generate_log(tree_one, start_traces)
    i = 0
    trees = [tree_one]
    while i < nu_models - 1:
        drift_tree = copy.deepcopy(trees[i])
        tree_ev, deleted_ac, added_ac, moved_ac = evolve_tree_randomly_gs(drift_tree, proportion_random_evolution)
        deleted_acs.extend(deleted_ac)
        added_acs.extend(added_ac)
        moved_acs.extend(moved_ac)
        trees.append(tree_ev)
        log = semantics.generate_log(trees[i + 1], drift_traces)
        result = combine_two_logs(result, log)
        i = i + 1
    drift_tree = copy.deepcopy(trees[i])
    tree_ev, deleted_ac, added_ac, moved_ac = evolve_tree_randomly_gs(drift_tree, proportion_random_evolution)
    deleted_acs.extend(deleted_ac)
    added_acs.extend(added_ac)
    moved_acs.extend(moved_ac)
    log = semantics.generate_log(tree_ev, end_traces)
    result = combine_two_logs(result, log)
    return result, deleted_acs, added_acs, moved_acs
