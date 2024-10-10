import os
from datetime import datetime
from math import copysign
from ANSFAB__Utility import Utility, Bladed
from ANSFAB__Utility import Bladed
from config import ULS_Searching #, FOWTs, ULS_Searching_keys
from main__ULS_summarizer_incl_each_DLC_ULS__all_new import BladedPostProcess

# Note from DNV Guidelines:
# DLC 1.4 and 1.5: Different rotor azimuth positions shall be considered. Evenly distributed rotor azimuth
# positions (with intervals be at most 30° for three-bladed turbines and 45° for two-bladed turbines) shall be
# simulated for each wind speed. For each wind speed, the characteristic load value may be determined as
# the average of all these distinct rotor azimuth positions.

# DLC 1.3 embodies the requirements for the ultimate loading resulting from extreme turbulence conditions.
# These conditions include both environmental turbulence as well as turbine wake extreme turbulence. For
# the analysis, it is sufficient to assume that mean wind and wave directions coincide.

# 4.7.2 Evaluation of load cases applying deterministic gusts [DLC 1.4, 1.5, 2.3]
# For load cases with specified deterministic gusts, the characteristic value of the loads shall be the worst case
# computed transient values. If more simulations are performed at a given wind speed, representing the rotor azimuth,
# the characteristic value for the load case is taken as the average value of the worst case computed transient values
# at each azimuth.
#
# 4.7.3 Evaluation of load cases applying turbulent wind [DLC 1.3, 1.6, 2.2, 5.1, 6.1, 6.3]
# For load cases with turbulent wind fields the total period of load data shall be long enough to ensure statistical
# reliability of the estimate of the characteristic loads. At least six 10 min stochastic realizations with different
# turbulent seeds shall be required for each mean hub-height wind speed used in the simulations. However, for DLC 2.1,
# 2.2 and 5.1 at least 12 simulations shall be carried out for each event at the given wind speed.
#
# When turbulent inflow is applied, the mean value among the worst case computed loads for different 10 min stochastic
# realisations shall be taken, except for DLC 2.1, 2.2 and 5.1, where the characteristic value of the load shall be the
# mean value of the largest half of the maximum loads.
#
# The same method shall be used for determining characteristic values of other properties such as deflections and
# accelerations.
#
# [Own edit: If 1h instead of six 10 min realizations are used, the 1h simulation could be cutted in 6 pieces to
# evaluate the mean of the worst cases in the 6 realizations, correct?]

