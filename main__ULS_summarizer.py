from ANSFAB__Utility import Utility
from config import k_steel, k_composite
from statistics import mean
from copy import copy


documentation_path = r'H:\BladedWS\BottomFixed\DLC_legacy\ExtremeDLCs_2B101teeter\ExtremeDLCs_2B101teeter__2023_09_14___ULS_evaluation.csv'
documentation_path = r'H:\BladedWS\BottomFixed\DLC_legacy\ExtremeDLCs_2B101_ref\ExtremeDLCs_2B101_ref__2023_09_15___ULS_evaluation.csv'
documentation_path = r'H:\BladedWS\BottomFixed\DLC_legacy\ExtremeDLCs_2B101v15_ref\ExtremeDLCs_2B101v15_ref__2023_09_15___ULS_evaluation.csv'
documentation_path = r'H:\BladedWS\BottomFixed\DLC_legacy\ExtremeDLCs_3B_ref\ExtremeDLCs_3B_ref__2023_09_14___ULS_evaluation.csv'
documentation_path = r'H:\BladedWS\FOWTs\DLC_ULS\3B20Volt_v008_baseline\3B20Volt_v008_baseline__2023_11_07___ULS_evaluation.csv'
documentation_path = r'H:\BladedWS\BottomFixed\DLC_legacy\ExtremeDLCs_2B101v18teeter_brake4rpm_IAG_noImbal\\ExtremeDLCs_2B101v18teeter_brake4rpm_IAG_noImbal__2023_11_27___ULS_evaluation_summary.csv'

# partial safety factor. Note: DLC2.2 is stuck pitch, but has often been falsely labeled as DLC2.1
PSF_dict = {'DLC13': 1.35, 'DLC14': 1.35, 'DLC15': 1.35, 'DLC16': 1.35, 'DLC22': 1.10, 'DLC23': 1.35, 'DLC51': 1.35,
            'DLC61': 1.35, 'DLC62': 1.10, 'DLC63': 1.35, 'DEFAULT': 1.35, 'DLC12': 1.25}

search_for_ULS_among_blades = True




























def ULS_checker(key, ULS, ULS_jobname, ULS_check, job_name):
    PSF = PSF_dict.get('DLC'+job_name.split('DLC')[-1][0:2])
    if not PSF:
        print('   ---> could not find DLC'+job_name.split('DLC')[-1][0:2], 'in', PSF_dict, ' Will use default value.')
        PSF = PSF_dict.get('DEFAULT')
    if key.find('AMAX') != -1:
        if abs(ULS) < abs(ULS_check):
            ULS = ULS_check
            ULS_jobname = job_name
    elif key.find('MAX') != -1:
        if ULS < ULS_check:
            ULS = ULS_check
            ULS_jobname = job_name
    elif key.find('MIN') != -1:
        if ULS > ULS_check:
            ULS = ULS_check
            ULS_jobname = job_name
    else:  # ULS:
        ULS_check = ULS_check * PSF
        if abs(ULS) < abs(ULS_check):
            ULS = ULS_check
            ULS_jobname = job_name
    return [ULS, ULS_jobname]


results_list_dict = Utility().readListDictFromCSV(documentation_path)
ULS_summary_list_dict = []
for legend in ['DLC', 'run', 'ULS']:
    ULS_summary_list_dict.append({documentation_path.split('\\')[-1]:legend})
keys = list(results_list_dict[0].keys())[1:]
for key_idx, key in enumerate(keys):
    ULS = float(results_list_dict[0].get(key))
    ULS_jobname = results_list_dict[0].get(list(results_list_dict[0].keys())[0])
    seed_nmbr_memory = []
    seed_ULS_memory = []
    run_name_details = ''
    for idx, result_dict in enumerate(results_list_dict):
        job_name_key = list(result_dict.keys())[0]
        job_name = result_dict.get(job_name_key).split('\\')[-1].split('.')[0]
        local_ULS = float(result_dict.get(key))
        found_seed = False
        for seed_identifier in ['_s', '_azi']:
            if job_name.find(seed_identifier) != -1:
                seed_nmbr = job_name.split(seed_identifier)[-1]  # [0:3]
                seed_name_idx = job_name.index(seed_identifier + seed_nmbr)
                if seed_nmbr.isnumeric():
                    found_seed = True
                    if (seed_nmbr in seed_nmbr_memory or run_name_details != job_name[0:seed_name_idx]) and seed_ULS_memory:
                        mean_ULS_memory = mean(seed_ULS_memory)
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

    DLC_number = ULS_jobname.split('DLC')[-1][0:2]
    DLC_name = 'DLC' + DLC_number[0] + '.' + DLC_number[1]
    print(key, 'ULS is', ULS, 'for run', ULS_jobname)
    # ULS_summary_list_dict.append({job_name_key:ULS_jobname, 'DLC': DLC_name, 'Load': key, 'ULS': ULS})
    ULS_summary_list_dict[0][key] = DLC_name
    ULS_summary_list_dict[1][key] = ULS_jobname
    ULS_summary_list_dict[2][key] = ULS

