import copy
import csv
import os
import datetime
from random import randint, uniform
import pathlib

from pm4py.objects.log.exporter.xes import exporter as xes_exporter
from pm4py.objects.process_tree.exporter import exporter as ptml_exporter

from conceptdrift.drifts.gradual import gradual_drift
from conceptdrift.drifts.incremental import incremental_drift_gs
from conceptdrift.drifts.recurring import recurring_drift
from conceptdrift.drifts.sudden import sudden_drift
from conceptdrift.source.evolution import evolve_tree_randomly_gs
from conceptdrift.source.event_log_controller import add_duration_to_log, get_timestamp_log
from conceptdrift.source.noise import add_noise_gs
from conceptdrift.source.process_tree_controller import generate_specific_trees


def generate_logs(num_logs=50, num_traces=1000, drifts=['sudden', 'gradual', 'recurring', 'incremental'], drift_area=[0.2, 0.8], pro_random_evolution=[0.2, 0.6], noise=[0, 0.1], model=generate_specific_trees('middle'), filepath=str(pathlib.Path().resolve())):
    """Generation of a set of event logs with different drifts, a corresponding CSV file and respective text files

    :param num_logs: number of event logs
    :param num_traces: number of traces in the event logs
    :param drifts: drift types in list as strings
    :param drift_area: drift area (i.e. start and end point of random drift range) as a range in list
    :param noise: possible proportion of noise in the event log as a range in list
    :param pro_random_evolution: possible proportion of activities to be affected by the random change as a range in list
    :param model: process model as process tree
    :param filepath: file path where the event logs are to be saved
    """

    if not os.path.exists(filepath+'/gold_standard'):
        os.makedirs(filepath+'/gold_standard')
    with open(filepath+'/gold_standard/gold_standard.csv', 'w', newline='') as log_file:
        writer = csv.writer(log_file)
        writer.writerow(["Event Log", "Drift Perspective", "Drift Type", "Drift Specific Information", "Drift Start Timestamp", "Drift End Timestamp", "Noise Proportion", "Activities Added", "Activities Deleted", "Activities Moved"])
        for i in range(num_logs):
            parameters = "number of traces: "+str(num_traces)
            drift = drifts[randint(0, len(drifts)-1)].strip()
            drift_area_one = round(uniform(drift_area[0], (drift_area[0]+0.8*drift_area[1]-drift_area[0])), 2)
            drift_area_two = round(uniform(drift_area_one + (drift_area[1]-drift_area[0]) * 0.2, drift_area[1]), 2)
            if len(pro_random_evolution) == 1:
                ran_evolve = round(pro_random_evolution[0], 2)
            else:
                ran_evolve = round(uniform(pro_random_evolution[0], pro_random_evolution[1]), 2)
            drift_tree = copy.deepcopy(model)
            if drift != 'incremental':
                tree_two, deleted_acs, added_acs, moved_acs = evolve_tree_randomly_gs(drift_tree, ran_evolve)
            if drift == 'sudden':
                event_log = sudden_drift(num_traces, drift_area_one, model, tree_two)
                parameters += "; drift: sudden; change point: "+str(drift_area_one) + "; random evolution: "+str(ran_evolve)
                dr_s = "N/A"
            elif drift == 'gradual':
                ra = randint(0, 1)
                if ra == 0:
                    gr_type = 'linear'
                    dr_s = 'linear distribution'
                else:
                    gr_type = 'exponential'
                    dr_s = 'exponential distribution'
                event_log = gradual_drift(num_traces, drift_area_one, drift_area_two, gr_type, model, tree_two)
                parameters += "; drift: gradual; start point: "+str(drift_area_one)+"; end point: "+str(drift_area_two)+"; distribution: "+gr_type + "; random evolution: "+str(ran_evolve)
            elif drift == 'recurring':
                ran_odd = [3, 5]
                pro_first = round(uniform(0.3, 0.7), 2)
                if drift_area_one > 0 and drift_area_two != 1:
                    ra = randint(0, 1)
                    sea_cha = ran_odd[ra]
                    dr_s = str(sea_cha)+" seasonal changes"
                else:
                    sea_cha = randint(1, 6)
                    dr_s = str(sea_cha)+" seasonal changes"
                event_log = recurring_drift(num_traces, drift_area_one, drift_area_two, sea_cha, pro_first, model, tree_two)
                parameters += "; drift: recurring; start point: "+str(drift_area_one)+"; end point: "+str(drift_area_two)+"; seasonal changes: "+str(sea_cha)+"; proportion initial version: "+str(pro_first) + "; random evolution: "+str(ran_evolve)
            elif drift == 'incremental':
                num_models = randint(2, 5)
                ran_in_evolve = round(ran_evolve/num_models, 2)
                event_log, deleted_acs, added_acs, moved_acs = incremental_drift_gs(model, drift_area_one, drift_area_two, num_traces, num_models, ran_in_evolve)
                dr_s = str(num_models) + " evolving versions"
                parameters += "; drift: incremental; start point: "+str(drift_area_one)+"; end point: "+str(drift_area_two) + "; number evolving versions: " + str(num_models) + "; random evolution per model: "+str(ran_in_evolve)
            noise_prop = 0
            noise_ha = True
            if noise != 0:
                noise_prop = round(uniform(noise[0], noise[1]), 4)
                if noise_prop != 0:
                    ran_no = randint(0, 1)
                    if ran_no == 0:
                        event_log, noise_ha = add_noise_gs(event_log, model, noise_prop, 'changed_model', 0, 1)
                    else:
                        event_log, noise_ha = add_noise_gs(event_log, model, noise_prop, 'random_model', 0, 1)
            if not noise_ha:
                noise_prop = 0.0
            date = datetime.datetime.strptime('20/8/3 8:0:0', '%y/%d/%m %H:%M:%S')
            add_duration_to_log(event_log, date, 1, 14000)
            start_drift = get_timestamp_log(event_log, num_traces, drift_area_one)
            if drift == 'sudden':
                end_drift = "N/A"
            else:
                end_drift = str(get_timestamp_log(event_log, num_traces, drift_area_two)) + " (" + str(drift_area_two) + ")"
            data = "event log: "+"event_log_"+str(i)+"; drift perspective: control-flow; drift type: "+drift+"; drift specific information: "+dr_s+"; drift start timestamp: "+str(start_drift)+" (" + str(drift_area_one) + "); drift end timestamp: "+end_drift+"; noise proportion: "+str(noise_prop)+"; activities added: "+str(added_acs)+"; activities deleted: "+str(deleted_acs)+"; activities moved: "+str(moved_acs)
            event_log.attributes['drift info'] = data
            xes_exporter.apply(event_log, filepath+"/gold_standard/event_log_"+str(i)+".xes")
            writer.writerow(["event_log_"+str(i), "control-flow", drift, dr_s, start_drift, end_drift, noise_prop, added_acs, deleted_acs, moved_acs])
            file_object = open(filepath+"/gold_standard/event_log_"+str(i)+".txt", 'w')
            file_object.write("--- USED PARAMETERS ---\n")
            file_object.write(parameters+"\n\n")
            file_object.write("--- DRIFT INFORMATION ---\n")
            file_object.write(data)
            file_object.close()
    ptml_exporter.apply(model, filepath + "/gold_standard/initial_version.ptml")
