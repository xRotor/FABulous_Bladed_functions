from ANSFAB__Utility import Utility
from statistics import mean
from copy import copy
import math


documentation_path = r'H:\BladedWS\FOWTs\DLC_ULS\2B20Volt_v009_baseline_IAG_stall__teeter_v4__teeterStopAt4rpm\2B20Volt_v009_baseline_IAG_stall__teeter_v4__teeterStopAt4rpm__2023_11_15___ULS_select_no_DLC61_evaluation_v2.csv'
documentation_path = r'H:\BladedWS\FOWTs\DLC_ULS\3B20Volt_v008_baseline_IAG_stall_v2\3B20Volt_v008_baseline_IAG_stall_v2__2024_03_13___ULS_selected_evaluation.csv'
documentation_path = r'H:\BladedWS\FOWTs\DLC_ULS\3B20Volt_2B_v009_baseline_IAG_stall_v2\3B20Volt_2B_v009_baseline_IAG_stall_v2__2024_03_16___ULS_evaluation.csv'

# partial safety factor. Note: DLC2.2 is stuck pitch, but has often been falsely labeled as DLC2.1
PSF_dict = {'DLC13': 1.35, 'DLC14': 1.35, 'DLC15': 1.35, 'DLC16': 1.35, 'DLC22': 1.10, 'DLC23': 1.35, 'DLC51': 1.35,
            'DLC61': 1.35, 'DLC62': 1.10, 'DLC63': 1.35, 'DEFAULT': 1.35, 'DLC12': 1.25, 'DLC21': 1.10}

search_for_ULS_among_blades = True

seed_identifiers = ['_s', '_azi']























