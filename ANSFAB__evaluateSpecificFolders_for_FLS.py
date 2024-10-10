import os
from datetime import datetime
from math import copysign
from ANSFAB__Utility import Utility
from config import ULS_Searching, FLS_Searching, FOWTs, yaw_bearing_diameter, p_yaw_bearing, pitch_bearing_diameter__two_bladed, pitch_bearing_diameter__three_bladed, nSectors
from main__ULS_summarizer_incl_each_DLC_ULS__all_new import BladedPostProcess
from numpy import std
import numpy as np
import math
from time import time

import scipy.signal

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

def evaluateFolder_for_ULS_or_FLS(folder, search_kind = 'ULS', search_in_subfolders=True, prefilter_ULS_folders=False):
    if search_kind == 'ULS':
        Searches = ULS_Searching
    elif search_kind == 'FLS':
        Searches = FLS_Searching

    if FOWTs:
        if not folder.find('FOWT') != -1:
            print('\n---> WARNING! THE FOWTs FLAG IS SET TRUE; BUT NO FOWT STRING IS DETECTED!!! <---\n')
    else:
        if folder.find('FOWT') != -1:
            print('\n---> WARNING! THE FOWTs FLAG IS SET FALSE; BUT A FOWT STRING IS DETECTED!!! <---\n')

    documentation_path = os.path.join(folder, folder.replace('\\\\', '\\').split('\\')[-2] + '__'
                                      + datetime.today().strftime('%Y_%m_%d__') + '_' + search_kind + '_new.csv')
    print('Results will be stored to --> ', documentation_path)

    #subfolders = [folder[0].replace('\\\\', '\\') for folder in os.walk(folder) if not folder.find('ignore') != -1]
    subfolders = [folder[0].replace('\\\\', '\\') for folder in os.walk(folder)]
    print('found folders ---> ', subfolders)

    if search_kind == 'ULS' and prefilter_ULS_folders:
        filtered_subfolders = []
        for subfolder in subfolders:
            if (not "DLC12" in subfolder and not "ignore" in subfolder) or ("DLC12" in subfolder and "ULS" in subfolder):
                filtered_subfolders.append(subfolder)
        subfolders = filtered_subfolders
        print('filtered folders list ---> ', subfolders)

    Documentation = []
    # collect all runs in the desired folder
    ListOfBladedJobs = []
    for RunFolderName in subfolders:
        [ListOfBladedJobs.append(filename.replace('.$05', '.$PJ')) for filename in
         Utility().return_run_files_in_folder(RunFolderName, fileEnd='*.$05') if filename]
    amount_of_runs = len(ListOfBladedJobs)
    print('found', amount_of_runs, 'runs')

    leveled_results_list_dict = []
    total_time = 0
    for Job_idx, BladedJob_path in enumerate(ListOfBladedJobs):
        time_at_loop_start = time()
        print('searching for', search_kind, 'in run', Job_idx, '---> ', BladedJob_path)
        BladedJob = BladedJob_path.split('\\')[-1]
        RunFolder = BladedJob_path.replace(BladedJob, '')
        leveled_results_list_dict.append({'ListOfBladedJobs': BladedJob_path})

        nmbr_removed_items = 0
        for Search_idx, Search in enumerate(Searches[:]):  # [:] forces to create a copy of the list to avoid
            Search_idx = Search_idx - nmbr_removed_items            # issues when removing items inside the loop
            if not Job_idx:  # only used in first run evaluation
                if not Search_idx:  # only used in the very first loop
                    print('search general time series file information in run', BladedJob, 'in folder', RunFolder)
                # search in the first run file for further information about the result files
                [fileEnd, idx, DIMENS] = Utility().collectTimeSeriesStructureFromBladedFiles(RunFolder=RunFolder,
                                                                BladedJob=BladedJob, VariableName=Search.get('VARIAB'))

                if not fileEnd:
                    print('   cannot find VARIAB', Search.get('VARIAB'), '  Will skip this loop and remove the key', Search.get('Key'))
                    del Searches[Search_idx]
                    nmbr_removed_items += 1
                    continue

                print('   found VARIAB', Search.get('VARIAB'), 'for key', Search.get('Key'),
                  'in file *', fileEnd, 'at index', idx, 'with dimensions', DIMENS)

                Searches[Search_idx]['FileEnd'] = fileEnd
                Searches[Search_idx]['IDX'] = idx
                Searches[Search_idx]['DIMENS'] = DIMENS

            fileEnd = Search.get('FileEnd')
            idx = Search.get('IDX')
            DIMENS = Search.get('DIMENS')

            if Search.get('NodePos')[0] == 'ALL':
                if len(DIMENS) == 3:
                    Searches[Search_idx]['NodePos'] = [i+1 for i in range(int(DIMENS[1]))]
                else:
                    Searches[Search_idx]['NodePos'] = [-1]

            # loop over the positions if many or all positions of one component e.g. mooring lines should be evaluated:
            for position_idx, position_of_node in enumerate(Search.get('NodePos')):
                #try:
                TimeSeries = Utility().readTimeSeriesData(RunFolder=RunFolder, BladedJob=BladedJob, fileEnd=fileEnd,
                                                          idx=idx, DIMENS=DIMENS, pos_of_node=position_of_node)
                #except OSError:  TimeSeries = [0]  # [-1]
                if TimeSeries == [0]:  # [-1]
                    print(' >>>>>> WARNING <<<<<< Time Series of ', Search.get('VARIAB'), ' does not exist. Will set ULS value to 0.')
                    # leveled_results_list_dict[-1][Search.get('Key')] = 0
                    final_desired_value = 0
                    continue

                if not Search_idx:
                    [time_total, deltat] = Utility().calcTotalTimeAndDeltat(RunFolder, BladedJob)

                search_mode = Search.get('Desired')

                # ----------------------------------------> FLS Search <-----------------------------------------------#
                if search_mode == 'DEL':
                    final_desired_value = desired_value = Utility().calcDELfromTimeSeries(TimeSeries, Search.get('k_SN'))
                elif search_mode == 'DEL_sector':
                    # get the time series of the orthogonal moment for the calculation of the maximum DEL sector
                    [fileEnd, idx, DIMENS] = Utility().collectTimeSeriesStructureFromBladedFiles(
                        RunFolder=RunFolder, BladedJob=BladedJob, VariableName=Search.get('Orthogonal_VARIAB'))
                    TimeSeries_orthogonal = Utility().readTimeSeriesData(RunFolder=RunFolder, BladedJob=BladedJob,
                                                  fileEnd=fileEnd, idx=idx, DIMENS=DIMENS, pos_of_node=position_of_node)
                    final_desired_value = desired_value = Utility().calcWorstDELsector(TimeSeries, TimeSeries_orthogonal)

                elif search_mode == 'STD':
                    final_desired_value = desired_value = std(TimeSeries)

                elif search_mode == 'MEAN':
                    final_desired_value = desired_value = sum(TimeSeries)/len(TimeSeries)

                elif search_mode == 'ADC':
                    final_desired_value = desired_value = max(TimeSeries)

                elif search_mode == 'LDC':  # load duty cycle:
                    [fileEnd, idx, DIMENS] = Utility().collectTimeSeriesStructureFromBladedFiles(
                        RunFolder=RunFolder, BladedJob=BladedJob, VariableName=Search.get('Pitch_Velo_VARIAB'))
                    pitch_velo_TS = Utility().readTimeSeriesData(RunFolder=RunFolder, BladedJob=BladedJob,
                        fileEnd=fileEnd, idx=idx, DIMENS=DIMENS, pos_of_node=position_of_node)
                    Pitch_LDC = 0  # pitch load duty cycle
                    for i in range(len(TimeSeries) - 1):
                        Pitch_LDC = Pitch_LDC + abs(TimeSeries[i] * pitch_velo_TS[i]) * deltat  # no real difference
                    final_desired_value = desired_value = Pitch_LDC

                elif search_mode == 'P_ea_pitch':
                    P_ea, N_ave, theta_e = Utility().calcPitchBearingDamage(RunFolder, BladedJob)
                    final_desired_value = P_ea
                    # leveled_results_list_dict[-1]['N_ave_ops'] = N_ave
                    # leveled_results_list_dict[-1]['theta_e'] = theta_e

                elif search_mode == 'P_ea_yaw':  # calculating the yaw bearing load according to NREL's DG03 (https://www.nrel.gov/docs/fy10osti/42362.pdf)
                    [fileEnd, idx, DIMENS] = Utility().collectTimeSeriesStructureFromBladedFiles(RunFolder=RunFolder,
                        BladedJob=BladedJob, VariableName=Search.get('VARIAB').replace('Mxy','Fxy'))
                    TS_yaw_radial_force = Utility().readTimeSeriesData(RunFolder=RunFolder,
                        BladedJob=BladedJob, fileEnd=fileEnd, idx=idx, DIMENS=DIMENS, pos_of_node=position_of_node)
                    [fileEnd, idx, DIMENS] = Utility().collectTimeSeriesStructureFromBladedFiles(RunFolder=RunFolder,
                        BladedJob=BladedJob, VariableName=Search.get('VARIAB').replace('Mxy', 'Fz'))
                    TS_yaw_axial_force = Utility().readTimeSeriesData(RunFolder=RunFolder,
                        BladedJob=BladedJob, fileEnd=fileEnd, idx=idx, DIMENS=DIMENS, pos_of_node=position_of_node)
                    P_ea_k_yaw_TS = []
                    for time_step, yaw_overturning_moment in enumerate(TimeSeries):
                        P_ea_k_yaw_TS.append(0.75 * abs(TS_yaw_radial_force[time_step]) + abs(TS_yaw_axial_force[time_step])
                                             + 2 * abs(yaw_overturning_moment) / yaw_bearing_diameter)

                    final_desired_value = desired_value = Utility().calcBearingDamageFromTimeSeriesForConstSpeed(P_ea_k_yaw_TS, time_total, deltat, p=p_yaw_bearing)

                    # tidy up!
                    del TS_yaw_radial_force, TS_yaw_axial_force, P_ea_k_yaw_TS

                elif search_mode == 'P_ea_first_main_bearing':  # calculating by ISO 281
                    # adding all rotating hub moments, forces for approximating the rotating bearing load:
                    TS_hub_My_rot = TimeSeries
                    TS_hub_Mz_rot = Utility().readTimeSeriesDataFromScratch(RunFolder, BladedJob, 'Rotating hub Mz')
                    TS_hub_Fx_rot = Utility().readTimeSeriesDataFromScratch(RunFolder, BladedJob, 'Rotating hub Fx')  # axial; rotation equals stationary
                    TS_hub_Fy_rot = Utility().readTimeSeriesDataFromScratch(RunFolder, BladedJob, 'Rotating hub Fy')
                    TS_hub_Fz_rot = Utility().readTimeSeriesDataFromScratch(RunFolder, BladedJob, 'Rotating hub Fz')
                    TS_rotor_azimuth_rad = Utility().readTimeSeriesDataFromScratch(RunFolder, BladedJob, 'Rotor azimuth angle')
                    # same with stationary moments and forces:
                    TS_hub_My_stat = Utility().readTimeSeriesDataFromScratch(RunFolder, BladedJob, 'Stationary hub My')
                    TS_hub_Mz_stat = Utility().readTimeSeriesDataFromScratch(RunFolder, BladedJob, 'Stationary hub Mz')
                    TS_hub_Fy_stat = Utility().readTimeSeriesDataFromScratch(RunFolder, BladedJob, 'Stationary hub Fy')
                    TS_hub_Fz_stat = Utility().readTimeSeriesDataFromScratch(RunFolder, BladedJob, 'Stationary hub Fz')
                    # generator rotor weight and levers
                    if BladedJob.find('3B') != -1:
                        generator_rotor_weight_in_N = 207607.34 * 9.81  # 3B generator rotor weight force
                    else:
                        generator_rotor_weight_in_N = 187987.07 * 9.81   # 2B generator rotor weight force
                    x1_lever_rotor_to_first_main_bearing_in_m = 4.64
                    x2_lever_first_to_second_main_bearing_in_m = 1.38
                    x3_lever_generator_rotor_to_first_main_bearing_in_m = 1.04
                    # main_bearing_diameter = 3.35
                    # main bearing properties (assumed as 20 degree contact angle, but should evaluate 10 and 30 degree in the future as well)
                    deg_to_rad = 0.01745329251994329576
                    alpha_contact_angle = 20 * deg_to_rad
                    e_main_bearing = 1.5 * math.tan(alpha_contact_angle)
                    cot_alpha_contact_angle = 1/math.tan(alpha_contact_angle)

                    P_ea_k_main_yz_TS = []
                    P_ea_k_main_y_TS_rot = []
                    P_ea_k_main_z_TS_rot = []
                    P_ea_k_main_y_TS_stat = []
                    P_ea_k_main_z_TS_stat = []
                    for step in range(len(TimeSeries)):
                        # rotating Fz at bearing
                        TS_hub_Fz_rot_step = -1 / x2_lever_first_to_second_main_bearing_in_m * (TS_hub_My_rot[step] + TS_hub_Fz_rot[step]*(x1_lever_rotor_to_first_main_bearing_in_m + x2_lever_first_to_second_main_bearing_in_m)
                                                - generator_rotor_weight_in_N * (x3_lever_generator_rotor_to_first_main_bearing_in_m+x2_lever_first_to_second_main_bearing_in_m) * math.cos(TS_rotor_azimuth_rad[step]))
                        # rotating Fy at bearing
                        TS_hub_Fy_rot_step = - 1 / x2_lever_first_to_second_main_bearing_in_m * (-TS_hub_Mz_rot[step] + TS_hub_Fy_rot[step] * (x1_lever_rotor_to_first_main_bearing_in_m + x2_lever_first_to_second_main_bearing_in_m)
                                                - generator_rotor_weight_in_N * (x3_lever_generator_rotor_to_first_main_bearing_in_m + x2_lever_first_to_second_main_bearing_in_m) * math.sin(TS_rotor_azimuth_rad[step]))
                        # stationary Fz at bearing (weight is adds a constant force)
                        TS_hub_Fz_stat_step = -1 / x2_lever_first_to_second_main_bearing_in_m * (TS_hub_My_stat[step] + TS_hub_Fz_stat[step] * (x1_lever_rotor_to_first_main_bearing_in_m + x2_lever_first_to_second_main_bearing_in_m)
                                    - generator_rotor_weight_in_N * (x3_lever_generator_rotor_to_first_main_bearing_in_m + x2_lever_first_to_second_main_bearing_in_m))
                        # stationary Fy at bearing (weight adds no force)
                        TS_hub_Fy_stat_step = - 1 / x2_lever_first_to_second_main_bearing_in_m * (-TS_hub_Mz_stat[step] + TS_hub_Fy_stat[step] * (x1_lever_rotor_to_first_main_bearing_in_m + x2_lever_first_to_second_main_bearing_in_m))

                        # resulting yz axial load (POTENTIALLY ONLY THE RESULT LOAD IS NEEDED; THE DIRECTIONS WILL FOR NOW BE KEPT FOR INTEREST)
                        TS_hub_Fyz_rot_step = math.sqrt(pow(TS_hub_Fy_rot_step, 2) + pow(TS_hub_Fz_rot_step, 2))
                        F_axial_step = abs(TS_hub_Fx_rot[step])
                        # calculate resulting dynamic equivalent main bearing load
                        if F_axial_step/TS_hub_Fyz_rot_step < e_main_bearing:
                            X = 1
                            Y = 0.45 * cot_alpha_contact_angle
                        else:
                            X = 0.67
                            Y = 0.67 * cot_alpha_contact_angle
                        P_ea_k_main_yz_TS.append(X * F_axial_step + Y * TS_hub_Fyz_rot_step)

                        # calculate rotating dynamic equivalent main bearing loads in y and z direction
                        if F_axial_step/TS_hub_Fy_rot_step < e_main_bearing:
                            X = 1
                            Y = 0.45 * cot_alpha_contact_angle
                        else:
                            X = 0.67
                            Y = 0.67 * cot_alpha_contact_angle
                        P_ea_k_main_y_TS_rot.append(X * F_axial_step + Y * abs(TS_hub_Fy_rot_step))
                        if F_axial_step/TS_hub_Fz_rot_step < e_main_bearing:
                            X = 1
                            Y = 0.45 * cot_alpha_contact_angle
                        else:
                            X = 0.67
                            Y = 0.67 * cot_alpha_contact_angle
                        P_ea_k_main_z_TS_rot.append(X * F_axial_step + Y * abs(TS_hub_Fz_rot_step))

                        # calculate stationary dynamic equivalent main bearing loads in y and z direction (axial load is the same as rotating)
                        if F_axial_step/TS_hub_Fy_stat_step < e_main_bearing:
                            X = 1
                            Y = 0.45 * cot_alpha_contact_angle
                        else:
                            X = 0.67
                            Y = 0.67 * cot_alpha_contact_angle
                        P_ea_k_main_y_TS_stat.append(X * F_axial_step + Y * abs(TS_hub_Fy_stat_step))
                        if F_axial_step/TS_hub_Fz_stat_step < e_main_bearing:
                            X = 1
                            Y = 0.45 * cot_alpha_contact_angle
                        else:
                            X = 0.67
                            Y = 0.67 * cot_alpha_contact_angle
                        P_ea_k_main_z_TS_stat.append(X * F_axial_step + Y * abs(TS_hub_Fz_stat_step))

                    P_ea_main_y_TS_rot = Utility().calcBearingDamageFromTimeSeriesForConstSpeed(P_ea_k_main_y_TS_rot, time_total, deltat, p=Search.get('k_SN'))
                    P_ea_main_z_TS_rot = Utility().calcBearingDamageFromTimeSeriesForConstSpeed(P_ea_k_main_z_TS_rot, time_total, deltat, p=Search.get('k_SN'))
                    P_ea_main_y_TS_stat = Utility().calcBearingDamageFromTimeSeriesForConstSpeed(P_ea_k_main_y_TS_stat, time_total, deltat, p=Search.get('k_SN'))
                    P_ea_main_z_TS_stat = Utility().calcBearingDamageFromTimeSeriesForConstSpeed(P_ea_k_main_z_TS_stat, time_total, deltat, p=Search.get('k_SN'))
                    # see which direction is worst. can potentially be extended by sector wise evaluation (BETTER ACCUMULATE AS RESULTING yz VECTOR TO STAY CONSERVATIVE??)
                    final_desired_value = desired_value = max(abs(P_ea_main_y_TS_stat), abs(P_ea_main_z_TS_stat)) # , abs(P_ea_main_y_TS_rot), abs(P_ea_main_z_TS_rot))

                    leveled_results_list_dict[-1][Search.get('Key') + '_y_rot'] = P_ea_main_y_TS_rot
                    leveled_results_list_dict[-1][Search.get('Key') + '_z_rot'] = P_ea_main_z_TS_rot
                    leveled_results_list_dict[-1][Search.get('Key') + '_y_stat'] = P_ea_main_y_TS_stat
                    leveled_results_list_dict[-1][Search.get('Key') + '_z_stat'] = P_ea_main_z_TS_stat

                    # tidy up!
                    del P_ea_k_main_yz_TS, P_ea_k_main_y_TS_rot, P_ea_k_main_z_TS_rot, P_ea_k_main_y_TS_stat, P_ea_k_main_z_TS_stat, TS_hub_My_rot, \
                        TS_hub_Mz_rot, TS_hub_Fx_rot, TS_hub_Fy_rot, TS_hub_Fz_rot, TS_rotor_azimuth_rad, TS_hub_My_stat, TS_hub_Mz_stat, TS_hub_Fy_stat, TS_hub_Fz_stat

                elif search_mode == 'DEL_sector_rot_main_shaft':
                    # test, if the time series are still in the storage
                    # if not 'TS_hub_My_rot' in globals():  # never triggered...  also not: in locals():

                    # adding all rotating hub moments, forces for approximating the rotating bearing load:
                    TS_hub_My_rot = TimeSeries
                    TS_hub_Mz_rot = Utility().readTimeSeriesDataFromScratch(RunFolder, BladedJob, 'Rotating hub Mz')
                    TS_hub_Fy_rot = Utility().readTimeSeriesDataFromScratch(RunFolder, BladedJob, 'Rotating hub Fy')
                    TS_hub_Fz_rot = Utility().readTimeSeriesDataFromScratch(RunFolder, BladedJob, 'Rotating hub Fz')
                    TS_rotor_azimuth_rad = Utility().readTimeSeriesDataFromScratch(RunFolder, BladedJob,'Rotor azimuth angle')
                    # generator rotor weight and levers
                    if BladedJob.find('3B') != -1:
                        generator_rotor_weight_in_N = 207607.34 * 9.81  # 3B generator rotor weight force
                    else:
                        generator_rotor_weight_in_N = 187987.07 * 9.81  # 2B generator rotor weight force
                    x1_lever_rotor_to_first_main_bearing_in_m = 4.64
                    x3_lever_generator_rotor_to_first_main_bearing_in_m = 1.04

                    TS_main_shaft_My_rot = []
                    TS_main_shaft_Mz_rot = []
                    for step in range(len(TimeSeries)):
                        TS_main_shaft_My_rot.append(TS_hub_My_rot[step] + TS_hub_Fz_rot[step] * x1_lever_rotor_to_first_main_bearing_in_m \
                            - generator_rotor_weight_in_N * x3_lever_generator_rotor_to_first_main_bearing_in_m * math.cos(TS_rotor_azimuth_rad[step]))
                        TS_main_shaft_Mz_rot.append(TS_hub_Mz_rot[step] - TS_hub_Fy_rot[step] * x1_lever_rotor_to_first_main_bearing_in_m \
                            + generator_rotor_weight_in_N * x3_lever_generator_rotor_to_first_main_bearing_in_m * math.sin(TS_rotor_azimuth_rad[step]))

                    leveled_results_list_dict[-1][Search.get('Key') + '_My'] = Utility().calcDELfromTimeSeries(TS_main_shaft_My_rot, Search.get('k_SN'))
                    leveled_results_list_dict[-1][Search.get('Key') + '_Mz'] = Utility().calcDELfromTimeSeries(TS_main_shaft_Mz_rot, Search.get('k_SN'))
                    final_desired_value = desired_value = Utility().calcWorstDELsector(TS_main_shaft_My_rot, TS_main_shaft_Mz_rot)

                    # tidy up!
                    del TS_main_shaft_My_rot, TS_main_shaft_Mz_rot, TS_rotor_azimuth_rad, TS_hub_Fz_rot, TS_hub_Fy_rot, TS_hub_Mz_rot, TS_hub_My_rot

                    '''elif search_mode == 'DEL_sector_HP_filtered':
                    # get the time series of the orthogonal moment for the calculation of the maximum DEL sector
                    [fileEnd, idx, DIMENS] = Utility().collectTimeSeriesStructureFromBladedFiles(
                        RunFolder=RunFolder, BladedJob=BladedJob, VariableName=Search.get('Orthogonal_VARIAB'))
                    TimeSeries_orthogonal = Utility().readTimeSeriesData(RunFolder=RunFolder, BladedJob=BladedJob,
                                                  fileEnd=fileEnd, idx=idx, DIMENS=DIMENS, pos_of_node=position_of_node)

                    # filter signals
                    FilterOrderN = 2
                    sos = scipy.signal.butter(FilterOrderN, Wn=Search.get('filter_HP_Hz'), fs=1 / deltat, btype='hp', output='sos')  # high pass
                    # sos = scipy.signal.butter(FilterOrderN, Wn, fs=fs, btype='bandpass', output='sos')
                    TimeSeries_filtered = scipy.signal.sosfilt(sos, TimeSeries)
                    TimeSeries = [TimeSeries_filtered[9] for _ in TimeSeries_filtered[:9]] + [i for i in TimeSeries_filtered[9:]]  # smoothens the initial offset
                    TimeSeries_filtered = scipy.signal.sosfilt(sos, TimeSeries_orthogonal)
                    TimeSeries_orthogonal = [TimeSeries_filtered[9] for _ in TimeSeries_filtered[:9]] + [i for i in TimeSeries_filtered[9:]]  # smoothens the initial offset

                    final_desired_value = desired_value = Utility().calcWorstDELsector(TimeSeries, TimeSeries_orthogonal)'''















                # ----------------------------------------> ULS Search <-----------------------------------------------#
                else:  # ULS search
                    try:
                        if search_mode == 'yaw_bearing_ULS' or search_mode == 'pitch_bearing_ULS':  # calculating the yaw bearing load according to NREL's DG03 (https://www.nrel.gov/docs/fy10osti/42362.pdf) Note, that a bearing load angle of 45 deg is assumed and its representive for a bearing with only ine roller
                            [fileEnd, idx, DIMENS] = Utility().collectTimeSeriesStructureFromBladedFiles(RunFolder=RunFolder,
                                BladedJob=BladedJob, VariableName=Search.get('VARIAB').replace('Mxy', 'Fxy'))
                            TS_yaw_radial_force = Utility().readTimeSeriesData(RunFolder=RunFolder,
                                BladedJob=BladedJob, fileEnd=fileEnd, idx=idx, DIMENS=DIMENS, pos_of_node=position_of_node)
                            [fileEnd, idx, DIMENS] = Utility().collectTimeSeriesStructureFromBladedFiles(
                                RunFolder=RunFolder, BladedJob=BladedJob, VariableName=Search.get('VARIAB').replace('Mxy', 'Fz'))
                            TS_yaw_axial_force = Utility().readTimeSeriesData(RunFolder=RunFolder,
                                BladedJob=BladedJob, fileEnd=fileEnd, idx=idx, DIMENS=DIMENS, pos_of_node=position_of_node)
                            Q_max_TS = []
                            if search_mode.find('yaw') != -1:
                                bearing_diameter = yaw_bearing_diameter
                            elif search_mode.find('pitch') != -1:
                                if BladedJob.find('3B') != -1:
                                    bearing_diameter = pitch_bearing_diameter__three_bladed
                                else:
                                    bearing_diameter = pitch_bearing_diameter__two_bladed
                            for time_step, yaw_overturning_moment in enumerate(TimeSeries):
                                Q_max_TS.append(0.55 * (2 * abs(TS_yaw_radial_force[time_step]) + abs(TS_yaw_axial_force[time_step])
                                                + 4 * abs(yaw_overturning_moment) / bearing_diameter) * 2 / np.sqrt(2))      # note that sqrt(2)/2 equals cos(45 deg) and sin(45 deg)
                            TimeSeries = Q_max_TS

                            # tidy up!
                            del TS_yaw_radial_force, TS_yaw_axial_force

                        elif search_mode == 'main_bearing_ULS': # from ISO 76
                            # adding all rotating hub moments, forces for approximating the rotating bearing load:
                            TS_hub_My_rot = TimeSeries
                            TS_hub_Mz_rot = Utility().readTimeSeriesDataFromScratch(RunFolder, BladedJob,'Rotating hub Mz')
                            TS_hub_Fx_rot = Utility().readTimeSeriesDataFromScratch(RunFolder, BladedJob,'Rotating hub Fx')  # axial
                            TS_hub_Fy_rot = Utility().readTimeSeriesDataFromScratch(RunFolder, BladedJob,'Rotating hub Fy')
                            TS_hub_Fz_rot = Utility().readTimeSeriesDataFromScratch(RunFolder, BladedJob,'Rotating hub Fz')
                            TS_rotor_azimuth_rad = Utility().readTimeSeriesDataFromScratch(RunFolder, BladedJob,'Rotor azimuth angle')
                            # generator rotor weight and levers
                            if BladedJob.find('3B') != -1:
                                generator_rotor_weight_in_N = 207607.34 * 9.81  # 3B generator rotor weight force
                            else:
                                generator_rotor_weight_in_N = 187987.07 * 9.81  # 2B generator rotor weight force
                            x1_lever_rotor_to_first_main_bearing_in_m = 4.64
                            x2_lever_first_to_second_main_bearing_in_m = 1.38
                            x3_lever_generator_rotor_to_first_main_bearing_in_m = 1.04
                            # main bearing properties (assumed as 20 degree contact angle, but should evaluate 10 and 30 degree in the future as well)
                            deg_to_rad = 0.01745329251994329576
                            alpha_contact_angle = 20 * deg_to_rad
                            e_main_bearing = 1.5 * math.tan(alpha_contact_angle)
                            cot_alpha_contact_angle = 1 / math.tan(alpha_contact_angle)
                            X = 1
                            Y = 0.44 * cot_alpha_contact_angle

                            P_0r_k_main_yz_TS = []
                            for step in range(len(TimeSeries)):
                                # rotating Fz at bearing
                                TS_hub_Fz_rot_step = -1 / x2_lever_first_to_second_main_bearing_in_m * (TS_hub_My_rot[step] + TS_hub_Fz_rot[step] * (x1_lever_rotor_to_first_main_bearing_in_m + x2_lever_first_to_second_main_bearing_in_m)
                                            - generator_rotor_weight_in_N * (x3_lever_generator_rotor_to_first_main_bearing_in_m + x2_lever_first_to_second_main_bearing_in_m) * math.cos(TS_rotor_azimuth_rad[step]))
                                # rotating Fy at bearing
                                TS_hub_Fy_rot_step = - 1 / x2_lever_first_to_second_main_bearing_in_m * (-TS_hub_Mz_rot[step] + TS_hub_Fy_rot[step] * ( x1_lever_rotor_to_first_main_bearing_in_m + x2_lever_first_to_second_main_bearing_in_m)
                                            - generator_rotor_weight_in_N * (x3_lever_generator_rotor_to_first_main_bearing_in_m + x2_lever_first_to_second_main_bearing_in_m) * math.sin(TS_rotor_azimuth_rad[step]))
                                # resulting yz axial load
                                TS_hub_Fyz_rot_step = math.sqrt(pow(TS_hub_Fy_rot_step, 2) + pow(TS_hub_Fz_rot_step, 2))
                                # calculate resulting static main bearing load time series from ISO 76
                                P_0r_k_main_yz_TS.append(X * abs(TS_hub_Fx_rot[step]) + Y * TS_hub_Fyz_rot_step)

                            TimeSeries = P_0r_k_main_yz_TS

                            # tidy up!
                            del TS_hub_My_rot, TS_hub_Mz_rot, TS_hub_Fx_rot, TS_hub_Fy_rot, TS_hub_Fz_rot, TS_rotor_azimuth_rad

                        elif search_mode == 'main_shaft_ULS':
                            # adding all rotating hub moments, forces for approximating the rotating bearing load:
                            TS_hub_My_rot = TimeSeries
                            TS_hub_Mz_rot = Utility().readTimeSeriesDataFromScratch(RunFolder, BladedJob,'Rotating hub Mz')
                            TS_hub_Fy_rot = Utility().readTimeSeriesDataFromScratch(RunFolder, BladedJob,'Rotating hub Fy')
                            TS_hub_Fz_rot = Utility().readTimeSeriesDataFromScratch(RunFolder, BladedJob,'Rotating hub Fz')
                            TS_rotor_azimuth_rad = Utility().readTimeSeriesDataFromScratch(RunFolder, BladedJob,'Rotor azimuth angle')
                            # generator rotor weight and levers
                            if BladedJob.find('3B') != -1:
                                generator_rotor_weight_in_N = 207607.34 * 9.81  # 3B generator rotor weight force
                            else:
                                generator_rotor_weight_in_N = 187987.07 * 9.81  # 2B generator rotor weight force
                            x1_lever_rotor_to_first_main_bearing_in_m = 4.64
                            x3_lever_generator_rotor_to_first_main_bearing_in_m = 1.04

                            TS_main_shaft_Myz = []
                            for step in range(len(TimeSeries)):
                                TS_main_shaft_My_rot_step = TS_hub_My_rot[step] + TS_hub_Fz_rot[step] * x1_lever_rotor_to_first_main_bearing_in_m \
                                                            - generator_rotor_weight_in_N * x3_lever_generator_rotor_to_first_main_bearing_in_m * math.cos(TS_rotor_azimuth_rad[step])
                                TS_main_shaft_Mz_rot_step = TS_hub_Mz_rot[step] - TS_hub_Fy_rot[step] * x1_lever_rotor_to_first_main_bearing_in_m \
                                                            + generator_rotor_weight_in_N * x3_lever_generator_rotor_to_first_main_bearing_in_m * math.sin(TS_rotor_azimuth_rad[step])
                                TS_main_shaft_Myz.append(math.sqrt(pow(TS_main_shaft_My_rot_step, 2) + pow(TS_main_shaft_Mz_rot_step, 2)))

                            TimeSeries = TS_main_shaft_Myz

                            # tidy up!
                            del TS_hub_My_rot, TS_hub_Mz_rot, TS_hub_Fy_rot, TS_hub_Fz_rot, TS_rotor_azimuth_rad




                        if time_total < 1200:
                            #if search_mode == 'ULS':
                            if search_mode.find('ULS') != -1:
                                desired_value = max(TimeSeries, key=abs)
                            elif search_mode == 'MAX':
                                desired_value = max(TimeSeries)
                            elif search_mode == 'MIN':
                                desired_value = min(TimeSeries)


                        else:
                            multiple_TimeSeries = []
                            number_of_blocks = int(time_total/600)  # cutting the time series into 10 minute alias 600 s pieces
                            steps_per_block = int(time_total/number_of_blocks/deltat)
                            # print(len(TimeSeries))
                            for cutting_idx in range(number_of_blocks):
                                if cutting_idx < number_of_blocks-1:
                                    multiple_TimeSeries.append(TimeSeries[int(steps_per_block * cutting_idx):
                                                                          int(steps_per_block * (cutting_idx+1))])
                                else:  # to ensure that all time steps are included and the list does not get out of range
                                    local_TimeSeries = TimeSeries[int(steps_per_block * cutting_idx):-1]
                                    if len(local_TimeSeries) > 100/deltat:  # ensure that the last block is large enough
                                        multiple_TimeSeries.append(local_TimeSeries)
                            ULS_values = []
                            for TimeSeries in multiple_TimeSeries:
                                # if search_mode == 'ULS':
                                if search_mode.find('ULS') != -1:
                                    ULS_values.append(max(TimeSeries, key=abs))
                                if search_mode == 'MAX':
                                    # print(len(TimeSeries))
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
                                if final_desired_value > desired_value:
                                    final_desired_value = desired_value
                            else:
                                if abs(final_desired_value) < abs(desired_value):
                                    final_desired_value = desired_value
                        else:
                            final_desired_value = desired_value
                    except:
                        print('time series is empty. Setting value to -1')
                        final_desired_value = desired_value = -1

            leveled_results_list_dict[-1][Search.get('Key')] = final_desired_value

        total_time = total_time + time() - time_at_loop_start
        time_to_end = (amount_of_runs-Job_idx+1) * total_time/(Job_idx+1)
        rel_progression = (Job_idx+1)/amount_of_runs * 100
        print('      ', '[{0}{1}]'.format('#'*(int(rel_progression/5)), '-'*(int((100-rel_progression)/5))), round(rel_progression,1), '% is done. Approximated time to finish is ', int(time_to_end // (60*60)),'hours and', int(time_to_end // 60 % 60),'minutes. Search took ', round(time()-time_at_loop_start,2), 'seconds.')

    documentation_path = Utility().writeListDictToCSV(leveled_results_list_dict, documentation_path)

    if search_kind == 'ULS':
        # old: Bladed().ULS_DLCs_evaluation_summarizer(documentation_path)
        from main__ULS_summarizer_incl_each_DLC_ULS__all_new import BladedPostProcess
        BladedPostProcess().ULS_DLCs_evaluation_summarizer(documentation_path)

    elif search_kind == 'FLS':
        '''
        number_of_evaluated_runs = len(leveled_results_list_dict)
        if number_of_evaluated_runs >= 9 * 3 * 6:
            nSeeds = 6
            nYawErrors = 3
        elif number_of_evaluated_runs >= 9 * 6:
            nSeeds = 6
            nYawErrors = 1
        elif number_of_evaluated_runs >= 9 * 3:
            nSeeds = 1
            nYawErrors = 3
        else:
            nSeeds = 1
            nYawErrors = 1
        print('----> ', nSeeds, 'seeds and ', nYawErrors, ' yaw errors are guessed by the amounts of evaluated runs')
        '''
        from main__DLC12_summarizer_v2 import BladedPostProcess
        BladedPostProcess().DLC12_summarizer(documentation_path)  #, nSeeds, nYawErrors)


    return Documentation, ListOfBladedJobs, documentation_path  #, ULS_Searching_keys



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
