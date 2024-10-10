import os
from datetime import datetime
from ANSFAB__Utility import Utility
from config import k_composite
import math



def evaluateFolder_for_DEL_along_blades(folder, calc_out_and_inplane_blade_DELs=False):
    DEL_along_blade__Searching = []

    DEL_along_blade__Searching.append({'VARIAB': 'Blade 1 Mx (Root axes)', 'FileEnd': '.%41', 'Desired': 'DEL'}) # has to remain Mx at position 0 to calc in and out of plane loads correctly
    DEL_along_blade__Searching.append({'VARIAB': 'Blade 1 My (Root axes)', 'FileEnd': '.%41', 'Desired': 'DEL'}) # has to remain My at position 1 to calc in and out of plane loads correctly
    DEL_along_blade__Searching.append({'VARIAB': 'Blade 1 Mz (Root axes)', 'FileEnd': '.%41', 'Desired': 'DEL'})
    DEL_along_blade__Searching.append({'VARIAB': 'Blade 1 Fz (Root axes)', 'FileEnd': '.%41', 'Desired': 'DEL'})

    DEL_along_blade__Searching__keys = ['Blade_Mx_DEL', 'Blade_My_DEL', 'Blade_Mz_DEL', 'Blade_Fz_DEL']

    documentation_path = os.path.join(folder, folder.split('\\')[-1] + '__' + datetime.today().strftime('%Y_%m_%d__')
                                      + '_DEL_along_blade1_evaluation_v2.csv')

    subfolders = [folder[0] for folder in os.walk(folder)]
    print('found folders ---> ', subfolders)

    Documentation = []
    # collect all runs in the desired folder
    ListOfBladedJobs_ULS = []
    for RunFolderName in subfolders:
        [ListOfBladedJobs_ULS.append(filename.replace('.$04', '.$PJ')) for filename in
         Utility().return_run_files_in_folder(RunFolderName, fileEnd='*.$04') if filename]
    print('found', len(ListOfBladedJobs_ULS), 'runs')

    # collect data file information (and utilize only the first run)
    BladedJob = ListOfBladedJobs_ULS[0].split('\\')[-1]
    RunFolder = ListOfBladedJobs_ULS[0].replace(BladedJob, '')
    for Search_idx, Search in enumerate(DEL_along_blade__Searching):
        if not Search_idx:
            print('search general time series file information in run', BladedJob, 'in folder', RunFolder)
        # search in the first run file for further information about the result files
        [fileEnd, idx, DIMENS] = Utility().collectTimeSeriesStructureFromBladedFiles(RunFolder=RunFolder,
                                                                                     BladedJob=BladedJob,
                                                                                     VariableName=Search.get(
                                                                                         'VARIAB'))
        DEL_along_blade__Searching[Search_idx]['FileEnd'] = fileEnd
        DEL_along_blade__Searching[Search_idx]['IDX'] = idx
        DEL_along_blade__Searching[Search_idx]['DIMENS'] = DIMENS

        print('   found VARIAB', Search.get('VARIAB'), 'for key', DEL_along_blade__Searching__keys[Search_idx],
              'in file *', fileEnd, 'at index', idx, 'with dimensions', DIMENS)



    leveled_results_list_dict = []
    for Job_idx, BladedJob_path in enumerate(ListOfBladedJobs_ULS):
        print('searching for DEL along the blades in ---> ', BladedJob_path)
        BladedJob = BladedJob_path.split('\\')[-1]
        RunFolder = BladedJob_path.replace(BladedJob, '')
        leveled_results_list_dict.append({'ListOfBladedJobs': BladedJob_path})

        Utility().calcTotalTimeAndDeltat(RunFolder, BladedJob)

        if calc_out_and_inplane_blade_DELs:
            [pitchFileEnd, pitch_angle_idx, pitch_DIMENS] = Utility().collectTimeSeriesStructureFromBladedFiles(
                RunFolder=RunFolder, BladedJob=BladedJob, VariableName='Blade 1 pitch angle')
            pitch_angle_timeSeries = Utility().readTimeSeriesData(RunFolder=RunFolder, BladedJob=BladedJob,
                fileEnd=pitchFileEnd, idx=pitch_angle_idx, DIMENS=pitch_DIMENS)
            Mx_timeSeries = []
            My_timeSeries = []

        for Search_idx, Search in enumerate(DEL_along_blade__Searching):
            fileEnd = Search.get('FileEnd')
            idx = Search.get('IDX')
            DIMENS = Search.get('DIMENS')
            for pos_in_dimension_two in range(1, int(DIMENS[1])+1):
                timeSeries = Utility().readTimeSeriesData(RunFolder=RunFolder, BladedJob=BladedJob, fileEnd=fileEnd,
                                                          idx=idx, DIMENS=DIMENS, pos_of_node=pos_in_dimension_two)
                DEL = Utility().calcDELfromTimeSeries(timeSeries, k=k_composite)

                local_search_key = DEL_along_blade__Searching__keys[Search_idx]+'_pos'+str(pos_in_dimension_two)
                leveled_results_list_dict[-1][local_search_key] = DEL

                if calc_out_and_inplane_blade_DELs and Search_idx == 0:
                    Mx_timeSeries.append(timeSeries)
                elif calc_out_and_inplane_blade_DELs and Search_idx == 1:
                    My_timeSeries.append(timeSeries)

        if calc_out_and_inplane_blade_DELs:
            for in_out_idx, in_out_key in enumerate(['Blade_M_in_plane_DEL_pos', 'Blade_M_out_of_plane_DEL_pos']):
                for pos_in_dimension_two in range(int(DIMENS[1])):
                    in_out_timeSeries = []
                    for time_step_idx, pitch_angle in enumerate(pitch_angle_timeSeries):
                        if not in_out_idx:  # refers to in-plane loads, calculated by turning Mx and My against the pitch direction:
                            in_out_timeSeries.append(
                                Mx_timeSeries[pos_in_dimension_two][time_step_idx] * math.cos(pitch_angle) +
                                My_timeSeries[pos_in_dimension_two][time_step_idx] * math.sin(pitch_angle))
                        else:  # refers to out-of-plane loads
                            in_out_timeSeries.append(
                               -Mx_timeSeries[pos_in_dimension_two][time_step_idx] * math.sin(pitch_angle) +
                                My_timeSeries[pos_in_dimension_two][time_step_idx] * math.cos(pitch_angle))
                    leveled_results_list_dict[-1][in_out_key + str(pos_in_dimension_two+1)] = \
                        Utility().calcDELfromTimeSeries(in_out_timeSeries, k=k_composite)


            '''M_in_plane_timeSeries = []
            M_out_of_plane_timeSeries = []
            for pos_in_dimension_two in range(1, int(DIMENS[1])+1):
                for time_step_idx, pitch_angle in enumerate(pitch_angle_timeSeries):
                    M_in_plane_timeSeries.append(     Mx_timeSeries[pos_in_dimension_two-1][time_step_idx] * math.cos(pitch_angle) + My_timeSeries[pos_in_dimension_two-1][time_step_idx] * math.sin(pitch_angle))
                    M_out_of_plane_timeSeries.append(-Mx_timeSeries[pos_in_dimension_two-1][time_step_idx] * math.sin(pitch_angle) + My_timeSeries[pos_in_dimension_two-1][time_step_idx] * math.cos(pitch_angle))
                leveled_results_list_dict[-1]['Blade_M_in_plane_DEL_pos'+str(pos_in_dimension_two)] = Utility().calcDELfromTimeSeries(M_in_plane_timeSeries, k=k_composite)
                leveled_results_list_dict[-1]['Blade_M_out_of_plane_DEL_pos'+str(pos_in_dimension_two)] = Utility().calcDELfromTimeSeries(M_out_of_plane_timeSeries, k=k_composite)'''



        Utility().writeListDictToCSV(leveled_results_list_dict, documentation_path)

    return Documentation, DEL_along_blade__Searching__keys, ListOfBladedJobs_ULS, documentation_path