class BladedPostProcess:
    # searches for ULS by the given parameters
    def ULS_checker(self, key, ULS, ULS_jobname, ULS_check, job_name):
        PSF = PSF_dict.get('DLC'+job_name.split('DLC')[-1][0:2])
        # print('PSF', PSF, job_name, key, ULS, ULS_check * PSF)
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


    def ULS_DLCs_evaluation_summarizer(self, documentation_path):
        # reads in the evaluation of all runs:
        results_list_dict = Utility().readListDictFromCSV(documentation_path)
        keys = list(results_list_dict[0].keys())[1:]
        job_name_key = list(results_list_dict[0].keys())[0]

        # filter out runs that should not be evaluated in the ULS DLC summarizer
        results_list_dict = [results_dict for results_dict in results_list_dict if not results_dict.get(job_name_key).find('ignore__') != -1]
        results_list_dict = [results_dict for results_dict in results_list_dict if not 'DLC12' in results_dict.get(job_name_key) or 'ULS' in results_dict.get(job_name_key)]

        # sort the list alphabetically by the run names in the first column. It's important to avoid seed group confusions:
        results_list_dict = sorted(results_list_dict, key=lambda d: d[job_name_key])

        # calculate the mean of all seed based runs for each key
        seed_filter_list = []   # gets filled with the int values for 0 if it is a seed run, 1 if it is not a seed run and a number > 1 for the amount of seeds placed at the last seed run
        seed_nmbr_memory = []
        job_name_details = ''
        seed_name_idx = -1
        for idx, result_dict in enumerate(results_list_dict):
            job_name = result_dict.get(job_name_key).split('\\')[-1].split('.')[0]
            found_seed = False
            for seed_identifier in seed_identifiers:  # ['_s', '_azi']:
                if job_name.find(seed_identifier) != -1:
                    # seed_nmbr = job_name.split(seed_identifier)[-1].split('_')[0]  # .split('.')[0]  # [0:3]
                    for possible_seed_nmbr in job_name.split(seed_identifier)[1:]:
                        possible_seed_nmbr = possible_seed_nmbr.split('_')[0]
                        if possible_seed_nmbr.isnumeric():  # necessary to ensure that a run name with e.g. "_stall" at the end is not mistaken as a (wrong) seed number
                            found_seed = True
                            seed_name_idx = job_name.index(seed_identifier + possible_seed_nmbr)
                            if (possible_seed_nmbr in seed_nmbr_memory or job_name_details != job_name[0:seed_name_idx]) and seed_nmbr_memory:  # checks whether a new azimuth or seed set has been started OR a new set of DLCs has been started AND if it might be the first round.
                                seed_filter_list[-1] = len(seed_nmbr_memory)  # if the length of the seed memory is only 1, then it is a false friend and counts as non seed run
                                seed_nmbr_memory = []
                            seed_nmbr_memory.append(possible_seed_nmbr)
            if found_seed:
                seed_filter_list.append(0)
            else:
                if seed_nmbr_memory:  # important if a group of seeds is followed by a non seeded run.
                    seed_filter_list[-1] = len(seed_nmbr_memory)  # if the length of the seed memory is only 1, then it is a false friend and counts as non seed run
                    seed_nmbr_memory = []
                seed_filter_list.append(1)
            # remember the basic run name without the seed end to check whether a new seed run group has been started:
            job_name_details = job_name[0:seed_name_idx]

        if found_seed:  # if there is a seed run group at the end, the amount of seeds does not get captured
            seed_filter_list[-1] = len(seed_nmbr_memory)

        # helps to check whether all seeds have been found correctly:
        # for idx, result_dict in enumerate(results_list_dict):
        #     print(seed_filter_list[idx], result_dict.get(job_name_key).split('\\')[-1].split('.')[0])





        ULS_summary_list_dict = []
        for key_idx, key in enumerate(keys):
            summary_idx = 0
            first_ULS = True   # use as trigger in each first round
            for idx, result_dict in enumerate(results_list_dict):
                job_name = result_dict.get(job_name_key).split('\\')[-1].split('.')[0]
                job_name = result_dict.get(job_name_key).split('.')[0]
                local_ULS = float(result_dict.get(key))
                DLC_number = job_name.split('DLC')[-1][0:2]

                if seed_filter_list[idx]:
                    if seed_filter_list[idx] == 1:
                        ULS_to_check = local_ULS
                    else:
                        ULS_seed_group = [float(results_dict2.get(key)) for results_dict2 in results_list_dict[idx - seed_filter_list[idx] + 1:idx+1]]
                        ULS_to_check = math.copysign(mean([abs(ULS_seed) for ULS_seed in ULS_seed_group]), max(ULS_seed_group))
                    if first_ULS:  # set first reference values for next round.
                        first_ULS = False
                        ULS = ULS_to_check
                        ULS_jobname = job_name
                    [ULS, ULS_jobname] = self.ULS_checker(key=key, ULS=ULS, ULS_jobname=ULS_jobname,
                                                     ULS_check=ULS_to_check, job_name=job_name)

                try:  # get next DLC number if list index is not out of range. Otherwise set string to empty
                    next_DLC_number = results_list_dict[idx+1].get(job_name_key).split('\\')[-1].split('.')[0].split('DLC')[-1][0:2]
                except:
                    next_DLC_number = ''
                if next_DLC_number != DLC_number:
                    if key_idx == 0:
                        DLC_name = 'DLC' + DLC_number[0] + '.' + DLC_number[1]
                        ULS_summary_list_dict.append({'DLC': DLC_name})

                    # old: ULS_summary_list_dict[summary_idx][key] = ULS
                    # reorder the list and fill the ULS value in between the names:
                    items = list(ULS_summary_list_dict[summary_idx].items())
                    items.insert(key_idx+1, (key, ULS))
                    ULS_summary_list_dict[summary_idx] = dict(items)

                    ULS_summary_list_dict[summary_idx][key+'_run_name'] = ULS_jobname
                    summary_idx += 1
                    first_ULS = True  # triggers renewing the reference ULS


        print(ULS_summary_list_dict)

        Utility().writeListDictToCSV(ULS_summary_list_dict, documentation_path.split('.')[0] + '_summary_allDLC_allBlades.csv')


        if search_for_ULS_among_blades:
            # search for the maximum among all blades
            ULS_check_among_blades_indexes_list = []
            ULS_check_among_blades_indexes_blacklist = []
            for key_idx, key in enumerate(keys):
                if key.find('Blade') != -1 and not key_idx in ULS_check_among_blades_indexes_blacklist:
                    ULS_check_among_blades_indexes_list.append([key_idx])
                    for blade_number in range(2, 4, 1):
                        search_key = key.replace('1', str(blade_number))
                        for check_key_idx, check_key in enumerate(keys):
                            if search_key == check_key:
                                ULS_check_among_blades_indexes_list[-1].extend([check_key_idx])
                                ULS_check_among_blades_indexes_blacklist.append(check_key_idx)

            for ULS_check_among_blades_indexes in ULS_check_among_blades_indexes_list:
                if len(ULS_check_among_blades_indexes) > 1:   # check whether there are other blade ULS to find highest
                    first_index = ULS_check_among_blades_indexes[0]
                    first_key = keys[first_index]
                    for list_idx, ULS_summary_dict in enumerate(ULS_summary_list_dict):
                        ULS = ULS_summary_dict.get(keys[first_index])
                        ULS_jobname = ULS_summary_dict.get(keys[first_index] + '_run_name')
                        ULS_blade_number = '1'
                        for blade_number, check_blade_index in enumerate(ULS_check_among_blades_indexes[1:]):  # list starts from second value
                            check_ULS = ULS_summary_dict.get(keys[check_blade_index])
                            job_name = ULS_summary_dict.get(keys[check_blade_index] + '_run_name')
                            # shorten dictionary from further blades and pop out the unnecessary blade positions
                            ULS_summary_list_dict[list_idx].pop(keys[check_blade_index])
                            ULS_summary_list_dict[list_idx].pop(keys[check_blade_index] + '_run_name')
                            if first_key.find('MIN') != -1:
                                if ULS > check_ULS:
                                    UlS = copy(check_ULS)
                                    ULS_jobname = copy(job_name)
                                    ULS_blade_number = str(blade_number+2)
                            else:  # accounts for AMAX, MAX and ULS
                                if abs(ULS) < abs(check_ULS):
                                    ULS = copy(check_ULS)
                                    ULS_jobname = copy(job_name)
                                    ULS_blade_number = str(blade_number+2)

                        # update the summary dictionaries to first blade's position
                        ULS_summary_list_dict[list_idx][first_key] = copy(ULS)
                        ULS_summary_list_dict[list_idx][first_key+'_run_name'] = copy(ULS_jobname) + '___blade_' + ULS_blade_number

                        # convert dictionary in item list:
                        items = list(ULS_summary_list_dict[list_idx].items())
                        # change item that represents the key that has to be changed:
                        index_fist_ULS = list(ULS_summary_list_dict[list_idx]).index(first_key)
                        index_run_name = list(ULS_summary_list_dict[list_idx]).index(first_key+'_run_name')
                        # tuple has to be changed to list to be editable
                        as_list = list(items[index_fist_ULS])
                        as_list[0] = as_list[0].replace('1', 'ALL')
                        items[index_fist_ULS] = tuple(as_list)
                        as_list = list(items[index_run_name])
                        as_list[0] = as_list[0].replace('1', 'ALL')
                        items[index_run_name] = tuple(as_list)
                        # convert the item list back into a dictionary
                        ULS_summary_list_dict[list_idx] = dict(items)

            '''# shorten dictionary from further blades.
            for ULS_check_among_blades_indexes in ULS_check_among_blades_indexes_list:
                if len(ULS_check_among_blades_indexes) > 1:   # check whether there are other blade ULS to find highest
                    for list_idx, ULS_summary_dict in enumerate(ULS_summary_list_dict):
                        for check_blade_index in ULS_check_among_blades_indexes[1:]:  # list starts from second value
                            # pop out the unnecessary blade positions
                            ULS_summary_list_dict[list_idx].pop(keys[check_blade_index])
                            ULS_summary_list_dict[list_idx].pop(keys[check_blade_index] + '_run_name')
            '''

        Utility().writeListDictToCSV(ULS_summary_list_dict, documentation_path.split('.')[0] + '_summary_allDLC.csv')
        return documentation_path

if __name__ == "__main__":
    # executing the function of this is a main function
    BladedPostProcess().ULS_DLCs_evaluation_summarizer(documentation_path)