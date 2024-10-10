import os
from datetime import datetime
from ANSFAB__Utility import Utility
from ANSFAB__Utility import Bladed
from config import FOWTs
from main__DLC12_summarizer import BladedPostProcess


def evaluateFolder(folderPlusFirstSnip, use_hub_fixed_blade_coordinate_system=False):


    ListOfBladedJobs = []
    for run_file in Utility().return_run_files_in_folder(folderPlusFirstSnip): #, fileEnd='*.$25'):
        # ListOfBladedJobs.append(dict(zip(['run_name'], [''.join(run_file)])))
        ListOfBladedJobs.append(run_file.split('\\')[-1])  # .split('.')[0])

    print('job names are: ', ListOfBladedJobs)

    RunFolder = os.path.dirname(folderPlusFirstSnip)
    RunFolderName = RunFolder.split('\\')[-1]

    print('# ----------- starting with run evaluation ------------- #')
    # Statistics = extractStatisticalBladedResultsData(RunFolder, ListOfBladedJobs)
    Statistics = Bladed().extractStatisticalBladedResultsData(RunFolder, ListOfBladedJobs)
    # DEL_keys = ['Blade_My_DEL', 'Hub_Mx_DEL', 'Tower_My_sector_max_DEL', 'Pitch_LDC']
    # DEL_dicts = extractDEL_towerHubBlade(RunFolder, ListOfBladedJobs)
    DEL_dicts = Bladed().extractDEL_towerHubBlade(RunFolder, ListOfBladedJobs, use_hub_fixed_blade_coordinate_system=
                                                                               use_hub_fixed_blade_coordinate_system)

    # Save most important parameters to csv file in every loop (note, opening GA_Strings in csv removes the leading 0s)
    Docu_keys = ['Blade_Mx_DEL', 'Blade_My_DEL', 'Blade_Mz_DEL', 'Blade_Fz_DEL',  # 'Blade_My_max',
                 'Tower_Mx_DEL', 'Tower_My_DEL', 'Tower_My_sector_max_DEL', 'Tower_Mz_DEL',
                 'Hub_Mx_DEL', 'Hub_My_DEL', 'Hub_Mz_DEL', 'Hub_Myz_sector_max_DEL',
                 'Power_mean', 'Pitch_LDC', 'mean_Thrust_Hub_Fx']
    if FOWTs:
        Docu_keys += ['mean_Platform_Pitch', 'max_Platform_Pitch', 'max_mooring_tension']
    Docu_keys.append('max_Nacelle_FA_accel')
    if use_hub_fixed_blade_coordinate_system:
        Docu_keys += ['Blade_Mx_hub_root_DEL', 'Blade_My_hub_root_DEL', 'Blade_Mz_hub_root_DEL', 'Blade_Fz_hub_root_DEL']


    Documentation = []
    for idx in range(len(DEL_dicts)):
        # Documentation[idx]['ListOfBladedJobs'] = ListOfBladedJobs[idx]
        Documentation.append({'ListOfBladedJobs': ListOfBladedJobs[idx]})
        for key in Docu_keys:
            try:
                Documentation[idx][key] = DEL_dicts[idx][key]
            except:
                Documentation[idx][key] = Statistics[idx][key]

        '''Documentation.append(dict(zip(Docu_keys, [ListOfBladedJobs[idx], str(DEL_dicts[idx].get('Blade_Mx_DEL')),
                 str(DEL_dicts[idx].get('Blade_My_DEL')), str(DEL_dicts[idx].get('Blade_Mz_DEL')),
                 str(DEL_dicts[idx].get('Blade_Fz_DEL')),
                 str(DEL_dicts[idx].get('Tower_Mx_DEL')), str(DEL_dicts[idx].get('Tower_My_DEL')),
                 str(DEL_dicts[idx].get('Tower_My_sector_max_DEL')), str(DEL_dicts[idx].get('Tower_Mz_DEL')),
                 str(DEL_dicts[idx].get('Hub_Mx_DEL')),
                 str(Statistics[idx].get('Power_mean')), str(DEL_dicts[idx].get('Pitch_LDC'))])))'''

    print(Documentation)
    documentation_path = os.path.join(RunFolder, RunFolderName + '_' + datetime.today().strftime('%Y_%m_%d__')
                                          + '_DEL_evaluation.csv')

    Utility().writeListDictToCSV(Documentation, documentation_path)

    number_of_evaluated_runs = len(DEL_dicts)
    if number_of_evaluated_runs >= 9*3*6:
        nSeeds = 6
        nYawErrors = 3
    elif number_of_evaluated_runs >= 9*6:
        nSeeds = 6
        nYawErrors = 1
    elif number_of_evaluated_runs >= 9*3:
        nSeeds = 1
        nYawErrors = 3
    else:
        nSeeds = 1
        nYawErrors = 1
    print('----> ', nSeeds, 'seeds and ', nYawErrors, ' yaw errors are guessed by the amounts of evaluated runs')
    BladedPostProcess().DLC12_summarizer(documentation_path, nSeeds, nYawErrors)

    return Documentation, Docu_keys, ListOfBladedJobs, documentation_path















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