print(ULS_summary_list_dict)




if search_for_ULS_among_blades:
    # search for the maximum among all blades
    ULS_check_among_blades_indexes = []
    ULS_check_among_blades_indexes_blacklist = []
    for key_idx, key in enumerate(keys):
        if key.find('Blade') != -1 and not key_idx in ULS_check_among_blades_indexes_blacklist:
            ULS_check_among_blades_indexes.append([key_idx])
            for blade_number in range(2, 4, 1):
                search_key = key.replace('1', str(blade_number))
                for check_key_idx, check_key in enumerate(keys):
                    if search_key == check_key:
                        ULS_check_among_blades_indexes[-1].extend([check_key_idx])
                        ULS_check_among_blades_indexes_blacklist.append(check_key_idx)

    for ULS_check_among_blades_index in ULS_check_among_blades_indexes:
        if len(ULS_check_among_blades_index) > 1:   # check whether there are other blade ULS to find highest
            first_index = ULS_check_among_blades_index[0]
            first_key = keys[first_index]
            change_key = keys[first_index].replace('1', 'all')
            DLC_name = ULS_summary_list_dict[0].get(keys[first_index])
            ULS_jobname = ULS_summary_list_dict[1].get(keys[first_index])
            ULS = ULS_summary_list_dict[2].get(keys[first_index])
            for check_blade_index in ULS_check_among_blades_index[1:]:  # list starts from second value
                check_ULS = ULS_summary_list_dict[2].get(keys[check_blade_index])
                if change_key.find('MIN') != -1:
                    if ULS > check_ULS:
                        UlS = copy(check_ULS)
                        DLC_name    = ULS_summary_list_dict[0].get(keys[check_blade_index])
                        ULS_jobname = ULS_summary_list_dict[1].get(keys[check_blade_index])
                else:  # accounts for AMAX, MAX and ULS
                    if abs(ULS) < abs(check_ULS):
                        ULS = copy(check_ULS)
                        DLC_name = ULS_summary_list_dict[0].get(keys[check_blade_index])
                        ULS_jobname = ULS_summary_list_dict[1].get(keys[check_blade_index])

            # update the summary dictionaries
            ULS_summary_list_dict[0][first_key] = copy(DLC_name)
            ULS_summary_list_dict[1][first_key] = copy(ULS_jobname)
            ULS_summary_list_dict[2][first_key] = copy(ULS)

            ULS_summary_list_dict_update = []
            for legend in ['DLC', 'run', 'ULS']:
                ULS_summary_list_dict_update.append({documentation_path.split('\\')[-1]: legend})
            for key_idx, key in enumerate(keys):
                if key == first_key:
                    keys[key_idx] = change_key
                ULS_summary_list_dict_update[0][keys[key_idx]] = ULS_summary_list_dict[0].get(key)
                ULS_summary_list_dict_update[1][keys[key_idx]] = ULS_summary_list_dict[1].get(key)
                ULS_summary_list_dict_update[2][keys[key_idx]] = ULS_summary_list_dict[2].get(key)
            ULS_summary_list_dict = copy(ULS_summary_list_dict_update)

    # shorten dictionary from further blades. Has to be done after the ULS check among the blades.
    for ULS_check_among_blades_index in ULS_check_among_blades_indexes:
        if len(ULS_check_among_blades_index) > 1:
            for check_blade_index in ULS_check_among_blades_index[1:]:
                ULS_summary_list_dict[0].pop(keys[check_blade_index])
                ULS_summary_list_dict[1].pop(keys[check_blade_index])
                ULS_summary_list_dict[2].pop(keys[check_blade_index])








documentation_path = documentation_path.split('.')[0] + '_summary.csv'
Utility().writeListDictToCSV(ULS_summary_list_dict, documentation_path)