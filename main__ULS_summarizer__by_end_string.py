from ANSFAB__Utility import Utility
from config import k_steel, k_composite
from statistics import mean



documentation_path = r'H:\BladedWS\FOWTs\DLC_ULS\DLC6X_idling_pitch_iteration\DLC6X__2B20Volt_v009_idling_pitch_itr__2023_11_10___ULS_evaluation.csv'
documentation_path = r'H:\BladedWS\FOWTs\DLC_ULS\DLC6X_idling_pitch_iteration\DLC6X__3B20Volt_v008_idling_pitch_itr\DLC6X__3B20Volt_v008_idling_pitch_itr__2023_12_03___ULS_evaluation.csv'
documentation_path = r'H:\BladedWS\BottomFixed\DLC_legacy\DLC61__idling_pitch_iteration\3B_ref_IAG_stall__DLC61_idling_pitch_itr\3B_ref_IAG_stall__DLC61_idling_pitch_itr__2023_12_03___ULS_evaluation.csv'

# partial safety factor. Note: DLC2.2 is stuck pitch, but has often been falsely labeled as DLC2.1
PSF_dict = {'DLC13': 1.35, 'DLC14': 1.35, 'DLC15': 1.35, 'DLC16': 1.35, 'DLC22': 1.10, 'DLC23': 1.35, 'DLC51': 1.35,
            'DLC61': 1.35, 'DLC62': 1.10, 'DLC63': 1.35, 'DEFAULT': 1.35}





endString = '_pit'
























def ULS_checker(key, ULS, ULS_jobname, ULS_check, job_name):
    PSF = PSF_dict.get('DLC'+job_name.split('DLC')[-1][0:2])
    if not PSF:
        print('   ---> could not find DLC'+job_name.split('DLC')[-1][0:2], 'in', PSF_dict, ' Will use default value.')
        PSF = PSF_dict.get('DEFAULT')
    ULS_check = ULS_check * PSF
    if key.find('MAX') != -1:
        if ULS < ULS_check:
            ULS = ULS_check
            ULS_jobname = job_name
    elif key.find('MIN') != -1:
        if ULS > ULS_check:
            ULS = ULS_check
            ULS_jobname = job_name
    else:
        if abs(ULS) < abs(ULS_check):
            ULS = ULS_check
            ULS_jobname = job_name
    return [ULS, ULS_jobname]

results_list_dict = Utility().readListDictFromCSV(documentation_path)
ULS_summary_list_dict = []
ULS_iteration_summary_list_dict = []
for legend in ['DLC', 'run', 'ULS']:
    ULS_summary_list_dict.append({documentation_path.split('\\')[-1]:legend})
