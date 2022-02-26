import copy

from conceptdrift.source.evolution import evolve_tree_randomly_gs
from conceptdrift.source.event_log_controller import length_of_log, include_noise_in_log, get_timestamp_log
from conceptdrift.source.process_tree_controller import generate_tree
from pm4py.objects.process_tree import semantics


def add_noise(event_log, pro_noise=0.05, start_noise=0, end_noise=1, model=None):
    """ Introduction of noise into an event log

    :param event_log: event log into which noise is introduced
    :param pro_noise: proportion of noise traces occurring in the set sector of the event log
    :param start_noise: Start point of the noise as a proportion of the total number of traces
    :param end_noise: End point of the noise as a proportion of the total number of traces
    :param model: process tree for noise
    :return: event log with noise
    """
    nu_traces = int(
        round(((length_of_log(event_log) * end_noise) - (
                length_of_log(event_log) * start_noise)) * pro_noise + 0.0001))
    if model is not None:
        drift_tree = copy.deepcopy(model)
        drift_tree, a, b, c = evolve_tree_randomly_gs(drift_tree, 0.4)
        log_noise = semantics.generate_log(drift_tree, nu_traces)

        data = "noise proportion: " + str(pro_noise) + "; start point: " + str(
            get_timestamp_log(event_log, len(event_log), start_noise)) + " (" + str(
            start_noise) + "); end point: " + str(get_timestamp_log(event_log, len(event_log), end_noise)) + " (" + str(
            end_noise) + "); noise type: similar"
    else:
        model = generate_tree(
            {'mode': 8, 'min': 6, 'max': 10, 'sequence': 0.25, 'choice': 0.25, 'parallel': 0.25, 'loop': 0.2, 'or': 0,
             'silent': 0, 'duplicate': 0, 'lt_dependency': 0, 'infrequent': 0.25, 'no_models': 10, 'unfold': 10,
             'max_repeat': 10})
        log_noise = semantics.generate_log(model, nu_traces)
        data = "noise proportion: " + str(pro_noise) + "; start point: " + str(
            get_timestamp_log(event_log, len(event_log), start_noise)) + " (" + str(
            start_noise) + "); end point: " + str(get_timestamp_log(event_log, len(event_log), end_noise)) + " (" + str(
            end_noise) + "); noise type: random"
    result = include_noise_in_log(event_log, log_noise, start_noise, end_noise)
    try:
        data_drift = event_log.attributes['drift info']
        result.attributes['drift info'] = data_drift
    except:
        pass
    result.attributes['noise info'] = data
    return result


def add_noise_gs(event_log, tree, pro_noise, type_noise, start_noise, end_noise):
    """ Introduction of noise into an event log for text file

    :param event_log: event log
    :param tree: process tree for noise
    :param pro_noise: proportion of noise in sector
    :param type_noise: type of noise (i.e. random or changed)
    :param start_noise: start point of noise
    :param end_noise: end point of noise
    :return: event log with noise
    """
    nu_traces = int(
        round(((length_of_log(event_log) * end_noise) - (
                length_of_log(event_log) * start_noise)) * pro_noise + 0.0001))
    if nu_traces == 0:
        return event_log, False
    if type_noise == 'changed_model':
        drift_tree = copy.deepcopy(tree)
        drift_tree, a, b, c = evolve_tree_randomly_gs(drift_tree, 0.4)
        log_noise = semantics.generate_log(drift_tree, nu_traces)
    else:
        tree = generate_tree(
            {'mode': 8, 'min': 6, 'max': 10, 'sequence': 0.25, 'choice': 0.25, 'parallel': 0.25, 'loop': 0.2, 'or': 0,
             'silent': 0, 'duplicate': 0, 'lt_dependency': 0, 'infrequent': 0.25, 'no_models': 10, 'unfold': 10,
             'max_repeat': 10})
        log_noise = semantics.generate_log(tree, nu_traces)
    return include_noise_in_log(event_log, log_noise, start_noise, end_noise), True