'''
def evaluateFolder_for_ULS(folder, search_in_subfolders=True):
    documentation_path = os.path.join(folder, folder.split('\\')[-1] + '__' + datetime.today().strftime('%Y_%m_%d__')
                                      + '_ULS_evaluation.csv')

    subfolders = [folder[0] for folder in os.walk(folder)]
    print('found folders ---> ', subfolders)

    Documentation = []
    for RunFolderName in subfolders:
        ListOfBladedJobs_ULS = [filename.replace('.$04', '.$PJ').split('\\')[-1] for filename in Utility().return_run_files_in_folder(RunFolderName, fileEnd='*.$04')]
        if ListOfBladedJobs_ULS:
            print('searching for ULS in folder ---> ', RunFolderName, ' in files --->', ListOfBladedJobs_ULS)
            Statistics = Bladed().extractStatisticalBladedResultsData(RunFolderName, ListOfBladedJobs_ULS, ULS_search=True)
            for idx in range(len(Statistics)):
                # Documentation[idx]['ListOfBladedJobs'] = ListOfBladedJobs[idx]
                Documentation.append({'ListOfBladedJobs': ListOfBladedJobs_ULS[idx]})
                for key in ULS_Searching_keys:
                    Documentation[idx][key] = Statistics[idx][key]

        Utility().writeListDictToCSV(Documentation, documentation_path)

    return Documentation, ULS_Searching_keys, ListOfBladedJobs_ULS, documentation_path
'''











