""" ====================================================================================================================

                                        Customize the Genetic Algorithm (GA)
                         ------------------------------------------------------------------

                    Here, all the parameters are stored, that need to be adapted from the user

==================================================================================================================== """
nBlades = 2

# Folders and Job names
# baselineFolder = r"D:\GeneticAlgorithm_Bladed_tuning\baselineFiles_turb\\"
#baselineFolder = r"D:\GeneticAlgorithm_Bladed_tuning\baselineFiles_turb_1P2P_IPC\\"
baselineFolder = r"D:\GeneticAlgorithm_Bladed_tuning\baselineFiles_temp_run_folder\\"
# baselineFolder = r"D:\GeneticAlgorithm_Bladed_tuning\baselineFiles_LIPC_1P\\"
MainPathToBladedRuns = r"D:\GeneticAlgorithm_Bladed_tuning\runs\\"
#ListOfBaselineFiles = [r"2B101IPC1P2P07mps121.$PJ", r"2B101IPC1P2P07mps264.$PJ", r"2B101IPC1P2P07mps473.$PJ", r"2B101IPC1P2P07mps551.$PJ", r"2B101IPC1P2P07mps627.$PJ", r"2B101IPC1P2P07mps961.$PJ"]
# ListOfBaselineFiles = [r"2B101IPC1P2P11mps121.$PJ", r"2B101IPC1P2P11mps264.$PJ", r"2B101IPC1P2P11mps473.$PJ", r"2B101IPC1P2P11mps551.$PJ", r"2B101IPC1P2P11mps627.$PJ", r"2B101IPC1P2P11mps961.$PJ"]
# ListOfBaselineFiles = [r"2B101IPC1P2P15mps121.$PJ", r"2B101IPC1P2P15mps264.$PJ", r"2B101IPC1P2P15mps473.$PJ", r"2B101IPC1P2P15mps551.$PJ", r"2B101IPC1P2P15mps627.$PJ", r"2B101IPC1P2P15mps961.$PJ"]
ListOfBaselineFiles = [r"2B101LIPCbode15mps121.$PJ", r"2B101LIPCbode15mps264.$PJ", r"2B101LIPCbode15mps473.$PJ", r"2B101LIPCbode15mps551.$PJ", r"2B101LIPCbode15mps627.$PJ", r"2B101LIPCbode15mps961.$PJ"]
#ListOfBaselineFiles = [r"2B101FF2P_IPC15mps121.$PJ", r"2B101FF2P_IPC15mps264.$PJ", r"2B101FF2P_IPC15mps473.$PJ", r"2B101FF2P_IPC15mps551.$PJ", r"2B101FF2P_IPC15mps627.$PJ", r"2B101FF2P_IPC15mps961.$PJ"]
#ListOfBaselineFiles = [r"2B101FF2P_CPC15mps121.$PJ", r"2B101FF2P_CPC15mps264.$PJ", r"2B101FF2P_CPC15mps473.$PJ", r"2B101FF2P_CPC15mps551.$PJ", r"2B101FF2P_CPC15mps627.$PJ", r"2B101FF2P_CPC15mps961.$PJ"]
#ListOfBaselineFiles = [r"2B101LIPCbode23mps121.$PJ", r"2B101LIPCbode23mps264.$PJ", r"2B101LIPCbode23mps473.$PJ", r"2B101LIPCbode23mps551.$PJ", r"2B101LIPCbode23mps627.$PJ", r"2B101LIPCbode23mps961.$PJ"]
#ListOfBaselineFiles = [r"2B101LIPCbode11mps121.$PJ", r"2B101LIPCbode11mps264.$PJ", r"2B101LIPCbode11mps473.$PJ", r"2B101LIPCbode11mps551.$PJ", r"2B101LIPCbode11mps627.$PJ", r"2B101LIPCbode11mps961.$PJ"]
# ListOfBaselineFiles = [r"2B101LIPCbode07mps121.$PJ", r"2B101LIPCbode07mps264.$PJ", r"2B101LIPCbode07mps473.$PJ", r"2B101LIPCbode07mps551.$PJ", r"2B101LIPCbode07mps627.$PJ", r"2B101LIPCbode07mps961.$PJ"]

ListOfBaselineFiles = [r"2B101yawCon23mps121.$PJ", r"2B101yawCon23mps264.$PJ", r"2B101yawCon23mps473.$PJ", r"2B101yawCon23mps551.$PJ", r"2B101yawCon23mps627.$PJ", r"2B101yawCon23mps961.$PJ"]
ListOfBaselineFiles = [r"2B101yawCon13mps121.$PJ", r"2B101yawCon13mps264.$PJ", r"2B101yawCon13mps473.$PJ", r"2B101yawCon13mps551.$PJ", r"2B101yawCon13mps627.$PJ", r"2B101yawCon13mps961.$PJ"]
ListOfBaselineFiles = [r"2B101yawCon17mps121.$PJ", r"2B101yawCon17mps264.$PJ", r"2B101yawCon17mps473.$PJ", r"2B101yawCon17mps551.$PJ", r"2B101yawCon17mps627.$PJ", r"2B101yawCon17mps961.$PJ"]
ListOfBaselineFiles = [r"2B101yawCon15mps121.$PJ", r"2B101yawCon15mps264.$PJ", r"2B101yawCon15mps473.$PJ", r"2B101yawCon15mps551.$PJ", r"2B101yawCon15mps627.$PJ", r"2B101yawCon15mps961.$PJ"]
ListOfBaselineFiles = [r"2B101yawCon11mps121.$PJ", r"2B101yawCon11mps264.$PJ", r"2B101yawCon11mps473.$PJ", r"2B101yawCon11mps551.$PJ", r"2B101yawCon11mps627.$PJ", r"2B101yawCon11mps961.$PJ"]


