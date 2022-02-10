import copy
import datetime

from pm4py.objects.process_tree import semantics

from conceptdrift.source.control_flow_controller import evolve_tree_randomly_gs
from conceptdrift.source.event_log_controller import generate_two_parts_of_event_log, combine_two_logs, \
    generate_several_parts_of_event_log, add_duration_to_log, get_timestamp_log
from conceptdrift.source.process_tree_controller import generate_specific_trees, visualise_tree
from pm4py.objects.log.exporter.xes import exporter as xes_exporter


def recurring_drift(nu_traces=1000, start_point=0.0,
                    end_point=1.0, number_of_seasonal_changes=3, proportion_first=0.5, tree_one=None, tree_two=0.4):
    """ Generation of an event log with a recurring drift

    :param end_point: end change point of the drift
    :param start_point: start change point of the drift
    :param proportion_first: proportion of the initial model version during the drift
    :param tree_one: initial version of the process tree
    :param tree_two: evolved version of the process tree
    :param nu_traces: number of traces in the log
    :param number_of_seasonal_changes: the number of changes of the model versions in the log
    :return: event log with recurring drift
    """
    deleted_acs = []
    added_acs = []
    moved_acs = []
    if tree_one is None:
        ver_one = generate_specific_trees('middle')
        ver_copy = copy.deepcopy(ver_one)
        ver_two, deleted_acs, added_acs, moved_acs = evolve_tree_randomly_gs(ver_copy, tree_two)
        visualise_tree(ver_one)
        visualise_tree(ver_two)
    elif tree_one is not None and isinstance(tree_two, float):
        ver_one = tree_one
        ver_copy = copy.deepcopy(ver_one)
        ver_two, deleted_acs, added_acs, moved_acs = evolve_tree_randomly_gs(ver_copy, tree_two)
        visualise_tree(ver_one)
        visualise_tree(ver_two)
    else:
        ver_one = tree_one
        ver_two = tree_two
        visualise_tree(ver_one)
        visualise_tree(ver_two)
    nu_traces_log_one = int(
        round((nu_traces * start_point) + (nu_traces * ((end_point - start_point) * proportion_first)) + 0.0001))
    nu_traces_log_two = nu_traces - nu_traces_log_one
    log_one = semantics.generate_log(ver_one, nu_traces_log_one)
    log_two = semantics.generate_log(ver_two, nu_traces_log_two)
    if start_point == 0:
        nu_occur_one = int(round((number_of_seasonal_changes + 1.1) / 2))
        nu_occur_two = (number_of_seasonal_changes + 1) - nu_occur_one
    else:
        nu_occur_two = int(round((number_of_seasonal_changes + 1.1) / 2))
        nu_occur_one = (number_of_seasonal_changes + 1) - nu_occur_two
    nu_traces_start = int(round(nu_traces * start_point + 0.0001))
    nu_traces_sec_drift = int(
        round((((nu_traces * end_point) - (nu_traces * start_point)) * (1 - proportion_first)) + 0.0001))
    event_log, log_drift = generate_two_parts_of_event_log(log_one, nu_traces_start)
    sec_drift_log, log_end = generate_two_parts_of_event_log(log_two, nu_traces_sec_drift)
    parts_log_one = generate_several_parts_of_event_log(log_drift, nu_occur_one)
    parts_log_two = generate_several_parts_of_event_log(sec_drift_log, nu_occur_two)
    if start_point == 0:
        event_log = combine_two_logs(event_log, parts_log_one[0])
        event_log = combine_two_logs(event_log, parts_log_two[0])
        i = 1
        while i < nu_occur_two:
            event_log = combine_two_logs(event_log, parts_log_one[i])
            event_log = combine_two_logs(event_log, parts_log_two[i])
            i = i + 1
        if nu_occur_two != nu_occur_one:
            event_log = combine_two_logs(event_log, parts_log_one[nu_occur_one - 1])
        if end_point != 1:
            event_log = combine_two_logs(event_log, log_end)
    else:
        event_log = combine_two_logs(event_log, parts_log_two[0])
        event_log = combine_two_logs(event_log, parts_log_one[0])
        i = 1
        while i < nu_occur_one:
            event_log = combine_two_logs(event_log, parts_log_two[i])
            event_log = combine_two_logs(event_log, parts_log_one[i])
            i = i + 1
        if nu_occur_two != nu_occur_one:
            event_log = combine_two_logs(event_log, parts_log_two[nu_occur_two - 1])
        if end_point != 1:
            event_log = combine_two_logs(event_log, log_end)
    date = datetime.datetime.strptime('20/8/3 8:0:0', '%y/%d/%m %H:%M:%S')
    add_duration_to_log(event_log, date, 1, 14000)
    start_drift = get_timestamp_log(event_log, nu_traces, start_point)
    end_drift = get_timestamp_log(event_log, nu_traces, end_point)
    if isinstance(tree_two, float):
        data = "drift perspective: control-flow; drift type: recurring; drift specific information: "+str(number_of_seasonal_changes) + " seasonal changes; drift start timestamp: "+str(start_drift)+"; drift end timestamp: "+str(end_drift)+"; activities added: "+str(added_acs)+"; activities deleted: "+str(deleted_acs)+"; activities moved: "+str(moved_acs)
    else:
        data = "drift perspective: control-flow; drift type: recurring; drift specific information: "+str(number_of_seasonal_changes) + " seasonal changes; drift start timestamp: "+str(start_drift)+"; drift end timestamp: "+str(end_drift)
    event_log.attributes['drift info'] = data
    return event_log

"---TESTS---"
# ve_one = generate_specific_trees('simple')
# ve_two = generate_specific_trees('simple')
# log = recurring_drift(1000, 4, 0.5, 0.2, 0.8, ve_one, ve_two)
# log = recurring_drift()
# xes_exporter.apply(log, "event_log.xes")
