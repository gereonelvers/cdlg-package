CDLG: Concept Drift Log Generator
====
Python package for creating concept drifts in event logs, introducing noise into an event log and randomly evolving a process tree to a new version.

About
---
This package contains all essential functions of our approach as described in 
</br>_HERE PAPER_

**This is the package to use the functions for your own project. The actual tool for generating usable event logs with concept drifts can be found [here](https://gitlab.uni-mannheim.de/processanalytics/cdlg_tool).**

Installation
---
**The package requires python >= 3.9**

1. Install via pip: <code>pip install git+https://gitlab.uni-mannheim.de/processanalytics/cdlg-package </code>


Usage
---
Seven main functions are explained below that can be used to generate event logs with specific concept drifts, introduce noise, and modify process trees.

### Generation of drift types

The following functions generate event logs with specific concept drifts, with all drift information stored as an attribute in the event log.

**Sudden drift**

This function generates an event log with a specified sudden drift. If the function is called without parameters, the default values from the table are used.

<code> from conceptdrift.drifts.sudden import generate_log_with_sudden_drift </code><br>
<code> event_log = generate_log_with_sudden_drift(num_traces, change_point, process_tree_one, process_tree_two, change_proportion) </code>

| Parameter         | Meaning                                                                    | Type          | Default |
|-------------------|----------------------------------------------------------------------------|---------------|---------|
| num_traces        | Number of traces in the event log                                          | Integer       | 1000    |
| change_point      | Change point of the drift as a proportion of the total number of traces    | 0 < Float < 1 | 0.5     |
| process_tree_one  | Initial version of the process tree                                        | ProcessTree   | None    |
| process_tree_two  | Evolved version of the process tree                                        | ProcessTree   | None    |
| change_proportion | Proportion of total number of activities to be changed by random evolution | 0 ≤ Float ≤ 1 | 0.2     |
| **return**        | An event log with a sudden drift                                           | EventLog      | N/A     |

_Note:_ If one or no model is used, the change_proportion parameter is used to evolve the original version of the process tree to a new version (i.e. model_two=None). Otherwise, the two passed process model versions are used.
If process_tree_one is None and a process tree is passed for process_tree_two, the function is called as if both process trees are None.


**Gradual drift**

This function generates an event log with a specified gradual drift. If the function is called without parameters, the default values from the table are used.

<code> from conceptdrift.drifts.gradual import generate_log_with_gradual_drift </code> <br>
<code> event_log = generate_log_with_gradual_drift(num_traces, start_point, end_point, distribution_type, process_tree_one, process_tree_two, change_proportion) </code>

| Parameter         | Meaning                                                                       | Type                    | Default  |
|-------------------|-------------------------------------------------------------------------------|-------------------------|----------|
| num_traces        | Number of traces in the event log                                             | Integer                 | 1000     |
| start_point       | Start change point of the drift as a proportion of the total number of traces | 0 ≤ Float < 1           | 0.4      |
| end_point         | End change point of the drift as a proportion of the total number of traces   | start_point < Float ≤ 1 | 0.6      |
| distribution_type | Type of distribution of the traces during the drift [linear, exponential]     | String                  | 'linear' |
| process_tree_one  | Initial version of the process tree                                           | ProcessTree             | None     |
| process_tree_two  | Evolved version of the process tree                                           | ProcessTree             | None     |
| change_proportion | Proportion of total number of activities to be changed by random evolution    | 0 ≤ Float ≤ 1           | 0.2      |
| **return**        | An event log with a gradual drift                                             | EventLog                | N/A      |

_Note:_ If one or no model is used, the change_proportion parameter is used to evolve the original version of the process tree to a new version (i.e. model_two=None). Otherwise, the two passed process model versions are used.
If process_tree_one is None and a process tree is passed for process_tree_two, the function is called as if both process trees are None.


**Recurring drift**

This function generates an event log with a specified recurring drift. If the function is called without parameters, the default values from the table are used.

<code> from conceptdrift.drifts.recurring import generate_log_with_recurring_drift </code><br>
<code> event_log = generate_log_with_recurring_drift(num_traces, start_point, end_point, num_of_seasonal_changes, pro_first_version, process_tree_one, process_tree_two, change_proportion) </code>

| Parameter               | Meaning                                                                          | Type                    | Default |
|-------------------------|----------------------------------------------------------------------------------|-------------------------|---------|
| num_traces              | Number of traces in the event log                                                | Integer                 | 1000    |
| start_point             | Start change point of the drift as a proportion of the total number of traces    | 0 ≤ Float < 1           | 0.0     |
| end_point               | End change point of the drift as a proportion of the total number of traces      | start_point < Float ≤ 1 | 1.0     |
| num_of_seasonal_changes | The number of changes of the model versions in the event log                     | Integer (odd)           | 3       |
| pro_first_version       | Proportion of the traces generated by the initial model version during the drift | 0 < Float < 1           | 0.5     |
| process_tree_one        | Initial version of the process tree                                              | ProcessTree             | None    |
| process_tree_two        | Evolved version of the process tree                                              | ProcessTree             | None    |
| change_proportion       | Proportion of total number of activities to be changed by random evolution       | 0 ≤ Float ≤ 1           | 0.2     |
| **return**              | An event log with a recurring drift                                              | EventLog                | N/A     |

_Note:_ If one or no model is used, the change_proportion parameter is used to evolve the original version of the process tree to a new version (i.e. model_two=None). Otherwise, the two passed process model versions are used.
If process_tree_one is None and a process tree is passed for process_tree_two, the function is called as if both process trees are None. <br>
The parameter pro_first_version indirectly determines the execution length of the seasons of the different process versions. The proportion of traces of the second version during the drift is automatically _1 - pro_first_version_.

**Incremental drift**

This function generates an event log with a specified incremental drift. If the function is called without parameters, the default values from the table are used.

<code> from conceptdrift.drifts.incremental import generate_log_with_incremental_drift </code> <br>
<code> event_log = generate_log_with_incremental_drift(num_versions, traces, change_proportion, process_tree) </code>

| Parameter         | Meaning                                                                                     | Type          | Default                           |
|-------------------|---------------------------------------------------------------------------------------------|---------------|-----------------------------------|
| num_versions      | Number of occurring process tree versions in the event log                                  | Integer       | 4                                 |
| traces            | Number of traces for each version stored in a list (e.g. [300,200,200])                     | List          | None                              |
| change_proportion | Proportion of total number of activities to be changed by random evolution for each version | 0 ≤ Float ≤ 1 | 0.1                               |
| process_tree      | Initial version of the process tree                                                         | ProcessTree   | generate_specific_trees('middle') |
| **return**        | An event log with an incremental drift                                                      | EventLog      | N/A                               |

_Note:_  If the number of traces for each version is not specified, 300 traces of each version will be generated.


### Introduction of noise

This function adds specific noise to an existing event log that must be passed. All noise information is stored as an attribute in the event log.

<code> from conceptdrift.source.noise import add_noise </code><br>
<code> event_log_noise = add_noise(event_log, pro_noise, start_noise, end_noise, process_tree) </code>

| Parameter    | Meaning                                                                                  | Type                    | Default |
|--------------|------------------------------------------------------------------------------------------|-------------------------|---------|
| event_log    | Event log into which noise is introduced                                                 | EventLog                | N/A     |
| pro_noise    | Proportion of noise traces occurring in the set sector of the event log                  | 0 < Float < 0.5         | 0.05    |
| start_noise  | Start point of the noise as a proportion of the total number of traces                   | 0 ≤ Float < 1           | 0.0     |
| end_noise    | End point of the noise as a proportion of the total number of traces                     | start_noise < Float ≤ 1 | 1.0     |
| process_tree | Process tree version which will be changed by 0.4 for the generation of the noise traces | ProcessTree             | None    |
| **return**   | An event log with noise                                                                  | EventLog                | N/A     |

_Note:_ If no model is used, a random process tree is created to generate noise traces from it (i.e. random noise). 
When a process tree is passed, it is changed by 40% through random evolution and is then used to generate the noise traces (i.e. similar noise).

### Random evolution of a process tree

This function changes a passed process tree to a new version. 

<code> from conceptdrift.source.evolution import evolve_tree_randomly </code><br>
<code> new_version = evolve_tree_randomly(process_tree, change_proportion) </code>

| Parameter         | Meaning                                                                | Type          | Default |
|-------------------|------------------------------------------------------------------------|---------------|---------|
| process_tree      | Process tree version to be changed                                     | ProcessTree   | N/A     |
| change_proportion | Proportion of total number of activities to be affected by the changes | 0 < Float ≤ 1 | 0.2     |
| **return**        | Randomly evolved process tree version                                  | ProcessTree   | N/A     |


### Generation of a collection of logs

This function generates a certain number of random event logs with concept drifts and exports them directly to a specified folder.
If the function is called without parameters, the default values from the table are used.

<code> from conceptdrift.generate_collection_of_logs import generate_logs </code><br>
<code> generate_logs(num_logs, num_traces, drifts, drift_area, pro_random_evolution, noise, process_tree, filepath)</code>

| Parameter            | Meaning                                                                                                           | Type             | Default                                           |
|----------------------|-------------------------------------------------------------------------------------------------------------------|------------------|---------------------------------------------------|
| num_logs             | Number of event logs to be generated                                                                              | Integer          | 50                                                |
| num_traces           | Number of traces in the event logs                                                                                | Integer          | 1000                                              |
| drifts               | Required drift types generated in the event logs stored in a list ['sudden', 'recurring','gradual','incremental'] | String-List[1-4] | ['sudden', 'gradual', 'recurring', 'incremental'] |
| drift_area           | Area in the event log in which the drift can occur as a proportion of the total number of traces stored in a list | Float-List[2]    | [0.2, 0.8]                                        |
| pro_random_evolution | Range of proportion of total number of activities to be changed by random evolution stored in a list              | Float-List[2]    | [0.2, 0.6]                                        |
| noise                | Range of proportion of noise occurring in the event log stored in a list                                          | Float-List[2]    | [0.0, 0.1]                                        |
| process_tree         | Initial version of the process tree used for all event logs                                                       | ProcessTree      | generate_specific_trees('middle')                 |
| filepath             | File path to the folder where all data (i.e. event logs) are stored                                               | String           | str(pathlib.Path().resolve()))                    |

_Note:_ the ranges are determined in a list with two float numbers (e.g. [0.2, 0.8]).

### Additional functions

**Export of an event log**

<code> from pm4py.objects.log.exporter.xes import exporter as xes_exporter </code><br>
<code> xes_exporter.apply(event_log, filepath) </code>

**Export of a process tree**

<code> from pm4py.objects.process_tree.exporter import exporter as ptml_exporter </code><br>
<code> ptml_exporter.apply(tree, "running-example.ptml") </code>

**Import of a process model (BPMN/ Petri net/ process tree)**

<code> from conceptdrift.source.process_tree_controller import import_process_model </code><br>
<code> tree = import_process_model(filepath) </code>

**Generation of a random process tree**

<code> from conceptdrift.source.process_tree_controller import generate_specific_trees </code><br>
<code> tree = generate_specific_trees(str_clp='middle') </code>

_Note:_ str_clp can be one of the following values: 'simple', 'middle' or 'complex'.

Reference
---
* [PM4Py](https://pm4py.fit.fraunhofer.de)


 
