import copy
import datetime

from pm4py.objects.process_tree import semantics

from conceptdrift.source.control_flow_controller import evolve_tree_randomly_gs
from conceptdrift.source.event_log_controller import combine_two_logs, add_duration_to_log, get_timestamp_log
from conceptdrift.source.process_tree_controller import generate_specific_trees, visualise_tree
# from pm4py.objects.log.exporter.xes import exporter as xes_exporter


def sudden_drift(nu_traces=1000, change_point=0.5, tree_one=None, tree_two=0.2):
    """ Generation of an event log with a sudden drift

    :param tree_one: the initial version of the process model
    :param tree_two: the evolved version of the process model/ or the evolution stage of the first version
    :param nu_traces: number traces in event log
    :param change_point: change point of the drift
    :return: event log with sudden drift
    """
    deleted_acs = []
    added_acs = []
    moved_acs = []
    if tree_one is None:
        ver_one = generate_specific_trees('middle')
        ver_copy = copy.deepcopy(ver_one)
        ver_two, deleted_acs, added_acs, moved_acs = evolve_tree_randomly_gs(ver_copy, tree_two)
    elif tree_one is not None and isinstance(tree_two, float):
        ver_one = tree_one
        ver_copy = copy.deepcopy(ver_one)
        ver_two, deleted_acs, added_acs, moved_acs = evolve_tree_randomly_gs(ver_copy, tree_two)
    else:
        ver_one = tree_one
        ver_two = tree_two
    log_one_traces = int(round(nu_traces * change_point))
    log_two_traces = nu_traces - log_one_traces
    log_one = semantics.generate_log(ver_one, log_one_traces)
    log_two = semantics.generate_log(ver_two, log_two_traces)
    event_log = combine_two_logs(log_one, log_two)
    date = datetime.datetime.strptime('20/8/3 8:0:0', '%y/%d/%m %H:%M:%S')
    add_duration_to_log(event_log, date, 1, 14000)
    start_drift = get_timestamp_log(event_log, nu_traces, change_point)
    if isinstance(tree_two, float):
        data = "drift perspective: control-flow; drift type: sudden; drift start timestamp: "+str(start_drift)+" activities added: "+str(added_acs)+"; activities deleted: "+str(deleted_acs)+"; activities moved: "+str(moved_acs)
    else:
        data = "drift perspective: control-flow; drift type: sudden; drift start timestamp: "+str(start_drift)
    event_log.attributes['drift info'] = data
    return event_log


"---TESTS---"
# ve_one = generate_specific_trees('simple')
# ve_two = generate_specific_trees('simple')
# log = sudden_drift(200, 0.4, ve_one, 0.5)
# log = sudden_drift()
# xes_exporter.apply(log, "event_log.xes")
