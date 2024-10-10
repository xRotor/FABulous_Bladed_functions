""" ====================================================================================================================

                                      brute force optimization with a CCC matrix
                         ------------------------------------------------------------------

                        Idea is as simple as effective:
                        1. create a matrix of given size
                        2. evaluate matrix (incl. csv files)
                        3. potentially make new matrix around the minimal point or extend the rectangle if at bound
                        The optimum is based on the a control cost criterion (CCC)

        Optimality is not yet implemented! Possibly governed by the standard deviation of the closest rectangle?

==================================================================================================================== """
import copy

from ANSFAB__Utility import Utility, Bladed, BladedOptimizationFunction
from config import baselineFolder, MainFolder, param_key, max_rotor_speed_key, max_rotation_speed_bound, MainPathToBladedRuns #, nBlades, ListOfBaselineFiles, addToRunFileNames,
import matplotlib.pyplot as plt
from matplotlib import cm
import os

# define the bounds (min and max values of the evaluation space)
bounds_init = [[0, 0.4], [0, 0.2]]  # FA opt
bounds_init = [[0.1, 1], [0.005, 0.05]]  # PI opt
bounds_init = [[0.4, 0.7], [0.0, 0.02]]  # PI opt 0.55, 0.007
bounds_init = [[0.02, 0.2], [0.02, 0.2]]  #
bounds_init = [[0.0, 0.3], [0.0, 0.2]]  # FA n StS damp opt
bounds_init = [[-0.06, 0.3], [-0.1, 0.15]]  # FA n StS damp opt
bounds_init = [[0, 0.1], [-0.01, 0.01]]  # FA n StS damp opt
# bounds_init = [[0.1, 10], [0.01, 0.10]]  # pitch damp opt
# bounds_init = [[-1, 1], [0.01, 0.10]]  # pitch damp opt

# key for evaluation parameter
evaluation_key = 'CCC'
# evaluation_key = 'Tower_My_sector_max_DEL'
# evaluation_key = 'Power_mean'
# set flag to (not) allow to exceed the given boundaries if optimum seems to be outside of the given area
allow_exceeding_bounds = False
# define the matrix size in a x b format
matrix_size_init = [6, 6]
matrix_size_init = [7, 6]
matrix_size_init = [6, 6]
# plotting flag for 2D matrix
plotting_3D_surface = False

searchWords_list = [['pitchPGain', 'pitchIGain']]  # initial values: [0.43404, 0.03006]   [0.57695,0.01998]
searchWords_list = [['factor_Pitch_FATowDamper', 'factor_GenT_latTowDamper']]  # initial values: [0.43404, 0.03006]   [0.57695,0.01998]
# searchWords_list = [['GA_Parameter11', 'GA_Parameter12']]  # initial values: [[0, 10], [0, 0.15]]
# searchWords_list.append(['GA_Parameter13', 'GA_Parameter14'])  # initial values: [[0, 10], [0, 0.15]]
addToRunFileNames_list = [['_itr_P', '_I']]
addToRunFileNames_list = [['_itr_FA', '_StS']]
# addToRunFileNames_list = [['_ppitch_G', '_Hz']]
# addToRunFileNames_list.append(['_surge_G', '_Hz'])

ListOfBaselineFiles = [r"2B20Volt_v009_1_15mps.$PJ"]
ListOfBaselineFiles = [r"2B101v15_Mono_IPC_15mps.$PJ"]
#ListOfBaselineFiles = [r"3B20Volt_v009_15mps.$PJ"]

# DocStrings = ["_bruteForce__controller_PI_gains__3B20Volt_v008"]
DocStrings = ["_bruteForce__platform_pitch_damper_gain_n_Hz__2B20Volt_v009_1"]
DocStrings.append("_bruteForce__surge_damper_gain_n_Hz__2B20Volt_v009_1")


