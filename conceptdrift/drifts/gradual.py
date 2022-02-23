import copy
import datetime
import math

import numpy
from pm4py.objects.log.obj import EventLog

from pm4py.objects.process_tree import semantics

from conceptdrift.source.evolution import evolve_tree_randomly_gs
from conceptdrift.source.event_log_controller import combine_two_logs, add_duration_to_log, get_timestamp_log
from conceptdrift.source.noise import add_noise
from conceptdrift.source.process_tree_controller import generate_specific_trees, visualise_tree
from pm4py.objects.log.exporter.xes import exporter as xes_exporter


def gradual_drift(num_traces=1000, start_point=0.4, end_point=0.6, distribution_type='linear', model_one=None, model_two=None, change_proportion=0.2):
    """ Generation of an event log with a gradual drift

    :param num_traces: number of traces in the event log
    :param start_point: start change point of the drift as a proportion of the total number of traces
    :param end_point: end change point of the drift as a proportion of the total number of traces
    :param distribution_type: type of distribution of the traces during the drift [linear, exponential]
    :param model_one: initial version of the process tree
    :param model_two: evolved version of the process tree
    :param change_proportion: proportion of total number of activities to be changed by random evolution (model_two must be None if random evolution is targeted)
    :return: event log with gradual drift
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
    log_before_drift_traces = int(round((start_point * num_traces) + 0.0001))
    log_after_drift_traces = int(round(((1-end_point) * num_traces) + 0.0001))
    nu_traces_for_drift = num_traces - log_before_drift_traces - log_after_drift_traces
    log_before_drift = semantics.generate_log(ver_one, log_before_drift_traces)
    log_after_drift = semantics.generate_log(ver_two, log_after_drift_traces)
    log_combined_with_drift = distribute_traces(ver_one, ver_two, distribution_type,
                                                nu_traces_for_drift)
    log_be_one = combine_two_logs(log_before_drift, log_combined_with_drift)
    event_log = combine_two_logs(log_be_one, log_after_drift)
    date = datetime.datetime.strptime('20/8/3 8:0:0', '%y/%d/%m %H:%M:%S')
    add_duration_to_log(event_log, date, 1, 14000)
    start_drift = get_timestamp_log(event_log, num_traces, start_point)
    end_drift = get_timestamp_log(event_log, num_traces, end_point)
    if model_two is None:
        data = "drift perspective: control-flow; drift type: gradual; drift specific information: "+distribution_type+" distribution; drift start timestamp: "+str(start_drift)+" (" + str(start_point) + "); drift end timestamp: "+str(end_drift) + " (" + str(end_point) + "); activities added: "+str(added_acs)+"; activities deleted: "+str(deleted_acs)+"; activities moved: "+str(moved_acs)
    else:
        data = "drift perspective: control-flow; drift type: gradual; drift specific information: "+distribution_type+" distribution; drift start timestamp: "+str(start_drift)+" (" + str(start_point) + "); drift end timestamp: "+str(end_drift) + " (" + str(end_point) + ")"
    event_log.attributes['drift info'] = data
    return event_log


def distribute_traces(tree_one, tree_two, distribute_type, nu_traces):
    """Linear or exponential distribution of the traces during the gradual drift

    :param tree_one: initial model
    :param tree_two: evolved model
    :param distribute_type: distribution type (linear, exponential)
    :param nu_traces: number of occurring traces during drift
    :return: An log only including the gradual drift part
    """
    result = EventLog()
    count = 0
    if distribute_type.strip() == 'linear':
        rest_one, rest_two, rounds, b = get_rest_parameter(nu_traces, distribute_type)
        x = 1
        most_one = rest_one + b * rounds
        most_two = rest_two + b * rounds
        while x <= rounds:
            if x == rounds:
                count = count + most_two
                log_t = semantics.generate_log(tree_two, most_two)
            else:
                count = count + (x * b)
                log_t = semantics.generate_log(tree_two, x * b)
            for t in log_t:
                result.append(t)
            if x == 1:
                count = count + most_one
                log_a = semantics.generate_log(tree_one, most_one)
            else:
                count = count + ((rounds - (x - 1)) * b)
                log_a = semantics.generate_log(tree_one, (rounds - (x - 1)) * b)
            for a in log_a:
                result.append(a)
            x = x + 1
    else:
        rest_one, rest_two, rounds, b = get_rest_parameter(nu_traces, distribute_type)
        x = 1
        most_one = rest_one + int(round(math.exp(rounds * b)+0.0001))
        most_two = rest_two + int(round(math.exp(rounds * b)+0.0001))
        while x <= rounds:
            if x == rounds:
                log_t = semantics.generate_log(tree_two, most_two)
            else:
                log_t = semantics.generate_log(tree_two,  int(round(math.exp(x * b)+0.0001)))
            for t in log_t:
                result.append(t)
            if x == 1:
                log_a = semantics.generate_log(tree_one, most_one)
            else:
                log_a = semantics.generate_log(tree_one, int(round(math.exp((rounds - (x-1)) * b))))
            for a in log_a:
                result.append(a)
            x = x + 1
    return result


def get_rest_parameter(nu_traces, distribute_type):
    """ Calculation of the best parameters for the gradual drift.

    :param nu_traces: number of traces to be distributed
    :param distribute_type: mathematical type of distribution
    :return:
    """
    rests_one = []
    rests_two = []
    rounds = []
    nu_drift_model_one = int(round((nu_traces / 2) + 0.0001))
    nu_drift_model_two = nu_traces - nu_drift_model_one
    if distribute_type.strip() == 'linear':
        b = 2
        while b < 6:
            hel = 0
            rest_one = 1
            rest_two = 1
            round_l = 0
            while hel + (round_l+1) * b <= nu_drift_model_one:
                round_l = round_l + 1
                hel = hel + round_l * b
                rest_one = nu_drift_model_one - hel
                rest_two = nu_drift_model_two - hel
            b = b + 1
            rests_one.append(rest_one)
            rests_two.append(rest_two)
            rounds.append(round_l)
        return int(round(rests_one[numpy.argmin(rests_one)]+0.0001)), int(round(rests_two[numpy.argmin(rests_one)]+0.0001)), rounds[numpy.argmin(rests_one)], numpy.argmin(rests_one)+2
    else:
        b = 0.5
        while b <= 0.8:
            hel = 0
            rest_one = 1
            rest_two = 1
            round_l = 0
            while hel + int(round(math.exp((round_l+1)*b)+0.0001)) <= nu_drift_model_one:
                round_l = round_l + 1
                hel = hel + int(round(math.exp(round_l*b)+0.0001))
                rest_one = nu_drift_model_one - hel
                rest_two = nu_drift_model_two - hel
            b = b + 0.1
            rests_one.append(rest_one)
            rests_two.append(rest_two)
            rounds.append(round_l)
    return rests_one[numpy.argmin(rests_one)], rests_two[numpy.argmin(rests_one)], rounds[numpy.argmin(rests_one)], (numpy.argmin(rests_one)*0.1)+0.5

"---TESTS---"
# ve_one = generate_specific_trees('simple')
# ve_two = generate_specific_trees('simple')
# log = gradual_drift(200, 0.4, ve_one, 0.5)
# log = gradual_drift()
# xes_exporter.apply(log, "event_log.xes")
# event_log = add_noise(log)
# xes_exporter.apply(event_log, "event_log_noise.xes")
