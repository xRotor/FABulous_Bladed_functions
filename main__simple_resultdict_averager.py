from ANSFAB__Utility import Utility
from config import k_steel, k_composite, p_bearing, p_yaw_bearing


documentation_path = r'H:\BladedWS\BottomFixed\DLC_legacy\2B101_all_IEA_Monopiles_DLC12_evalu\new\z_DLC12_2B101v15_MonoIEA9m_7modes_FA_damp_itr\itrFA_6seeds_10min_TS\itrFA_6seeds_10min_TS__2024_10_22___FLS_new.csv'
#documentation_path = r

differing_strings = []
for wspeed in range(5,26,2):
    for idx in range(1,7):
        differing_strings.append('_s%s%s_' %(idx, str(wspeed).zfill(2)))
print(differing_strings)


results_list_dict = Utility().readListDictFromCSV(documentation_path)

assigning_indexes = {}
job_name_key = list(results_list_dict[0].keys())[0]
for idx, result_dict in enumerate(results_list_dict):
    job_name = result_dict.get(job_name_key)
    for differing_string in differing_strings:
        job_name = job_name.replace(differing_string, '_')
    #results_list_dict[idx][job_name_key] = job_name
    #print('job_name:', job_name)
    if job_name in assigning_indexes:
        assigning_indexes[job_name].append(idx)
    else:
        assigning_indexes[job_name] = [idx]

averaged_results_list_dict = []
for assigning_key in assigning_indexes:
    # print('averaging: ', assigning_key )
    averaged_results_list_dict.append({job_name_key: assigning_key})
    for key in list(results_list_dict[0].keys())[1:]:
        averaged_value = 0
        for assigned_index in assigning_indexes.get(assigning_key):
            averaged_value = averaged_value + float(results_list_dict[assigned_index].get(key))
        averaged_results_list_dict[-1][key] = averaged_value/len(assigning_indexes.get(assigning_key))


documentation_path = documentation_path.split('.')[0] + '_averaged.csv'
documentation_path = Utility().writeListDictToCSV(averaged_results_list_dict, documentation_path)





class BladedPostProcess:
    def DLC12_summarizer(self, documentation_path, nSeeds=6, nYawErrors=3):
        results_list_dict = Utility().readListDictFromCSV(documentation_path)

        # collect all indexes of one wind speed in a list
        wind_speed_idx_dict_list = {}
        job_name_key = list(results_list_dict[0].keys())[0]
        for idx, result_dict in enumerate(results_list_dict):
            job_name = result_dict.get(job_name_key)
            for name_section in job_name.split('_'):
                if name_section.find('mps') != -1:
                    wind_speed = int(name_section.split('.')[0].replace('mps', '')[-2:])
                    if wind_speed not in list(wind_speed_idx_dict_list.keys()):
                        wind_speed_idx_dict_list[wind_speed] = []
                    wind_speed_idx_dict_list[wind_speed].append(idx)
                    if job_name.find('0y_') != -1:
                        wind_speed_idx_dict_list[wind_speed].append(idx)


        print(wind_speed_idx_dict_list)


        leveled_results_list_dict = []
        for wind_speed_key in list(wind_speed_idx_dict_list.keys()):
            leveled_run_name = results_list_dict[wind_speed_idx_dict_list.get(wind_speed_key)[0]].get(job_name_key).replace('00y_' or 'n8y_' or 'p8y_', 'all_yaws_').split('mps_')[0] + 'mps' # .split('mps')[0][:-2] + '_all_mps'
            #global_run_name = results_list_dict[wind_speed_idx_dict_list.get(wind_speed_key)[0]].get(job_name_key).split('mps')[0][:-2] + '_all_mps'
            leveled_results_list_dict.append({job_name_key: leveled_run_name})
            print(leveled_run_name)
            for key in list(results_list_dict[0].keys())[1:]:
                if key.find('DEL') != -1:
                    if key.find('Blade') != -1:
                        k = k_composite
                    else:
                        k = k_steel
                elif key.find('P_ea') != -1:
                    if key.find('pitch') != -1 or key.find('Pitch') != -1:
                        k = p_bearing
                    else:
                        k = p_yaw_bearing
                elif key.find('max') != -1 or key.find('MAX') != -1 or key.find('MIN') != -1 or key.find('ULS') != -1:
                    k = 0
                else:
                    k = 1
                leveled_value = 0
                for result_run_index in wind_speed_idx_dict_list[wind_speed_key]:
                    local_value = float(results_list_dict[result_run_index].get(key))
                    # probability = Utility().calc_rayleigh_distribution_probability_from_wind_speed(wind_speed_key) / nSeeds
                    probability = 1 / len(wind_speed_idx_dict_list[wind_speed_key])
                    if k > 0:
                        leveled_value += pow(local_value, k) * probability
                    else:
                        if k < 0:
                            if abs(leveled_value) > abs(local_value):  # covers MIN (min of absolute values)
                                leveled_value = local_value
                        else:
                            if abs(leveled_value) < abs(local_value):  # covers MAX and AMAX (max of absolute values)
                                leveled_value = local_value
                if k > 0:
                    leveled_value = pow(leveled_value, 1/k)

                leveled_results_list_dict[-1][key] = leveled_value


        documentation_path = documentation_path.split('.')[0] + '_leveled.csv'
        documentation_path = Utility().writeListDictToCSV(leveled_results_list_dict, documentation_path)

        global_run_name = leveled_run_name.split('mps')[0][:-2] + '_all_mps'
        global_leveled_results_dict = {job_name_key: global_run_name}
        #leveled_results_list_dict.append({job_name_key: global_run_name})
        #for results_idx, results_dict in enumerate(leveled_results_list_dict):
        for key_idx, key in enumerate(list(results_list_dict[0].keys())[1:]):
            if key.find('DEL') != -1:
                if key.find('Blade') != -1:
                    k = k_composite
                else:
                    k = k_steel
            elif key.find('P_ea_pitch') != -1:
                k = p_bearing
            elif key.find('P_ea_yaw') != -1:
                k = p_yaw_bearing
            elif key.find('max') != -1 or key.find('MAX') != -1 or key.find('ULS') != -1:
                k = 0
            elif key.find('MIN') != -1:
                k = -1
            else:
                k = 1
            leveled_value = 0
            for results_idx, results_dict in enumerate(leveled_results_list_dict):
                local_value = float(results_dict.get(key))
                probability = Utility().calc_rayleigh_distribution_probability_from_wind_speed(list(wind_speed_idx_dict_list.keys())[results_idx])
                # probability = 1 / len(wind_speed_idx_dict_list[wind_speed_key])
                if k > 0:
                    leveled_value += pow(local_value, k) * probability
                else:
                    if k < 0:
                        if abs(leveled_value) > abs(local_value):  # covers MIN (min of absolute values)
                            leveled_value = local_value
                    else:
                        if abs(leveled_value) < abs(local_value):  # covers MAX and AMAX (max of absolute values)
                            leveled_value = local_value
            if k > 0:
                leveled_value = pow(leveled_value, 1/k)

            global_leveled_results_dict[key] = leveled_value

        leveled_results_list_dict.append(global_leveled_results_dict)
                

        # documentation_path = documentation_path.split('.')[0] + '_leveled_new.csv' # might be unnecessary to add new name
        documentation_path = Utility().writeListDictToCSV(leveled_results_list_dict, documentation_path)


        print('Note: The probablities herein do !! NOW !! sum up to the value of one!')


        return documentation_path

#if __name__ == "__main__":
#    # executing the function of this is a main function
#    BladedPostProcess().DLC12_summarizer(documentation_path)  # nSeeds, nYawErrors)
