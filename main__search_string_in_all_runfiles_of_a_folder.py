from ANSFAB__Utility import Utility
import numpy as np
from ANSFAB__Utility import Bladed
import os


baseline_folder = r'H:\BladedWS\BottomFixed\DLC_legacy\2B101ref_IEA_Monopile'

search_string = 'WINDF	H:\BladedWS\BottomFixed\DLC_legacy\DLC12windFileNew2_from5to25'

Include_Childfolder = True


search_if_all_runs_are_finished = True
search_if_rotor_speed_below = 1 * 2*3.14159265359/60 # 1 rpm




















replace_row = ''
if isinstance(search_string, str):
    search_string = [search_string]
    replace_row   = [replace_row]

infiles = []
if Include_Childfolder:
    subfolders = [folder[0] for folder in os.walk(baseline_folder)]
    print('found folders ---> ', subfolders)

    for subfolder in subfolders:
        childfiles = Utility().return_run_files_in_folder(subfolder)
        if childfiles:
            print('found in folder ---> ', subfolder, ' the files --->', childfiles)

            infiles.extend(childfiles)
else:
    #run_files = [path.split('\\')[-1] for path in Utility().return_run_files_in_folder(baseline_folder)]
    infiles.extend(Utility().return_run_files_in_folder(baseline_folder))


#for idx_file, run_file in enumerate(run_files):
#    infile = open(os.path.join(baseline_folder, run_file), "r")
#    outfileName = run_file.replace(old_string, new_string)
#    outfile = open(os.path.join(out_folder, outfileName), "w")
recognized_folders = []
recognized_files_speed_control = []
recognized_files_run_through = []
new_folder = []
local_idx = 0
for idx_file, infile in enumerate(infiles):
    # print('adapting: ', infile)
    run_file = infile.split('\\')[-1].split('.')[0]
    folder = infile.replace(infile.split('\\')[-1],'')

    if search_if_all_runs_are_finished:
        if not idx_file: # only triggered in first round
            [time_fileEnd, time_idx, time_DIMENS] = Utility().collectTimeSeriesStructureFromBladedFiles(
                RunFolder=folder, BladedJob=run_file, VariableName='Time from start of simulation')
        time_timeseries = Utility().readTimeSeriesData(RunFolder=folder, BladedJob=run_file,
                                                fileEnd=time_fileEnd, idx=time_idx, DIMENS=time_DIMENS)
        time_end = time_timeseries[-1] - time_timeseries[0]

        if search_if_rotor_speed_below:
            if not idx_file:  # only triggered in first round
                [rotSpeed_fileEnd, rotSpeed_idx, rotSpeed_DIMENS] = Utility().collectTimeSeriesStructureFromBladedFiles(
                    RunFolder=folder, BladedJob=run_file, VariableName='Rotor speed')
            min_rotor_speed = min(Utility().readTimeSeriesData(RunFolder=folder, BladedJob=run_file,
                                                    fileEnd=rotSpeed_fileEnd, idx=rotSpeed_idx, DIMENS=rotSpeed_DIMENS))
            #print(' minimal rotation speed is:', min_rotor_speed)
            found_speed_abnormality = False
            if min_rotor_speed < search_if_rotor_speed_below and not 'DLC51' in infile and not 'DLC6' in infile:
                found_speed_abnormality = True
                print('\n -> slow rotation in run ', infile)
            elif min_rotor_speed > search_if_rotor_speed_below and ('DLC51' in infile or 'DLC22' in infile or 'DLC21' in infile):
                found_speed_abnormality = True
                print('\n -> rotation did not spot in run in run ', infile)
            elif min_rotor_speed > search_if_rotor_speed_below and 'DLC6' in infile:
                found_speed_abnormality = True
                print('\n -> rotation did not spot in run in run ', infile)

            if found_speed_abnormality:
                recognized_files_speed_control.append(run_file)
                if not folder in recognized_folders:
                    recognized_folders.append(folder)


        if folder not in new_folder:
            new_folder.append(folder)
            ref_time_end = time_end
            local_idx = idx_file - 1
            print('\nsearching through:', folder, ' ref time length is ', ref_time_end)

        if time_end != ref_time_end:
            print('\nsomething is rotten in the depth of run ', infile)
            recognized_files_run_through.append(run_file)
            if not folder in recognized_folders:
                recognized_folders.append(folder)

        print('\r searching through file number: ', int(idx_file - local_idx), end='')






    else:
        infile = open(infile, "r")
        for row in infile:
            for search_string_i, replace_row_i in zip(search_string, replace_row):
                if row.find(search_string_i) != -1:
                    print('found string in', run_file)
                    if not folder in recognized_folders:
                        recognized_folders.append(folder)
                    #print('replacing', row, 'by', replace_row_i)
                    #row = replace_row_i
        infile.close()


if not search_if_all_runs_are_finished:
    print('\nfound string:', search_string, 'in folders:', *recognized_folders, sep='\n')
else:
    print('\n\nsuspicious folders found:', *recognized_folders, sep='\n')
    if recognized_files_run_through:
        print('\nruns possibly not finished:', *recognized_files_run_through, sep='\n->')
    if recognized_files_speed_control:
        print('\nruns possibly with strange rotation speeds:', *recognized_files_speed_control, sep='\n->')





