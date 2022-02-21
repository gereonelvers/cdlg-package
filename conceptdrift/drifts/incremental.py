import copy
import datetime

from pm4py.objects.process_tree import semantics

from conceptdrift.source.evolution import evolve_tree_randomly_gs
from conceptdrift.source.event_log_controller import combine_two_logs, add_duration_to_log, get_timestamp_log
from conceptdrift.source.process_tree_controller import generate_specific_trees, visualise_tree
from pm4py.objects.log.exporter.xes import exporter as xes_exporter


def incremental_drift(num_versions=4, traces=None, change_proportion=0.1, model=generate_specific_trees('middle')):
    """ Generation of an event log with an incremental drift
    
    :param num_versions: number of occurring process tree versions
    :param traces: number traces for each version in list (e.g. [300,200,200])
    :param change_proportion: proportion of total activities to be affected by the random evolution
    :param model: initial process tree model version
    :return: event log with incremental drift
    """
    vers = [model]
    num_traces = []
    deleted_acs = []
    added_acs = []
    moved_acs = []
    if traces is None:
        j = 0
        while j < num_versions:
            num_traces.append(300)
            j += 1
    else:
        num_traces = traces
    i = 0
    event_log = semantics.generate_log(vers[i], num_traces[i])
    while i < num_versions-1:
        ver_copy = copy.deepcopy(vers[i])
        ver_new, deleted_ac, added_ac, moved_ac = evolve_tree_randomly_gs(ver_copy, change_proportion)
        deleted_acs.extend(deleted_ac)
        added_acs.extend(added_ac)
        moved_acs.extend(moved_ac)
        vers.append(ver_new)
        log = semantics.generate_log(vers[i + 1], num_traces[i + 1])
        event_log = combine_two_logs(event_log, log)
        i = i + 1
    date = datetime.datetime.strptime('20/8/3 8:0:0', '%y/%d/%m %H:%M:%S')
    add_duration_to_log(event_log, date, 1, 14000)
    len(event_log)
    start_area = float(num_traces[0]/len(event_log))
    end_area = float((len(event_log) - num_traces[len(num_traces)-1])/len(event_log))
    start_drift = get_timestamp_log(event_log, len(event_log), start_area)
    end_drift = get_timestamp_log(event_log, len(event_log), end_area)
    data = "drift type: incremental; drift perspective: control-flow; drift specific information: " + str(num_versions) + " occurring process versions; drift start timestamp: "+str(start_drift)+"; drift end timestamp: "+str(end_drift)+"; activities added: "+str(added_acs)+"; activities deleted: "+str(deleted_acs)+"; activities moved: "+str(moved_acs)
    event_log.attributes['drift info'] = data
    return event_log


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

"---TESTS---"
# ve_one = generate_specific_trees('complex')
# ve_two = generate_specific_trees('simple')
# logi = incremental_drift(5, 0.3, ve_one)
# logi = incremental_drift()
# xes_exporter.apply(logi, "event_log.xes")