def evaluateFolder_for_ULS(folder, search_in_subfolders=True):
    documentation_path = os.path.join(folder, folder.replace('\\\\', '\\').split('\\')[-2] + '__'
                                      + datetime.today().strftime('%Y_%m_%d__') + '_ULS_evaluation.csv')

    subfolders = [folder[0].replace('\\\\', '\\') for folder in os.walk(folder)]
    print('found folders ---> ', subfolders)

    Documentation = []
    # collect all runs in the desired folder
    ListOfBladedJobs_ULS = []
    for RunFolderName in subfolders:
        [ListOfBladedJobs_ULS.append(filename.replace('.$05', '.$PJ')) for filename in
         Utility().return_run_files_in_folder(RunFolderName, fileEnd='*.$05') if filename]
    print('found', len(ListOfBladedJobs_ULS), 'runs')

    leveled_results_list_dict = []
    for Job_idx, BladedJob_path in enumerate(ListOfBladedJobs_ULS):
        print('searching for ULS in run', Job_idx, '---> ', BladedJob_path)
        BladedJob = BladedJob_path.split('\\')[-1]
        RunFolder = BladedJob_path.replace(BladedJob, '')
        leveled_results_list_dict.append({'ListOfBladedJobs': BladedJob_path})

        nmbr_removed_items = 0
        for Search_idx, Search in enumerate(ULS_Searching[:]):  # [:] forces to create a copy of the list to avoid
            Search_idx = Search_idx - nmbr_removed_items            # issues when removing items inside the loop
            if not Job_idx:  # only used in first run evaluation
                if not Search_idx:  # only used in the very first loop
                    print('search general time series file information in run', BladedJob, 'in folder', RunFolder)
                # search in the first run file for further information about the result files
                [fileEnd, idx, DIMENS] = Utility().collectTimeSeriesStructureFromBladedFiles(RunFolder=RunFolder,
                                                                BladedJob=BladedJob, VariableName=Search.get('VARIAB'))

                if not fileEnd:
                    print('   cannot find VARIAB', Search.get('VARIAB'), '  Will skip this loop and remove the key', Search.get('Key'))
                    del ULS_Searching[Search_idx]
                    nmbr_removed_items += 1
                    continue

                print('   found VARIAB', Search.get('VARIAB'), 'for key', Search.get('Key'),
                  'in file *', fileEnd, 'at index', idx, 'with dimensions', DIMENS)

                ULS_Searching[Search_idx]['FileEnd'] = fileEnd
                ULS_Searching[Search_idx]['IDX'] = idx
                ULS_Searching[Search_idx]['DIMENS'] = DIMENS

            fileEnd = Search.get('FileEnd')
            idx = Search.get('IDX')
            DIMENS = Search.get('DIMENS')

            if Search.get('NodePos')[0] == 'ALL':
                if len(DIMENS) == 3:
                    ULS_Searching[Search_idx]['NodePos'] = [i+1 for i in range(int(DIMENS[1]))]
                else:
                    ULS_Searching[Search_idx]['NodePos'] = [-1]

            # loop over the positions if many or all positions of one component e.g. mooring lines should be evaluated:
            for position_idx, position_of_node in enumerate(Search.get('NodePos')):
                #try:
                TimeSeries = Utility().readTimeSeriesData(RunFolder=RunFolder, BladedJob=BladedJob, fileEnd=fileEnd,
                                                          idx=idx, DIMENS=DIMENS, pos_of_node=position_of_node)
                #except OSError:  TimeSeries = [0]  # [-1]
                if TimeSeries == [0]:  # [-1]
                    print(' >>>>>> WARNING <<<<<< Time Series of ', Search.get('VARIAB'), ' does not exist. Will set ULS value to 0.')
                    # leveled_results_list_dict[-1][Search.get('Key')] = 0
                    ULS_of_desired_value = 0
                    continue

                if not Search_idx:
                    [time_total, deltat] = Utility().calcTotalTimeAndDeltat(RunFolder, BladedJob)

                search_mode = Search.get('Desired')

                if time_total < 1200:
                    if search_mode == 'ULS':
                        desired_value = max(TimeSeries, key=abs)
                    if search_mode == 'MAX':
                        desired_value = max(TimeSeries)
                    if search_mode == 'MIN':
                        desired_value = min(TimeSeries)

                else:
                    multiple_TimeSeries = []
                    number_of_blocks = int(time_total/600)  # cutting the time series into 10 minute alias 600 s pieces
                    steps_per_block = int(time_total/number_of_blocks/deltat)
                    for cutting_idx in range(number_of_blocks):
                        if cutting_idx < number_of_blocks:
                            multiple_TimeSeries.append(TimeSeries[int(steps_per_block * cutting_idx):
                                                                  int(steps_per_block * (cutting_idx+1))])
                        else:  # to ensure that all time steps are included and the list does not get out of range
                            multiple_TimeSeries.append(TimeSeries[int(steps_per_block * cutting_idx):-1])
                    ULS_values = []
                    for TimeSeries in multiple_TimeSeries:
                        if search_mode == 'ULS':
                            ULS_values.append(max(TimeSeries, key=abs))
                        if search_mode == 'MAX':
                            ULS_values.append(max(TimeSeries))
                        if search_mode == 'MIN':
                            ULS_values.append(min(TimeSeries))

                    # the mean of the absolute ULS values is need with sign of the ultimate among the ULS
                    sum_ULS_values = 0
                    for ULS_value in ULS_values:
                        sum_ULS_values += abs(ULS_value)
                    desired_value = sum_ULS_values / number_of_blocks * copysign(1, max(ULS_values, key=abs))

                if position_idx:
                    if search_mode == 'MIN':
                        if ULS_of_desired_value > desired_value:
                            ULS_of_desired_value = desired_value
                    else:
                        if abs(ULS_of_desired_value) < abs(desired_value):
                            ULS_of_desired_value = desired_value
                else:
                    ULS_of_desired_value = desired_value


            leveled_results_list_dict[-1][Search.get('Key')] = ULS_of_desired_value

    Utility().writeListDictToCSV(leveled_results_list_dict, documentation_path)

    # old: Bladed().ULS_DLCs_evaluation_summarizer(documentation_path)
    BladedPostProcess().ULS_DLCs_evaluation_summarizer(documentation_path)

    return Documentation, ListOfBladedJobs_ULS, documentation_path  #, ULS_Searching_keys



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
