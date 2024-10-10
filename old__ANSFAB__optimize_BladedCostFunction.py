# This class guides through the process of starting and evaluating Bladed runs automatically to optimize parameters

import numpy as np
from ANSFAB__Utility import Utility, Bladed
from config import nSeeds, max_rotation_speed_bound, nParams, DocString, MainPathToBladedRuns, documentation_path


# define Bladed optimization work flow as a class:
class BladedMethod: # (object):
    def __init__(self, nBlades, baselineFolder, ListOfBaselineFiles):
        self.Iteration_idx = int(0)

        # for progress documentary
        self.MinCCC = []
        self.AverageCCC = []
        self.BestParameters = []
        self.Documentation = []
        self.Plot_documentary = []
        self.LastBestCCC = 2
        # dat: self.n_var = nParams

        #initial_fitness = float('inf')
        # ----------------------------------------------------------------------------------
        # self.global_best_CCC = initial_fitness
        # self.global_best_Params = []

        # print('# ----- starting to run initial Bladed jobs in Batch ----- #')
        # Bladed().AutoRunBatch(baselineFolder, ListOfBaselineFiles)

        try:
            print('# --- starting with initial CCC ref values calculation --- #')
            # DEL_keys = ['Blade_My_DEL', 'Hub_Mx_DEL', 'Tower_My_sector_max_DEL', 'Pitch_LDC']
            self.DEL_dicts_ref = Bladed().extractDEL_towerHubBlade(baselineFolder, ListOfBaselineFiles)
        except:
            # if not self.DEL_dicts_ref[0].get('Blade_My_DEL') == 0:
            print('# -- starting to run missing initial Bladed jobs in Batch -- #')
            Bladed().AutoRunBatch(baselineFolder, ListOfBaselineFiles)
            print('# -- re-starting with initial CCC ref values calculation -- #')
            self.DEL_dicts_ref = Bladed().extractDEL_towerHubBlade(baselineFolder, ListOfBaselineFiles)

        self.Statistics_ref = Bladed().extractStatisticalBladedResultsData(baselineFolder, ListOfBaselineFiles)
        [self.Statistics_ref[i].update(self.DEL_dicts_ref[i]) for i in range(len(self.Statistics_ref))]

        print('maximum rotation speed is: ' + str(self.Statistics_ref[0].get('RotationSpeed_max'))
              + ' and max allowed is: ' + str(max_rotation_speed_bound))

    def BladedOptimizationFunction(self, Params):

        print('\n\n# -------------- THIS IS GENERATION ' + str(self.Iteration_idx) + ' -------------- #\n\n')

        print('The Params are: ', Params)
        # Params = [Params[i] for i in range(nParams)]

        print('# ------- starting to manipulate Bladed job files ------- #')
        ListOfBladedJobs, RunFolder = Utility().manipulatePRJfiles(Params, self.Iteration_idx)

        print('# -------- starting to run Bladed jobs in Batch --------- #')
        Bladed().AutoRunBatch(RunFolder, ListOfBladedJobs, skip_of_existing=True)

        print('# ----------- starting with CCC calculation ------------- #')
        Statistics = Bladed().extractStatisticalBladedResultsData(RunFolder, ListOfBladedJobs)
        DEL_dicts = Bladed().extractDEL_towerHubBlade(RunFolder, ListOfBladedJobs)
        [Statistics[i].update(DEL_dicts[i]) for i in range(len(Statistics))]

        '''if nSeeds > 1:
            print('calculation mean of ' + str(nSeeds) + ' Seeds')
            print('CAUTION: is not validated any more')
            Statistics = Utility().calcMeanValuesForSeeds(Statistics)  #, nSeeds)
            DEL_dicts = Utility().calcMeanValuesForSeeds(DEL_dicts)    #, nSeeds) '''

        CCCs = [Utility().calcCCC(Statistic, self.Statistics_ref[0]) for Statistic in Statistics]

        self.AverageCCC.append(sum(CCCs) / len(CCCs))
        self.MinCCC.append(min(CCCs))
        if len(Statistics) == 1:
            self.BestParameters.append(Params)
        else:
            self.BestParameters.append(Params[np.argmin(CCCs)])

        global_best_CCC = min(self.MinCCC)
        global_best_Params = self.BestParameters[np.argmin(self.MinCCC)]

        print('# --------------------------------------------------------------------------------------------------- #')
        print('Average CCC is: ' + str(self.AverageCCC[-1]) + ' with min CCC ' + str(self.MinCCC[-1])
              + ' delta of ' + "%.4f" % ((self.MinCCC[-1] / self.LastBestCCC - 1) * 100)
              + '% and Parameters ', self.BestParameters[-1])
              #+ '% and Parameters ' + ", ".join([str(Param) for Param in self.BestParameters[-1]]))
        self.LastBestCCC = self.MinCCC[-1]
        print('# --------------------------------------------------------------------------------------------------- #')

        # Save most important parameters to csv file in every loop (note, opening GA_Strings in csv removes the leading 0s)
        Docu_keys = ['Generation', 'BladedJobName', 'CCC', 'Params']
        # [Docu_keys.append(key) for key in ['Blade_My_DEL', 'Blade_My_max', 'Hub_Mx_DEL', 'Tower_My_sector_max_DEL', 'Power_mean', 'Pitch_LDC']]
        [Docu_keys.append(key) for key in Statistics[0].keys()]
        # for idx in range(nPopulation):
        for idx in range(len(Statistics)):
            if Statistics[idx].get('Blade_My_max'):  # to be shure that its not empty
                if len(Statistics) == 1:
                    Params_string = ", ".join([str(Param) for Param in Params])
                else:
                    Params_string = ", ".join([str(Param) for Param in Params[idx]])

                new_Dict = {'Generation': self.Iteration_idx, 'BladedJobName': ListOfBladedJobs[idx], 'CCC': CCCs[idx], 'Params': Params_string}
                SubDict1 = {}
                SubDict2 = {}
                for Key in Docu_keys[4:]:
                    SubDict1.update({Key: Statistics[idx].get(Key)})
                    SubDict2.update({Key + '_ratio': Statistics[idx].get(Key) / self.Statistics_ref[0].get(Key)})
                new_Dict.update(SubDict1)
                new_Dict.update(SubDict2)
                self.Documentation.append(new_Dict)

        Utility().writeListDictToCSV(self.Documentation, documentation_path)

        # for later visualization
        self.Plot_documentary.append(
            dict(zip(['Iteration', 'global_best_CCC', 'step_best_CCC', 'AverageCCC']
                     + ['step_best_Parameters ' + str(j + 1) for j in range(nParams)]
                     + ['global_best_Parameters ' + str(j + 1) for j in range(nParams)],
                     [self.Iteration_idx, global_best_CCC, self.MinCCC[-1], sum(CCCs) / len(CCCs)]
                     + [j for j in self.BestParameters[-1]]
                     + [j for j in global_best_Params])))
        Utility().writeListDictToCSV(self.Plot_documentary, documentation_path.split('.')[0] + '_plot.csv')

        print('global_best_CCC: ', global_best_CCC, '   with global_best_Params: ', global_best_Params)

        self.Iteration_idx += 1

        if len(Statistics) == 1:
            return CCCs[-1]    # Otherwise, there is a List of a List with only a single value
        else:
            return CCCs



















'''
# Visualize initial distribution
if True:
    initial_plot = plt.figure(figsize=(7, 5))
    plt.xlabel('parameter')
    plt.ylabel('variation inside bounds')
    plt.title('Initial parameter distribution for seed ' + str(Seed))
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
                             + DocString + '_GPSO_Plot_Documentary_s' + str(int(Seed)) + '.png'))
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
