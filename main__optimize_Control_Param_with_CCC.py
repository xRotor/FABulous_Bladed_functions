# The global particle swarm optimization (GPSO) utilizes the procedure published in "Global Particle Swarm Optimization
# for High Dimension Numerical Functions Analysis" from J. J. Jamian M. N. Abdullah H. Mokhlis M. W. Mustafa et.al.


#import random
#import matplotlib.pyplot as plt
# sys.path.append(r"C:/Program Files (x86)/Python38-32/EvoloPy/")
#from datetime import datetime
#from ANSFAB__GA_BladedBatchAuto import RunJobsInBladed
#from ANSFAB__GA_manipulate_prj_file import manipulatePRJfiles
#from ANSFAB__GA_Utility import GA_utility
#from ANSFAB__GA_extract_Statistical_Bladed_ASCII_Data import extractStatisticalBladedResultsData
#from ANSFAB__GA_DEL_BladeTowerHubMy_max_sector import extractDEL_towerHubBlade

#from ANSFAB___Customize_GA import nBlades, baselineFolder, MainPathToBladedRuns, ListOfBaselineFiles, searchWords, \
#    addToRunFileNames, SolutionIntervals, nPopulation, p_cross, p_mutate, Generations, UseElite, CostShares, nSeeds, nParams, Seed

# from ANSFAB___Customize_GA import SolutionIntervals, nParams
from ANSFAB__optimize_BladedCostFunction import BladedMethod #, MainPathToBladedRuns, DocString
from config import nBlades, baselineFolder, ListOfBaselineFiles

#sys.stdout=open(os.path.join(MainPathToBladedRuns,datetime.today().strftime('%Y_%m_%d__')+DocString+'_logging.txt'),"w")
#ListOfBaselineFiles = []
#ListOfBaselineFiles.append(r'2B20Volt_v009_1_15mps.$PJ')
#baselineFolder = r'C:\xBladed\FOWTs\test_pitchDamper'
#baselineFolder = r'H:\BladedWS\FOWTs\Optimize_FA_Damper_2B20Volt_v009\baselineFile'




CF = BladedMethod(nBlades, baselineFolder, ListOfBaselineFiles)  # Cost function initialization

Switch = 3
if Switch == 1:
    ##################### MATLABS NELDER-MEAD SIMPLEX ALGORITHM ##########################
    from scipy.optimize import fmin
    minimum = fmin(CF.BladedOptimizationFunction, [0.1, 0.05])  # , +0.001])
    ##################### MATLABS  NELDER-MEAD SIMPLEX ALGORITHM #########################
elif Switch == 2:
    from scipy.optimize import shgo
    bounds = [(0, 0.4), (0, 0.2)]
    minimum = shgo(CF.BladedOptimizationFunction, bounds)  # , workers=8)  # , +0.001])
    print(minimum)
elif Switch == 3:
    from scipy.optimize import basinhopping
    minimum = basinhopping(CF.BladedOptimizationFunction, [0.1, 0.05], stepsize=0.03)  # , +0.001])
    print(minimum)

'''
################################### MIT's PSO #########################################
import pyswarms as ps
# Set-up hyperparameters
options = {'c1': 0.5, 'c2': 0.3, 'w': 0.3}

SolutionIntervals = [[0.0, 0.0, -20, 0.12], [0.09, 0.09, 20, 0.8]]
# Call instance of PSO
optimizer = ps.single.GlobalBestPSO(n_particles=30, dimensions=nParams, options=options,bounds=SolutionIntervals)

# Perform optimization
cost, pos = optimizer.optimize(CF.BladedOptimizationFunction, iters=50)
################################### MIT's PSO #########################################
'''



















































'''
####################### USING MEALPY TOOLBOX (MIT Licence) ############################
# https://github.com/thieu1995/mealpy
from mealpy.swarm_based.PSO import BasePSO, PPSO, P_PSO, HPSO_TVAC
from mealpy.swarm_based.BA import BaseBA, BasicBA, OriginalBA
from mealpy.music_based.HS import BaseHS, OriginalHS
from mealpy.swarm_based.SRSR import BaseSRSR
# not yet tested:
from mealpy.evolutionary_based.DE import BaseDE, SAP_DE, JADE, SHADE, L_SHADE, SADE # L_SHADE: Tanabe, R., & Fukunaga, A. S. (2014, July). Improving the search performance of SHADE using linear population size reduction. In 2014 IEEE congress on evolutionary computation (CEC) (pp. 1658-1665). IEEE.
from mealpy.swarm_based.ABC import BaseABC

# Setting parameters
obj_func = CF.BladedOptimizationFunction  # This objective function come from "opfunu" library. You can design your own objective function like above
verbose = False  # Print out the training results
epoch = 50  # Number of iterations / generations / epochs
pop_size = 10  # Populations size (Number of individuals / Number of solutions)

# A - Different way to provide lower bound and upper bound. Here are some examples:

## 1. When you have different lower bound and upper bound for each variables
lb1 = [bound[0] for bound in SolutionIntervals]
ub1 = [bound[1] for bound in SolutionIntervals]

## 2. Using batch size idea
batchIdea = True
batchSize = 5

# Optimize = BaseBA(obj_func, lb1, ub1, verbose, epoch, pop_size)# , batch_idea=batchIdea, batch_size=batchSize)
Optimize = L_SHADE(obj_func, lb1, ub1, verbose, epoch, pop_size)
best_pos1, best_fit1, list_loss1 = Optimize.train()
print(Optimize.solution[0])
print(Optimize.solution[1])
print(Optimize.loss_train)'''

















#plt.ioff()
#plt.show()
#sys.stdout.close()