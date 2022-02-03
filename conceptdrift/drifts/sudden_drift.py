
from pm4py.objects.process_tree import semantics

from conceptdrift.source.event_log_controller import combine_two_logs


def sudden_drift(tree_one, tree_two, nu_traces, change_point):
    """ Generation of an event log with a sudden drift

    :param tree_one: the initial version of the process model
    :param tree_two: the evolved version of the process model
    :param nu_traces: number traces in event log
    :param change_point: change point of the drift
    :return: event log with sudden drift
    """
    log_one_traces = int(round(nu_traces * change_point))
    log_two_traces = nu_traces - log_one_traces
    log_one = semantics.generate_log(tree_one, log_one_traces)
    log_two = semantics.generate_log(tree_two, log_two_traces)
    logs_combined = combine_two_logs(log_one, log_two)
    return logs_combined