# ListOfBaselineFiles = [r"2B101IPC1P2P19mps121.$PJ", r"2B101IPC1P2P19mps264.$PJ", r"2B101IPC1P2P19mps473.$PJ", r"2B101IPC1P2P19mps551.$PJ", r"2B101IPC1P2P19mps627.$PJ", r"2B101IPC1P2P19mps961.$PJ"]
# ListOfBaselineFiles = [r"2B101IPC1P2P23mps121.$PJ", r"2B101IPC1P2P23mps264.$PJ", r"2B101IPC1P2P23mps473.$PJ", r"2B101IPC1P2P23mps551.$PJ", r"2B101IPC1P2P23mps627.$PJ", r"2B101IPC1P2P23mps961.$PJ"]
# ListOfBaselineFiles = [r"2B101PTC15mps264.$PJ"]# [r"2B101PTC15mps121.$PJ", r"2B101PTC15mps264.$PJ", r"2B101PTC15mps473.$PJ", r"2B101PTC15mps551.$PJ", r"2B101PTC15mps627.$PJ", r"2B101PTC15mps961.$PJ"]
# ListOfBaselineFiles = [r"2B101_15mps_s121.$PJ", r"2B101_15mps_s264.$PJ", r"2B101_15mps_s473.$PJ", r"2B101_15mps_s551.$PJ", r"2B101_15mps_s627.$PJ", r"2B101_15mps_s961.$PJ"]# searchWords = ['pitchPGain', 'pitchIGain']
# ListOfBaselineFiles =[r"2B101IPC1P2P15mps264.$PJ"]   # 2B101IPClio15mps_s264  #  2B101IPClio_c15mps # 2B101SB_IPClio_c15mps
# searchWords = ['pitchPGain', 'pitchIGain']
# searchWords = ['GA_Parameter1', 'GA_Parameter2', 'GA_Parameter3', 'GA_Parameter4',
#               'GA_Parameter5', 'GA_Parameter6', 'GA_Parameter7', 'GA_Parameter8']
searchWords = ['GA_Parameter11', 'GA_Parameter12', 'GA_Parameter13',# 'GA_Parameter14',
               #'GA_Parameter15', 'GA_Parameter16', # 'GA_Parameter17',
               'GA_Parameter18',
               'GA_Parameter21', 'GA_Parameter22', 'GA_Parameter23', 'GA_Parameter24',
               'GA_Parameter25', 'GA_Parameter26', 'GA_Parameter27',
               'GA_Parameter28'
              'factor_Pitch_FATowDamper', 'factor_GenT_latTowDamper']
#searchWords = ['GA_Parameter11', 'GA_Parameter12', 'GA_Parameter13', 'factor_GenT_latTowDamper', 'factor_Pitch_FATowDamper']
#searchWords = ['GA_Parameter14', 'GA_Parameter15']
# searchWords = ['GA_Parameter4']
#searchWords = ['GA_Parameter11', 'GA_Parameter12', 'GA_Parameter13', 'GA_Parameter14', 'GA_Parameter15', 'GA_Parameter16', 'GA_Parameter17', 'GA_Parameter18']
#searchWords = ['GA_Parameter11', 'GA_Parameter13', 'GA_Parameter15', 'GA_Parameter17']
searchWords = ['pitchPGain', 'pitchIGain']


# DocString = "turb_15mps_6seeds_PSO_1P_n_2P_PID_IPC_lio_BPfilt_before_MBC_LP_filt_after_14_param"
# DocString = "full_CCC_without_ADC__turb_23mps_6seeds_PSO_1P_PID_IPC_lio_BPfilt_before_MBC_LP_filt_after_7_param"
#DocString = "turb_GPSO_1P_n_2P_PID_IPC_lio_BPfilt_before_MBC_LP_filt_after_14_param"
#DocString = "full_CCC_without_ADC__turb_07mps_6seeds_PSO_1P_2P_PID_MBC_IPC_lio_BPfilt_LP_filt_14_param"
DocString = "full_CCC_without_ADC__turb_11mps_6seeds_PSO_1P_2P_PID_MBC_IPC_lio_BPfilt_LP_filt_14_param"
DocString = "full_CCC_without_ADC_HubMx__turb_15mps_6seeds_SMA_1P_PID_MBC_IPC_BP_LPfilt_PLUS_FA_StS_damper_9_param"
#DocString = "full_CCC_without_ADC__turb_19mps_6seeds_PSO_1P_2P_PID_MBC_IPC_lio_BPfilt_LP_filt_14_param"
# DocString = "dummy"
#DocString = "CCC_without_ADC_HubMx__turb_15mps_6seeds_ALPSO_LIPC_1P2P_v3_gain_filt_damping_PLUS_FA_StS_damper_5_param"
DocString = "CCC_without_ADC_HubMx__turb_11mps_6seeds_fmin_search_LIPC_123PP_v1_gains_PLUS_FA_StS_damper_5_param"
#DocString = "CCC_only_Blade_My__turb_23mps_6seeds_fmin_search_LIPC_123PP_v1_gains_PLUS_FA_StS_damper_5_param"
#DocString = "TowerLoads_n_Power__turb_15mps_6seeds_fmin_search_FF_2P_CPC_for_2P_tower_FA_damp__2_param"
DocString = "CCC_without_ADC_HubMx__turb_15mps_6seeds_PSO__LARGE_14_param_search_LIPC_123PP_v1_gains_PLUS_FA_StS_damper"


