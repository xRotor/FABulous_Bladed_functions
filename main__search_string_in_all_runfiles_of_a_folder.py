from ANSFAB__Utility import Utility
import numpy as np
from ANSFAB__Utility import Bladed
import os


baseline_folder = r'H:\BladedWS\BottomFixed\DLC_legacy\2B101ref_IEA_Monopile'
baseline_folder = r'H:\BladedWS\BottomFixed\DLC_legacy\2B101ref_IEA_Monopile\ignore__DAT__DLC14_2B101v15MonoIEA_IAG_stall'
baseline_folder = r'H:\BladedWS\BottomFixed\DLC_legacy\2B101ref_IEA_Monopile_new_v2_10min_TS\DLC12_2B101v15MonoIEA_exZ5_flexDamp__new_kaimal_ULS_10min_TS_v2'

search_string = 'WINDF	H:\BladedWS\BottomFixed\DLC_legacy\DLC12windFileNew2_from5to25'
search_string = 'Extreme yaw error of >42 deg registered.'
search_string = '*** WARNING:   Equilibrium conditions could not be found at'

search_file_end = r'.$ME'

Include_Childfolder = True
copy_suspicious_rj_files = True

search_if_all_runs_are_finished = False
search_if_rotor_speed_below = 1 * 2*3.14159265359/60 # 1 rpm
special_search = False




















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
recognized_files_with_string = []
recognized_files_speed_control = []
recognized_files_run_through = []
new_folder = []
special_search_results = []
local_idx = 0
for idx_file, infile in enumerate(infiles):
    #print('evaluating: ', infile)
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
            if not 'DLC51' in infile and not 'DLC6' in infile and not 'DLC23' in infile and not 'DLC22' in infile and not 'DLC14' in infile:
                if min_rotor_speed < search_if_rotor_speed_below:
                    found_speed_abnormality = True
                    print('\n -> slow rotation in run ', infile)
            else:
                if min_rotor_speed > search_if_rotor_speed_below:
                    found_speed_abnormality = True
                    print('\n -> rotation did not stop in run', infile)

            if found_speed_abnormality:
                recognized_files_speed_control.append(run_file)
                if not folder in recognized_folders:
                    recognized_folders.append(folder)

            if special_search:
                if not idx_file:  # only triggered in first round
                    [wspeed_fileEnd, wspeed_idx, wspeed_DIMENS] = Utility().collectTimeSeriesStructureFromBladedFiles(
                        RunFolder=folder, BladedJob=run_file, VariableName='Hub wind speed magnitude')
                    [yaw_err_fileEnd, yaw_err_idx, yaw_err_DIMENS] = Utility().collectTimeSeriesStructureFromBladedFiles(
                        RunFolder=folder, BladedJob=run_file, VariableName='Yaw misalignment')
                wspeed_timeseries = Utility().readTimeSeriesData(RunFolder=folder, BladedJob=run_file,
                                                        fileEnd=wspeed_fileEnd, idx=wspeed_idx, DIMENS=wspeed_DIMENS)
                yaw_err_timeseries = Utility().readTimeSeriesData(RunFolder=folder, BladedJob=run_file,
                                                        fileEnd=yaw_err_fileEnd, idx=yaw_err_idx, DIMENS=yaw_err_DIMENS)
                multipl_TS = []
                for wspeed, yaw_err in zip(wspeed_timeseries, yaw_err_timeseries):
                    multipl_TS.append(abs(wspeed) * abs(yaw_err))
                print('\n', max(multipl_TS), ' = max(wind_speed * yaw_error)')
                special_search_results.append({'windSpeed': np.mean(wspeed_timeseries)})
                special_search_results[-1]['max_multiplied'] = max(multipl_TS, key=abs)
                special_search_results[-1]['max_windSpeed'] = max(wspeed_timeseries, key=abs)
                special_search_results[-1]['max_yawError'] = max(yaw_err_timeseries, key=abs)



        if folder not in new_folder:
            new_folder.append(folder)
            ref_time_end = time_end
            local_idx = idx_file - 1
            print('\nsearching through:', folder, ' ref time length is ', ref_time_end)

        if time_end != ref_time_end:
            if abs(time_end - ref_time_end) > 1: # to exclude close calls
                print('\nsomething is rotten in the depth of run ', infile)
                recognized_files_run_through.append(run_file)
                if not folder in recognized_folders:
                    recognized_folders.append(folder)

        print('\r searching through file number: ', int(idx_file - local_idx), end='')






    else:
        if folder not in new_folder:
            new_folder.append(folder)
            print('searching through:', folder)
        if search_file_end: infile=infile.replace(r'.$PJ', search_file_end)
        infile = open(infile, "r")
        for row in infile:
            for search_string_i, replace_row_i in zip(search_string, replace_row):
                if row.find(search_string_i) != -1:
                    print(' ---> found string: [', search_string_i, '] in', run_file)
                    recognized_files_with_string.append(folder + '\\' + run_file)
                    if not folder in recognized_folders:
                        recognized_folders.append(folder)
                    #print('replacing', row, 'by', replace_row_i)
                    #row = replace_row_i
        infile.close()


if not search_if_all_runs_are_finished:
    print('\nfound string:', search_string, 'in runs:', *recognized_files_with_string, 'in folders:', *recognized_folders, sep='\n')
else:
    print('\n\nsuspicious folders found:', *recognized_folders, sep='\n')
    if recognized_files_run_through:
        print('\nruns possibly not finished:', *recognized_files_run_through, sep='\n->')
    if recognized_files_speed_control:
        print('\nruns possibly with strange rotation speeds:', *recognized_files_speed_control, sep='\n->')


if special_search_results:
    documentation_path = folder + '_' + folder.split('\\')[-2] + '_special_search.csv'
    documentation_path = Utility().writeListDictToCSV(special_search_results, documentation_path)

recognized_files_with_string = [file for file in recognized_files_with_string if not 'ignore_' in file]
if copy_suspicious_rj_files and recognized_files_with_string:
    suspicious_file_folder = baseline_folder + '\\ignore__suspicious_rj_files'
    Utility().createFolderIfNotExcisting(baseline_folder + '\\ignore__suspicious_rj_files')
    from shutil import copyfile
    for recognized_file_with_string in recognized_files_with_string:
        new_file = recognized_file_with_string.replace(baseline_folder, suspicious_file_folder)
        Utility().createFolderIfNotExcisting(new_file.replace(new_file.split('\\')[-1],''))
        copyfile(recognized_file_with_string + '.$PJ', new_file + '.$PJ')
        copyfile(recognized_file_with_string + search_file_end, new_file + search_file_end)