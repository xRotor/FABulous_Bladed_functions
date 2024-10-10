from ANSFAB__Utility import Utility
import os
from shutil import copyfile
import shutil

mainfolder = r'H:\BladedWS\FOWTs\DLC_ULS\\3B20Volt_v008_baseline\DLC15__3B20Volt_v008_baseline_new\\'
#mainfolder = r'H:\BladedWS\FOWTs\DLC_ULS\\3B20Volt_v008_baseline_IAG_stall\DLC15__3B20Volt_v008_baseline_IAG_stall_new\\'
#mainfolder = r'H:\BladedWS\FOWTs\DLC_ULS\\'  # 2B20Volt_v009_baseline\DLC15__2B20Volt_v009_baseline_new\\'


use_task = 2  # Task = 1 => copy important files to safety
              # Task = 2 => check whether prj files in folder have been executed

subfolders = [folder[0].replace('\\\\', '\\') for folder in os.walk(mainfolder)]

if use_task == 1:
    backup_folder = mainfolder[:-2] + r'__backup\\'
    #backup_folder = r'H:\GeneticAlgorithm_Bladed_tuning\\'
    #shutil.copytree(mainfolder, backup_folder)

    # select file extensions for files which should be saved
    safety_file_ends = ['*.dll', '*.txt', '*.$PJ', '*.csv', '*.xlsx', '*.prj', '*.me', '*.dat', '.png', '*.py', '*.log']

    for subfolder in subfolders:
        backup_subfolder = subfolder.replace(mainfolder, backup_folder)
        Utility().createFolderIfNotExcisting(backup_subfolder)
        for file_end in safety_file_ends:
            safety_files = [path.split('\\')[-1] for path in
                            Utility().return_run_files_in_folder(subfolder, fileEnd=file_end)]
            if safety_files:
                for file in safety_files:
                    filepath = os.path.join(subfolder, file)
                    copyfile(filepath, filepath.replace(mainfolder, backup_folder))
                print(safety_files)
        # remove folder if empty
        try:
            os.rmdir(backup_subfolder)
        except:
            pass




elif use_task == 2 or use_task == 3:
    all_folders_are_executed = True
    for subfolder in subfolders:
        project_files = [path.split('\\')[-1].replace(r'.$PJ', '') for path in
                         Utility().return_run_files_in_folder(subfolder, fileEnd='*.$PJ')]
        reference_files = [path.split('\\')[-1].replace(r'.$05', '') for path in
                           Utility().return_run_files_in_folder(subfolder, fileEnd='*.$05')]

        # if project_files == reference_files:
        #     print('All Bladed run files have been executed in folder', subfolder)

        if project_files != reference_files:
            false_alarm = True
            for project_file in project_files:
                if not project_file in reference_files:
                    false_alarm = False
                    print(r'    -----> not executed is', project_file)
                    if use_task == 3:
                        new_subfolder = subfolder.replace(subfolder.split('\\')[-2], subfolder.split('\\')[-2] + '_update')
                        Utility().createFolderIfNotExcisting(new_subfolder)
                        filepath = os.path.join(subfolder, project_file + '.$PJ')
                        filepath_copy = os.path.join(new_subfolder, project_file + '.$PJ')
                        copyfile(filepath, filepath_copy)
            if not false_alarm:
                all_folders_are_executed = False
                print('          -----> in folder', subfolder, '\n')

    if all_folders_are_executed:
        print('All files have been executed in', subfolders)

