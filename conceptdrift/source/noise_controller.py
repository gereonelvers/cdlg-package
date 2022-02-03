import copy

from conceptdrift.source.control_flow_controller import evolve_tree_randomly_gs
from conceptdrift.source.event_log_controller import length_of_log


def add_noise_doc(event_log, tree, pro_noise, type_noise, start_noise, end_noise):
    """ Introduction of noise into an event log for text file conceptdrift

    :param event_log: event log
    :param tree: process tree for noise conceptdrift
    :param pro_noise: proportion of noise in sector
    :param type_noise: type of noise (i.e. random or changed)
    :param start_noise: start point of noise
    :param end_noise: end point of noise
    :return: event log with noise
    """
    nu_traces = int(
        round(((length_of_log(event_log) * end_noise) - (
                length_of_log(event_log) * start_noise)) * pro_noise + 0.0001))
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
    return include_noise_in_log(event_log, log_noise, start_noise, end_noise)


def add_noise_gs(event_log, tree, pro_noise, type_noise, start_noise, end_noise):
    """ Introduction of noise into an event log for text file conceptdrift

    :param event_log: event log
    :param tree: process tree for noise conceptdrift
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