for key_idx, key in enumerate(list(results_list_dict[0].keys())[1:]):
    ULS = float(results_list_dict[0].get(key))
    ULS_jobname = results_list_dict[0].get(list(results_list_dict[0].keys())[0])
    seed_nmbr_memory = []
    seed_ULS_memory = []
    iteration_identifier_list = []
    iteration_ULS_dict = {}
    run_name_details = ''
    for idx, result_dict in enumerate(results_list_dict):
        job_name_key = list(result_dict.keys())[0]
        job_name = result_dict.get(job_name_key).split('\\')[-1].split('.')[0]
        local_ULS = float(result_dict.get(key))

        iteration_identifier = job_name.split(endString)[-1]
        if not iteration_identifier in iteration_identifier_list:
            iteration_identifier_list.append(iteration_identifier)
            iteration_ULS_dict[iteration_identifier] = local_ULS
            iteration_ULS_dict[iteration_identifier + '_JOBNAME'] = job_name

        else:
            [ULS, ULS_jobname] = ULS_checker(key=key, ULS=iteration_ULS_dict.get(iteration_identifier), ULS_jobname=iteration_ULS_dict.get(iteration_identifier + '_JOBNAME'), ULS_check=local_ULS,
                                                 job_name=result_dict.get(job_name_key))
            iteration_ULS_dict[iteration_identifier] = ULS
            iteration_ULS_dict[iteration_identifier + '_JOBNAME'] = ULS_jobname


    for iteration_identifier in iteration_identifier_list:
        iteration_ULS = iteration_ULS_dict.get(iteration_identifier)
        if abs(ULS) >= abs(iteration_ULS):
            ULS = iteration_ULS
            ULS_jobname = iteration_ULS_dict.get(iteration_identifier + '_JOBNAME')



    '''
        found_seed = False
        for seed_identifier in ['_s', '_azi', '_pit']:
            if job_name.find(seed_identifier) != -1:
                seed_nmbr = job_name.split(seed_identifier)[-1]  # [0:3]
                seed_name_idx = job_name.index(seed_identifier + seed_nmbr)
                if seed_nmbr.isnumeric():
                    found_seed = True
                    if (seed_nmbr in seed_nmbr_memory or run_name_details != job_name[0:seed_name_idx]) and seed_ULS_memory:
                        mean_ULS_memory = mean(seed_ULS_memory)
                        mean_ULS_memory = min(seed_ULS_memory)

                        [ULS, ULS_jobname] = ULS_checker(key=key, ULS=ULS, ULS_jobname=ULS_jobname,
                                                         ULS_check=mean_ULS_memory,job_name=job_name_memory)
                        seed_nmbr_memory = []  # = [seed_nmbr]
                        seed_ULS_memory = []  # = [local_ULS]

                    seed_nmbr_memory.append(seed_nmbr)
                    seed_ULS_memory.append(local_ULS)

        if not found_seed and idx:
            if seed_ULS_memory:
                mean_ULS_memory = mean(seed_ULS_memory)
                [ULS, ULS_jobname] = ULS_checker(key=key, ULS=ULS, ULS_jobname=ULS_jobname, ULS_check=mean_ULS_memory,
                                                 job_name=job_name_memory)
                seed_nmbr_memory = []  # = [seed_nmbr]
                seed_ULS_memory = []  # = [local_ULS]

            [ULS, ULS_jobname] = ULS_checker(key=key, ULS=ULS, ULS_jobname=ULS_jobname, ULS_check=local_ULS,
                                             job_name=result_dict.get(job_name_key))

        run_name_details = job_name[0:seed_name_idx]
        job_name_memory = result_dict.get(job_name_key)

    if found_seed:
        mean_ULS_memory = mean(seed_ULS_memory)
        [ULS, ULS_jobname] = ULS_checker(key=key, ULS=ULS, ULS_jobname=ULS_jobname, ULS_check=mean_ULS_memory,
                                         job_name=job_name_memory)
    '''



    # save maximum of each load category into a summary dictionary
    DLC_number = ULS_jobname.split('DLC')[-1][0:2]
    DLC_name = 'DLC' + DLC_number[0] + '.' + DLC_number[1]
    print(key, 'ULS is', ULS, 'for run', ULS_jobname)
    # ULS_summary_list_dict.append({job_name_key:ULS_jobname, 'DLC': DLC_name, 'Load': key, 'ULS': ULS})
    ULS_summary_list_dict[0][key] = DLC_name
    ULS_summary_list_dict[1][key] = ULS_jobname
    ULS_summary_list_dict[2][key] = ULS

    # create a longer results dictionary to check the propagation of the iterated value in graphs
    if not ULS_iteration_summary_list_dict:  # fill list in first round
        for iteration_identifier in iteration_identifier_list:
            ULS_iteration_summary_list_dict.append({documentation_path.split('\\')[-1]: iteration_identifier})
    for itr_idx, iteration_identifier in enumerate(iteration_identifier_list):
        iteration_ULS = iteration_ULS_dict.get(iteration_identifier)
        ULS_iteration_summary_list_dict[itr_idx][key] = iteration_ULS



print(ULS_summary_list_dict)


documentation_path_summary = documentation_path.split('.')[0] + '_summary.csv'
Utility().writeListDictToCSV(ULS_summary_list_dict, documentation_path_summary)

documentation_path_iter_overview = documentation_path.split('.')[0] + '_itr_overview.csv'
Utility().writeListDictToCSV(ULS_iteration_summary_list_dict, documentation_path_iter_overview)
