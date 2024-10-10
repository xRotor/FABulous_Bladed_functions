from ANSFAB__Utility import Utility
from config import k_steel, k_composite


documentation_path = r'H:\BladedWS\FOWTs\DLC_ULS\2B20Volt_v009_baseline_IAG_stall__teeter_v3\DLC12__2B20Volt_v009_baseline_IAG_stall__teeter\DLC12__2B20Volt_v009_baseline_IAG_stall__teeter_2023_11_16___DEL_evaluation_blade_in_outplane.csv'
documentation_path = r'H:\BladedWS\BottomFixed\DLC_legacy\DLC12\DLC12_3B90_EERA_ref_exZone5_flexDampers_6seeds_Kaimal\DLC12_3B90_EERA_ref_exZone5_flexDampers_6seeds_Kaimal_2023_09_26___DEL_evaluation_blade_in_outplane.csv'

nSeeds = 6
#nSeeds = 1
nYawErrors = 3
#nYawErrors = 1


class BladedPostProcess:
    def DLC12_summarizer(self, documentation_path, nSeeds=6, nYawErrors=3):
        results_list_dict = Utility().readListDictFromCSV(documentation_path)
        wind_speed_list = []
        nmbr_of_run_groups = 0
        nmbr_of_runs_per_groups = 0
        for idx, result_dict in enumerate(results_list_dict):
            if ((idx + 1) / nSeeds).is_integer():
                job_name_key = list(result_dict.keys())[0]
                job_name = result_dict.get(job_name_key)
                for name_section in job_name.split('_'):
                    if name_section.find('mps') != -1:
                        wind_speed = int(name_section.split('.')[0].replace('mps', ''))
                        if wind_speed in wind_speed_list and not nmbr_of_run_groups:
                            nmbr_of_runs_per_groups = int((idx+1)/nSeeds - 1)
                            nmbr_of_run_groups = int(len(results_list_dict)/nSeeds/nmbr_of_runs_per_groups)
                            print('found ', nmbr_of_run_groups, ' groups with ', nmbr_of_runs_per_groups, 'runs split in ', nSeeds, 'seeds each')
                        wind_speed_list.append(wind_speed)
        if not nmbr_of_run_groups:
            nmbr_of_run_groups = 1
            nmbr_of_runs_per_groups = int(len(results_list_dict))

        '''probabilities = []
        for wind_speed in wind_speed_list:
            probabilities.append(Utility().calc_rayleigh_distribution_probability_from_wind_speed(wind_speed))
        '''
        leveled_results_list_dict = []
        for group_idx in range(nmbr_of_run_groups):
            global_run_name = results_list_dict[group_idx*nmbr_of_runs_per_groups*nSeeds].get(job_name_key).split('mps')[0][:-2] + '_all_mps'
            leveled_results_list_dict.append({job_name_key: global_run_name})
            for key in list(results_list_dict[0].keys())[1:]:
                if key.find('DEL') != -1:
                    if key.find('Blade') != -1:
                        k = k_composite
                    if key.find('Tower') != -1:
                        k = k_steel
                elif key.find('max') != -1:
                    k = 0
                else:
                    k = 1
                leveled_value = 0
                for run_idx in range(nmbr_of_runs_per_groups):
                    for seed_idx in range(nSeeds):
                        wind_speed_list_idx = group_idx * nmbr_of_runs_per_groups + run_idx
                        global_index = wind_speed_list_idx * nSeeds + seed_idx
                        local_value = float(results_list_dict[global_index].get(key))
                        probability = Utility().calc_rayleigh_distribution_probability_from_wind_speed(wind_speed_list[wind_speed_list_idx]) / nSeeds
                        if k:
                            leveled_value += pow(local_value, k) * probability
                        else:
                            if leveled_value < local_value:
                                leveled_value = local_value
                if k:
                    leveled_value = pow(leveled_value, 1/k)

                leveled_results_list_dict[-1][key] = leveled_value


        documentation_path = documentation_path.split('.')[0] + '_levelized.csv'
        Utility().writeListDictToCSV(leveled_results_list_dict, documentation_path)



        # reading in a (three) yaw misalignment DELs of each key and calculate the 0deg double weighted mean
        if nYawErrors > 1:
            results_list_dict = Utility().readListDictFromCSV(documentation_path)
            leveled_results_list_dict = []
            leveled_results_list_dict.append({job_name_key: results_list_dict[0].get(job_name_key).replace('00y', '_all_yaws')})
            for key in list(results_list_dict[0].keys())[1:]:
                local_value = 0
                added_nYawErrors = nYawErrors
                for yawError_idx in range(nYawErrors):
                    if results_list_dict[yawError_idx].get(job_name_key).find('00y') != -1:  # the probability of a 0deg
                        local_value += float(results_list_dict[yawError_idx].get(key)) * 2   # yaw misalignment is twice
                        added_nYawErrors += 1                               # as high. Thus it should be weighted twice.
                    else:
                        local_value += float(results_list_dict[yawError_idx].get(key))
                leveled_results_list_dict[-1][key] = local_value / added_nYawErrors
            Utility().writeListDictToCSV(leveled_results_list_dict, documentation_path)

        return documentation_path

if __name__ == "__main__":
    # executing the function of this is a main function
    BladedPostProcess().DLC12_summarizer(documentation_path, nSeeds, nYawErrors)
