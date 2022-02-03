
from pm4py.objects.process_tree import semantics

from conceptdrift.source.event_log_controller import generate_two_parts_of_event_log, combine_two_logs, \
    generate_several_parts_of_event_log


def recurring_drift(tree_one, tree_two, nu_traces, number_of_seasonal_changes, proportion_first, start_point,
                    end_point):
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
    nu_traces_log_one = int(
        round((nu_traces * start_point) + (nu_traces * ((end_point - start_point) * proportion_first)) + 0.0001))
    nu_traces_log_two = nu_traces - nu_traces_log_one
    log_one = semantics.generate_log(tree_one, nu_traces_log_one)
    log_two = semantics.generate_log(tree_two, nu_traces_log_two)
    if start_point == 0:
        nu_occur_one = int(round((number_of_seasonal_changes + 1.1) / 2))
        nu_occur_two = (number_of_seasonal_changes + 1) - nu_occur_one
    else:
        nu_occur_two = int(round((number_of_seasonal_changes + 1.1) / 2))
        nu_occur_one = (number_of_seasonal_changes + 1) - nu_occur_two
    nu_traces_start = int(round(nu_traces * start_point + 0.0001))
    nu_traces_sec_drift = int(
        round((((nu_traces * end_point) - (nu_traces * start_point)) * (1 - proportion_first)) + 0.0001))
    result, log_drift = generate_two_parts_of_event_log(log_one, nu_traces_start)
    sec_drift_log, log_end = generate_two_parts_of_event_log(log_two, nu_traces_sec_drift)
    parts_log_one = generate_several_parts_of_event_log(log_drift, nu_occur_one)
    parts_log_two = generate_several_parts_of_event_log(sec_drift_log, nu_occur_two)
    if start_point == 0:
        result = combine_two_logs(result, parts_log_one[0])
        result = combine_two_logs(result, parts_log_two[0])
        i = 1
        while i < nu_occur_two:
            result = combine_two_logs(result, parts_log_one[i])
            result = combine_two_logs(result, parts_log_two[i])
            i = i + 1
        if nu_occur_two != nu_occur_one:
            result = combine_two_logs(result, parts_log_one[nu_occur_one - 1])
        if end_point != 1:
            result = combine_two_logs(result, log_end)
    else:
        result = combine_two_logs(result, parts_log_two[0])
        result = combine_two_logs(result, parts_log_one[0])
        i = 1
        while i < nu_occur_one:
            result = combine_two_logs(result, parts_log_two[i])
            result = combine_two_logs(result, parts_log_one[i])
            i = i + 1
        if nu_occur_two != nu_occur_one:
            result = combine_two_logs(result, parts_log_two[nu_occur_two - 1])
        if end_point != 1:
            result = combine_two_logs(result, log_end)
    return result
