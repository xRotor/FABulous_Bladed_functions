This repository contains many Python functions for pre- or post-processing wind turbine simulation project files or time series from DNV's Bladed. 

Typical pre-processing tasks are the manipulation of simulation project files to extend the possibilities of Bladed's multi-setup and facilitate larger adaptions by, e.g., cloning a full set of design load cases with specific parameters (main__replace_string_in_all_runfiles_of_a_folder.py) or cloning a set of load case settings to a desired turbine model (main__large_PRJ_files_copy_n_adapt_by_baselinefiles.py). Possible are as well software-in-the-loop optimizations of specific control or model parameters that include the manipulation of run files, starting bladed simulations, evaluating simulations, and updating parameters for new iterations.

Typical post-processing tasks are the evaluation of time series from Bladed simulations for fatigue and ultimate loads. The main script might be [main__evaluateSpecificFolders.py], which handles the pre-settings from [config.py] and calculates damage equivalent loads for materials, dynamic equivalent loads for bearings, and some performance indicators for [search_kind='FLS'], as well as ultimate loads of complete sets of design load case simulations for [search_kind='ULS']. Please be careful that the levelizing after the evaluation to the respecting wind velocities or DLC's can handle your run_naming. The concept used here is the token 'DLC' + number of DLC without the dot (e.g. DLC 1.2 as 'DLC12') the wind speed (e.g. for 14 m/s as '_14mps') and the seed with three digits (seed 440 as '_s440'). Or change the functions how ever it serves you well.

There are plenty more functionalities. It is not a sorted and well documented library, but I hope that reading through the scripts will clarify the usage and intention and serves as a basis for own Bladed pre- and post-processing. 

Don't hesitate to ask if there are any questions.

Fabian
