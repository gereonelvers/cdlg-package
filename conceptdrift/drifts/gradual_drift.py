import math

import numpy
from pm4py.objects.log.obj import EventLog

from pm4py.objects.process_tree import semantics

from conceptdrift.source.event_log_controller import combine_two_logs


def gradual_drift(tree_one, tree_two, nu_traces, start_point, end_point, distribution_type):
    """ Generation of an event log with a gradual drift

    :param tree_one: initial version of the process tree
    :param tree_two: evolved version of the process tree
    :param nu_traces: number of traces in the log
    :param start_point: start change point of the drift in percentage
    :param end_point: end change point of the drift in percentage
    :param distribution_type: type of distribution of the traces during the drift (linear, exponential)
    :return: event log with gradual drift
    """
    log_before_drift_traces = int(round((start_point * nu_traces) + 0.0001))
    log_after_drift_traces = int(round(((1-end_point)*nu_traces)+0.0001))
    nu_traces_for_drift = nu_traces - log_before_drift_traces - log_after_drift_traces
    log_before_drift = semantics.generate_log(tree_one, log_before_drift_traces)
    log_after_drift = semantics.generate_log(tree_two, log_after_drift_traces)
    log_combined_with_drift = distribute_traces(tree_one, tree_two, distribution_type,
                                                nu_traces_for_drift)
    log_be_one = combine_two_logs(log_before_drift, log_combined_with_drift)
    logs_combined = combine_two_logs(log_be_one, log_after_drift)
    return logs_combined


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