DocString = "CCC_without_ADC_HubMx__turb_11mps_6seeds_fmin__yawControll_PI"

#addToRunFileNames = 'IPC15g'
#addToRunFileNames = 'CCC23g'
#addToRunFileNames = 'IPCxPg'
#addToRunFileNames = 'itr10'
#addToRunFileNames = '12P07g'
#addToRunFileNames = '12P11g'
#addToRunFileNames = '12P19g'
addToRunFileNames = 'SMA15g'
addToRunFileNames = '3AL15g'
addToRunFileNames = '0fin15g'
addToRunFileNames = 'B3ALPSO'
addToRunFileNames = 'BODExPS'

addToRunFileNames = 'yawC3fm'
fileEnd = '.$PJ'
Seed = 42

# Parameters
# SolutionIntervals = [[0.1, 0.8], [0.01, 0.08]]
# SolutionIntervals = [[-0.03, 0.03] for _ in range(8)]
# SolutionIntervals = [[-0.004, 0.0], [0.0, 0.013], [0.0, 0.004], [-0.004, 0.0]]
# SolutionIntervals = [[-0.002, +0.002], [-0.004, 0.004], [-0.002, 0.002], [-0.002, 0.002]]
# SolutionIntervals = [[-0.03, +0.03], [-0.1, 0.1], [-0.03, 0.03], [-0.03, 0.03],
#                      [-0.1, +0.1], [-0.04, 0.04], [-0.03, 0.03], [-0.03, 0.03]]
#SolutionIntervals = [[0.0, 0.05], [0.0, 0.02], [0, 360]]
SolutionIntervals = [[0.0, 0.1], [0.0, 0.8]] # , [-1, 1]]
# SolutionIntervals = [[0.0, 1.0]] # , [-1, 1]]
# SolutionIntervals = [[0.0, 1.0], [0.0, 1.0], [0.0, 1.0], [0.0, 1.0]]#, [1.4, 1.6], [0.0, 1.0], [1.3, 1.4], [0.0, 1.0]]  # , [-1, 1]]
SolutionIntervals = [[0.0, 0.05], [0.0, 0.05], [0.0, 0.05], [-20, 20], [0.1, 1.0]]#, [0.03, 0.15], [0.125, 0.4]]#, [0.0, 0.25], [0.0, 0.2]]
SolutionIntervals = [[0.0, 0.05], [0.0, 0.05], [0.0, 0.05], [-20, 20], [0.1, 1.0], [0.03, 0.15], [0.125, 0.4], [0.0, 0.25], [0.0, 0.2],  [0.1, 1.0], [0.03, 0.15], [0.125, 0.4], [0.0, 0.25], [0.0, 0.2]]


SolutionIntervals = [[0.0, 0.1], [0.0, 0.8]] # , [-1, 1]]


nBits = 4
nPopulation = 20  # better 10 # should be an odd number if elite is true
p_cross = 0.85
p_mutate = 0.01
Generations = 50
UseElite = True  # If set to true, the best run will be used in the next round

# Parameters to calculate DELs (damage equivalent loads)
time_total = 100.0  #time series length in s
deltat = 0.04       # time step length in s
nSectors = 12  # 24
eps = 0.001  # accuracy of factor to not divide by zero

Referenz_Frequency = 1.0  # Hz
Nreff = time_total * Referenz_Frequency  # 600 #
k = 4.0  # Woehler exponent for steel extremely important that this is a float!!!!
var_nbins = 100

max_rotation_speed = 0.785863055 * 1.08  # 2B101 rated in rad/s is 0.785863055 and in rpm is 7.504439388

CostShares = {'Blade_costs': 0.18, 'Tower_costs': 0.3483, 'DriveTrain_costs': 0.075, 'PitchSys_costs': 0.044,
                      'Generator_costs': 0.153, 'CoE_CAPEX_ratio': 3.7037}

nSeeds = len(ListOfBaselineFiles)
nParams = len(SolutionIntervals)

# Choose Flags
PrintDetails = False

#if len(SolutionIntervals) > 2:
if len(SolutionIntervals) != len(searchWords):
    print('Sizes to not match. Update the Costum Skript')
    #exit()