'''
# Visualize initial distribution
if True:
    initial_plot = plt.figure(figsize=(7, 5))
    plt.xlabel('parameter')
    plt.ylabel('variation inside bounds')
    plt.title('Initial parameter distribution for seed ' + str(OriginalSeed))
    for j, particle in enumerate(swarm_particle):
        plt.plot(range(nParams), [(particle.particle_position[i] - bounds[i][0])/(bounds[i][1] - bounds[i][0])
                                  for i in range(nParams)], label='particle ' + str(j), marker="o", linestyle='--')
    plt.legend(bbox_to_anchor=(1.04, 1), loc="upper left")
    initial_plot.canvas.draw()
    initial_plot.canvas.flush_events()
    #plt.show()
    plt.pause(10)
    plt.ioff()

plt.ion()
# ------------------------------------------------------------------------------
# following Visualization
fig = plt.figure(figsize=(12, 10))
ax1 = fig.add_subplot()
ax2 = ax1.twinx()
linestyles = ['-', '--', '-.', ':', '-', '--', '-.', ':', '-', '--', '-.', ':', '-', '--', '-.', ':', '-', '--']
ax1.set_xlabel('generations')
ax2.set_ylabel('Parameter')
ax1.set_ylabel('CCC')
plt.title('GA_convergence_plot')
fig.show()'''







'''
    # ax1.plot(TestUniqueQuasiRandom, 'o')
    ax1.plot(global_best_particle_fitness_list, color='r', label='global best')
    ax1.plot(MinCCC, linestyle='--', color='red', label='min CCC')
    ax2.plot(AverageCCC, linestyle=':', color='green', label='average CCC')
    ax1.set_xlim(left=max(0, i-iterations), right=i + 3)
    # ax1.set_ylim(lower=0.5, upper=1.5)
    for idx in range(nParams):
        ax2.plot([BestPosition[idx] for BestPosition in global_best_partical_position_list], linestyle=linestyles[idx],
                 label='Position ' + str(idx))
    if i == 0:
        ax1.legend(loc='upper left')
        ax2.legend(loc='upper right')

    fig.canvas.draw()
    fig.canvas.flush_events()
    plt.pause(5)

    plt.savefig(os.path.join(MainPathToBladedRuns, datetime.today().strftime('%Y_%m_%d__')
                             + DocString + '_GPSO_Plot_Documentary_s' + str(int(OriginalSeed)) + '.png'))
    '''


'''
    CountDuplicates = 0
    for idx, Rand in enumerate(TestUniqueQuasiRandom):
        if Rand in TestUniqueQuasiRandom[:idx] + TestUniqueQuasiRandom[idx + 1:]:
            CountDuplicates += 1
    if CountDuplicates > 0:
        print('Error by Random Value. '+str(CountDuplicates)+' of '+str(len(TestUniqueQuasiRandom))+' are duplicates!')
    '''



#plt.ioff()
#plt.show()