ListOfBaselineFiles = [r"2B101v15_Mono_IPC_15mps"]
DocStrings = ["_bruteForce__FA_damper_tuning_for_tower_itr__2B101v15_Monopile_with_IPC_v2"]
#ListOfBaselineFiles = [r"3B90_Mono_15mps"]
#DocStrings = ["_bruteForce__FA_damper_tuning_for_tower_itr__3B_Monopile"]

'''
searchWords_list = [['GA_Parameter13', 'GA_Parameter14']]  # initial values: [[0, 10], [0, 0.15]]
addToRunFileNames_list = [['_surge_G', '_Hz']]
DocStrings = ["_bruteForce__surge_damper_gain_n_Hz__3B20Volt_v008"]
ListOfBaselineFiles = [r"3B20Volt_v008_15mps_g0_.$PJ"]'''


def brute_force_optimization(cost_function, global_bounds, matrix_size=[], evaluation_key='CCC',
                             allow_exceeding_bounds=False, plotting_3D_surface=False, addToRunFileNames=[]):
    if not matrix_size:
        matrix_size = [10 for _ in global_bounds]
    print('# ------- preparing parameter matrix grid point --------- #')
    params = Utility().prepare_n_dimensional_grid_points(global_bounds, matrix_size)

    # convergence_reached = False
    initial_matrix_size = matrix_size
    zoomed_in = 0
    while zoomed_in < 2:
        print('# -------------- evaluating cost function ---------------- #')
        CCCs = cost_function.BladedOptimizationFunction(params)
        # CCCs = [1 for _ in range(len(params))]#CCCs[5] = 0.1

        print('# ---------------- postprocessing data ------------------- #')
        # read all data in from csv file (to be more robust and ease debugging)
        results_list_dict = Utility().readListDictFromCSV(documentation_path)
        params_from_file = []
        evaluation_values = []
        max_rotor_speeds = []
        max_rotor_speeds_out_of_bound = []
        opt_value = 9e99  # results_list_dict[0].get(evaluation_key)
        for dict in results_list_dict:
            params_from_file.append([float(param) for param in dict.get(param_key).split(',')])
            evaluation_values.append(float(dict.get(evaluation_key)))
            max_rotor_speeds.append(float(dict.get(max_rotor_speed_key)))
            if max_rotor_speeds[-1] > max_rotation_speed_bound:
                max_rotor_speeds_out_of_bound.append(max_rotor_speeds[-1])
            else:
                if evaluation_values[-1] < opt_value:
                    opt_value = evaluation_values[-1]
        opt_params = params_from_file[evaluation_values.index(opt_value)]
        # filter values where the maximum rotation speed is out of bounds
        out_of_bounds_values = [evaluation_values[max_rotor_speeds.index(rotation_speed)] for rotation_speed in
                                max_rotor_speeds_out_of_bound]
        out_of_bounds_params = [params_from_file[max_rotor_speeds.index(rotation_speed)] for rotation_speed in
                                max_rotor_speeds_out_of_bound]
        print('<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
        print('found current optimum from', evaluation_key, '=', opt_value, 'for params', opt_params)
        print('<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')

        if plotting_3D_surface and len(matrix_size) == 2:
            # plt = Utility().plot_threedimensional_data(X, Y, Z, 0, addToRunFileNames[0].split('_')[-1],
            #                                            addToRunFileNames[1].split('_')[-1], 'CCC')
            print('# ------------------ visualizing data -------------------- #')
            # plotting 3D surface
            X = [param_tuple[0] for param_tuple in params_from_file]
            Y = [param_tuple[1] for param_tuple in params_from_file]
            Z = evaluation_values
            Z = [min(i, min(evaluation_values) * 1.2) for i in evaluation_values]

            fig = plt.figure()
            ax = fig.add_subplot(111, projection="3d")  # , elev=elev, azim=azim)
            surf = ax.plot_trisurf(X, Y, Z, cmap=cm.get_cmap('jet_r'),  # cmap='inferno_r', #
                                   alpha=0.8, linewidth=0.1, edgecolor='grey', antialiased=True, vmin=min(Z),
                                   vmax=min(min(Z) * 1.2, max(Z)))
            ax.set_zlim3d(min(Z), min(min(Z) * 1.2, max(Z)))
            # fig.colorbar(surf, shrink=0.5, aspect=5)

            # adding scatter plot for out of bounds values to 3D surface
            X = [param_tuple[0] for param_tuple in out_of_bounds_params]
            Y = [param_tuple[1] for param_tuple in out_of_bounds_params]
            Z = out_of_bounds_values
            ax.plot(X, Y, Z, 'o', color='red')

            if addToRunFileNames:
                ax.set_xlabel(addToRunFileNames[0].split('_')[-1])
                ax.set_ylabel(addToRunFileNames[1].split('_')[-1])
            ax.set_title(evaluation_key)

            plt.savefig(documentation_path.split('.')[0] + '.pdf')
            plt.pause(1)
            plt.show(block=False)
            plt.pause(1)

        print('# ----------------- preparing new grid ------------------- #')
        step_sizes = []
        lowest_value_at_border = False
        for idx, bound in enumerate(global_bounds):
            step_sizes.append((bound[1] - bound[0]) / (matrix_size[idx] - 1))
            # check if optimal parameters are at lower bound
            if opt_params[idx] == bound[0] and allow_exceeding_bounds:
                new_grid_line = opt_params[idx] - step_sizes[-1]
                lowest_value_at_border = True
                bound_side = 0
            # check if optimal parameters are at upper bound
            if opt_params[idx] == bound[1] and allow_exceeding_bounds:
                new_grid_line = opt_params[idx] + step_sizes[-1]
                lowest_value_at_border = True
                bound_side = 1
            # prepare new line of values if optimum is at a bound
            if lowest_value_at_border:
                print('optimum has been at a bound. Will extend grid.')
                temp_matrix_size = copy.deepcopy(matrix_size)
                temp_bounds = copy.deepcopy(global_bounds)
                # get one dimension temporary out of the matrix_size and increase the basic matrix size by one
                matrix_size[idx] = temp_matrix_size.pop(idx) + 1
                # get one dimension temporary out of the bounds
                temp_bounds.pop(idx)
                # increase the bounds by one step size
                global_bounds[idx][bound_side] = new_grid_line
                # prepare one new line outside of the previous bounds to increase the previous matrix
                params = Utility().prepare_n_dimensional_grid_points(temp_bounds, temp_matrix_size)
                [param.insert(idx, new_grid_line) for param in params]
                break

        if not lowest_value_at_border:
            zoomed_in += 1
            # prepare smaller grid
            matrix_size = initial_matrix_size
            use_spread_around_optimum = True
            if use_spread_around_optimum:
                # make sure that the matrix size consists only of even values for a nice grid spread around optimum
                matrix_size = [size if (size % 2) == 0 else size - 1 for size in matrix_size]
            # define bounds that are inside the previous matrix subgrid
            local_bounds = [[opt_params[idx] - step_sizes[idx] * (1 - 1 / size),
                       opt_params[idx] + step_sizes[idx] * (1 - 1 / size)]
                      for idx, size in enumerate(matrix_size)]
            params = Utility().prepare_n_dimensional_grid_points(local_bounds, matrix_size)

        print('new params have been prepared, will refine matrix with: ', params)
        # convergence_reached = True
    return opt_params, opt_value





""" ====================================================================================================================

                                            Main Script starts here
                         ------------------------------------------------------------------

                          

==================================================================================================================== """
E_multipliers = [i / 10 for i in range(10, 50, 10)]
E_multipliers = [1 * pow(1.06, i-30) for i in range(120)]
#E_multipliers = [1 * pow(1.06, i*3) for i in range(20)]
E_multipliers = [1 * pow(1.06, i*3-30) for i in range(30)]
#E_multipliers = [i / 10 for i in range(26, 52, 2)]
OptFiles = []
documentation_summary = []
for multiplier in E_multipliers:

    # ChangeNameDicts = [{'WORD': '.', 'EXCHANGE': ('_E%.3fE11' % (2 * multiplier)).replace('.', '_')}] #USE THIS FOR FOWTs
    ChangeNameDicts = [{'WORD': '.', 'EXCHANGE': ('_E%.3fE11' % (2.1 * multiplier)).replace('.', '_')}]
    # ChangeDicts = Bladed().change_dict_for_tower_steel_youngs_modulus(multiplier)
    ChangeDicts = Bladed().change_dict_for_tower_steel_youngs_modulus__v2(multiplier, os.path.join(baselineFolder, ListOfBaselineFiles[0]),
                                                                          n_tower_sections=14)  # =9 for FOWTs

    # ListOfBaselineFiles_itr = ListOfBaselineFiles
    ListOfBaselineFiles_itr, outfolder = Utility().manipulatePRJfiles(ListOfBaselineFiles_local=ListOfBaselineFiles,
                                                                         ChangeDicts=ChangeDicts,
                                                                         ChangeNameDicts=ChangeNameDicts,
                                                                         infolder=baselineFolder,
                                                                         outfolder=baselineFolder)

    print('\n\nStarting next cycle with baseline file', ListOfBaselineFiles_itr, ' and tower steel youngs modulus multiplier of ', multiplier)

    if OptFiles:
        Bladed().AutoRunBatch(outfolder, ListOfBaselineFiles_itr + OptFiles)
    #Bladed().AutoRunBatch(outfolder, ListOfBaselineFiles_itr + OptFiles)

    for idx, searchWords in enumerate(searchWords_list):
        # prepare the documentation path
        from datetime import datetime

        documentation_path = MainPathToBladedRuns + '\\' + datetime.today().strftime('%Y_%m_%d__') + DocStrings[
            idx] + '_Documentary.csv'
        # documentation_path = r'H:\BladedWS\FOWTs\Optimize_FA_Damper_2B20Volt_v009\bruteForce\2023_04_26___bruteForce__FA_dampers_gain_n_Hz__2B20Volt_v009_1_Documentary.csv'
        # documentation_path = r'H:\BladedWS\FOWTs\Optimize_PI_gains_2B20Volt_v009\bruteForce\2023_04_27___bruteForce__controller_PI_gains__2B20Volt_v009_1_Documentary.csv'

        # load and evaluate cost function
        cost_function = BladedOptimizationFunction(ListOfBaselineFiles_itr, searchWords, addToRunFileNames_list[idx],
                                                   documentation_path)
        opt_params, opt_value = brute_force_optimization(cost_function, bounds_init, matrix_size_init, evaluation_key,
                                                         allow_exceeding_bounds, plotting_3D_surface,
                                                         addToRunFileNames=addToRunFileNames_list[idx])

        # create new baseline_file for next round
        ChangeNameDicts = [{'WORD': '.', 'EXCHANGE': '_opt'}]
        OptFiles, outfolder = Utility().manipulatePRJfiles(opt_params, idx, searchWords_local=searchWords,
                                                           ListOfBaselineFiles_local=ListOfBaselineFiles_itr,
                                                           addToRunFileNames_local=['' for _ in opt_params],
                                                           infolder=baselineFolder, outfolder=baselineFolder)

        print('\n\n<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
        print('found final optimum from', evaluation_key, '=', opt_value, 'for params', opt_params)
        print('<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n\n')

        documentation_path = MainFolder + '\\' + datetime.today().strftime('%Y_%m_%d__') + DocStrings[idx] + '_Documentary_summary.csv'
        documentation_summary.append({'ListOfBladedJobs': OptFiles[0]})
        for key_idx, opt_key in enumerate(searchWords):
            documentation_summary[-1][opt_key] = opt_params[key_idx]
        Utility().writeListDictToCSV(documentation_summary, documentation_path)

        # Bladed().AutoRunBatch(outfolder, OptFiles)
        # ListOfBaselineFiles_itr = OptFiles

Bladed().AutoRunBatch(outfolder, OptFiles)
plt.show()
