import copy
import datetime

from pm4py.objects.process_tree import semantics

from conceptdrift.source.evolution import evolve_tree_randomly_gs
from conceptdrift.source.event_log_controller import combine_two_logs, add_duration_to_log, get_timestamp_log
from conceptdrift.source.process_tree_controller import generate_specific_trees, visualise_tree
# from pm4py.objects.log.exporter.xes import exporter as xes_exporter


def generate_log_with_sudden_drift(num_traces=1000, change_point=0.5, model_one=None, model_two=None, change_proportion=0.2):
    """ Generation of an event log with a sudden drift

    :param num_traces: number of traces in the event log
    :param change_point: change point of the drift as a proportion of the total number of traces
    :param model_one: initial version of the process tree
    :param model_two: evolved version of the process tree
    :param change_proportion: proportion of total number of activities to be changed by random evolution (model_two must be None if random evolution is targeted)
    :return: event log with sudden drift
    """
    deleted_acs = []
    added_acs = []
    moved_acs = []
    if model_one is None:
        ver_one = generate_specific_trees('middle')
        ver_copy = copy.deepcopy(ver_one)
        ver_two, deleted_acs, added_acs, moved_acs = evolve_tree_randomly_gs(ver_copy, change_proportion)
    elif model_one is not None and model_two is None:
        ver_one = model_one
        ver_copy = copy.deepcopy(ver_one)
        ver_two, deleted_acs, added_acs, moved_acs = evolve_tree_randomly_gs(ver_copy, change_proportion)
    else:
        ver_one = model_one
        ver_two = model_two
    log_one_traces = int(round(num_traces * change_point))
    log_two_traces = num_traces - log_one_traces
    log_one = semantics.generate_log(ver_one, log_one_traces)
    log_two = semantics.generate_log(ver_two, log_two_traces)
    event_log = combine_two_logs(log_one, log_two)
    date = datetime.datetime.strptime('20/8/3 8:0:0', '%y/%d/%m %H:%M:%S')
    add_duration_to_log(event_log, date, 1, 14000)
    start_drift = get_timestamp_log(event_log, num_traces, change_point)
    if model_two is None:
        data = "drift perspective: control-flow; drift type: sudden; drift start timestamp: "+str(start_drift) + " (" + str(change_point) + "); activities added: "+str(added_acs)+"; activities deleted: "+str(deleted_acs)+"; activities moved: "+str(moved_acs)
    else:
        data = "drift perspective: control-flow; drift type: sudden; drift start timestamp: "+str(start_drift)+ " (" + str(change_point) + ")"
    event_log.attributes['drift info'] = data
    return event_log


"---TESTS---"
# ve_one = generate_specific_trees('simple')
# ve_two = generate_specific_trees('simple')
# log = sudden_drift(200, 0.4, ve_one, 0.5)
# log = sudden_drift()
# xes_exporter.apply(log, "event_log.xes")
