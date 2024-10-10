""" ====================================================================================================================

                                           Collection of Utility functions
                         ------------------------------------------------------------------

     Basic functions mostly necessary for Bladed workflow
     Also GA (Genetic algorithm) functions are stored here: reproduction, crossover, mutation, bit_string_to_parameter

==================================================================================================================== """
# import random
import numpy.random as random
import numpy as np
from copy import copy
import sys
import os
import csv
import math
import rainflow # old legacy version
import rainflow_jenni_rinker as rainflow_rinker # new version
import glob
import clr
import matplotlib.pyplot as plt
from matplotlib import cm
from datetime import datetime
from statistics import mean

# import config parameters
from config import nSectors, runFileEnd, towerFileEnd, hubFileEnd, PrintDetails, addToRunFileNames, \
                   eps, Referenz_Frequency, k_steel, k_composite, p_bearing, bearing_DEL_nbins, var_nbins, DEL_keys, TowerNodePosition, ListOfBaselineFiles, \
                   baselineFolder, searchWords, CostShares, max_rotation_speed_bound, MainPathToBladedRuns, param_key,\
                   nParams, Statistics_Searching, Statistics_keys, DocString, bladed_batch_directory  #, ULS_Searching_keys, ULS_Searching


Nreff = -1e20   # has to be positive and will later on re-assigned

# ----------------------------------------------------------------------------------------------------------------
class Utility:
    def collectTimeSeriesStructureFromBladedFiles(self, RunFolder, BladedJob, VariableName, LineIdentifier='VARIAB'):
        # search through files to catch right time series
        InfoFiles = glob.glob(RunFolder + '\\' + BladedJob.split('.')[0] + '.%*')
        if PrintDetails:
            print('Found: ', InfoFiles)

        # foundIt = False
        counter = 0
        for InfoFile in InfoFiles:
            csv_data = csv.reader(open(InfoFile), delimiter='\t')
            for row in csv_data:
                if row[0] == 'DIMENS':  # need to be stored before, because it is marked in the lines above VARIAB
                    DIMENS = row[1:]
                if row[0] == LineIdentifier: # 'VARIAB':  # old alternative: if row[0].find('VARIAB') != -1:
                    for idx, Parameter in enumerate(row[1].split('\' ')):
                        if Parameter.replace('\'', '') == VariableName:
                            fileEnd = '.$' + InfoFile.split('.%')[-1]
                            if PrintDetails and counter == 0:
                                print('found (', Parameter.replace('\'', ''), ') at index ', idx,
                                      ' in file with ending: ', fileEnd, ' and dimensions: ', DIMENS)
                            return [fileEnd, idx, DIMENS]
        return ['', 0, 0]

    def calcTotalTimeAndDeltat(self, RunFolder, BladedJob):
        [fileEnd, idx, DIMENS] = self.collectTimeSeriesStructureFromBladedFiles(RunFolder, BladedJob, 'Time from start of simulation')
        TimeFileEnd = fileEnd  # '.$07'  # alternative: '.$04'
        file = os.path.join(RunFolder, BladedJob.split('.')[0] + TimeFileEnd)
        try:
            csv_data = csv.reader(open(file), delimiter=' ')
            TimeTimeSeries = []  # Time series of the time in s
            for idx, row in enumerate(csv_data):
                row = list(filter(None, row))
                TimeTimeSeries.append(float(row[0]))
            if idx < 1:
                print('warning: Empty time series in file ', file)
                raise OSError
            globals()['time_total'] = time_total = TimeTimeSeries[-1] - TimeTimeSeries[0]
            globals()['deltat'] = deltat = round(TimeTimeSeries[1] - TimeTimeSeries[0], 3)
            globals()['Nreff'] = Nreff = time_total * Referenz_Frequency
        except OSError:
            print('cannot find time file: ', file, '. Will use default values.')
            time_total = -1
            deltat = -1
            #Nreff = globals()['Nreff']

        if PrintDetails:
            print('simulation length is ', time_total, 's with a time step length of ', deltat, 's')
            print('Sector width = ' + str(180 / nSectors) + 'deg')
            print('MOST IMPORTANT DEL PARAMETER: Woehler Exp: ', k_steel, ', ref frequency: ', Referenz_Frequency,
                  ', ref cycles: ', Nreff, ' and numbers of bins is: ', var_nbins)

        return [time_total, deltat]

    def readTimeSeriesDataFromScratch(self, RunFolder, BladedJob, VariableName, pos_of_node=1):
        [fileEnd, idx, DIMENS] = self.collectTimeSeriesStructureFromBladedFiles(
            RunFolder=RunFolder, BladedJob=BladedJob, VariableName=VariableName)
        TimeSeries = self.readTimeSeriesData(RunFolder=RunFolder, BladedJob=BladedJob, fileEnd=fileEnd, idx=idx,
                                             DIMENS=DIMENS, pos_of_node=pos_of_node)
        return TimeSeries

    def readTimeSeriesData(self, RunFolder, BladedJob, fileEnd, idx, DIMENS, pos_of_node=-1):
        # search through the desired time series
        # positions of node (pos_of_node) starts at 1 and not 0
        file = RunFolder + '\\' + BladedJob.split('.')[0] + fileEnd
        try:
            csv_data = csv.reader(open(file), delimiter=' ')
        except OSError:
            print('cannot find ', file, '. Will skip and set value to 0.')
            return [0]

        if len(DIMENS) == 3:  # otherwise the third dimension is missing in the 2D csv data file
            dimensionTwo = float(DIMENS[1])
            if pos_of_node < 0:
                pos_of_node = TowerNodePosition[0]  # some members have two notes; all notes of a single time step are
                print('if this is not a tower time series this causes a failure...')
        else:
            dimensionTwo = 1
            if PrintDetails and TowerNodePosition[0] > 1:
                print('file with ending ', fileEnd,
                      ' should not have multiple stacked nodes! Will set node position to 1')
            pos_of_node = 1

        line_count = 0
        load_count = 0
        # nheader = 0
        TimeSeries = []
        for row in csv_data:
            # if load_count < int(time_total / deltat) + 1:  # nheader:
            if line_count == load_count * dimensionTwo + pos_of_node - 1:
                row = list(filter(None, row))
                # time[line_count-nheader] = row[0]
                TimeSeries.append(float(row[idx]))
                load_count = load_count + 1
            # else: print('overshooting lines')
            line_count = line_count + 1

        # print('node position is:', pos_of_node, '; length of series should be:', dimensionThree, ' and is:', len(TimeSeries), '; last value is:', TimeSeries[0])
        return TimeSeries

    def calcDELfromTimeSeries_old_legacy(self, timeSeries, k): #, Nreff=Nreff): # had some issues with the inconsistancy of the DEL results, thus new version below
        DEL = 0.0
        if timeSeries:  # just to be sure that its not emtpy
            RFC = copy(rainflow.count_cycles(timeSeries, nbins=var_nbins))
            # for bin in range(var_nbins): somehow the last bin can cause severe differences in some minor ocasions.WHY? (issue not found, but fixed in new version)
            for bin in range(var_nbins-1):
                DEL += copy(RFC[bin][1] * (math.pow(RFC[bin][0], k)))
            DEL = copy(math.pow(DEL / Nreff, 1 / k))
        return DEL

    def calcDELfromTimeSeries(self, time_series, k):  # , Nreff=Nreff):
        DEL_non_binned = 0.0
        if time_series:  # just to be sure that its not emtpy
            # extracting turning points of  time series
            TS_turning_points = [time_series[0]]
            #visualize = [0]
            for idx, load in enumerate(
                    time_series[1:-1]):  # the first idx is 0 but should refer to the second value's index
                if np.sign(time_series[idx + 1] - time_series[idx]) != np.sign(time_series[idx + 2] - time_series[idx + 1]):
                    if load != TS_turning_points[-1]:  # typically important for repetitive zeros
                        if len(TS_turning_points) > 2 and np.sign(TS_turning_points[-1] - TS_turning_points[-2]) == np.sign(load - TS_turning_points[-1]):  # needed for numerical issues when there is no actual turning point
                            TS_turning_points.pop()
                            #visualize.pop()
                        TS_turning_points.append(load)
                        #visualize.append(idx + 1)
            # generate cycle counting with the code of Jenni Rinker to get cycle range, cycle count, cycle mean,
            # goodman-adjusted range (GAR), and goodman-adjusted range with zero fixed-load mean (GAR-ZFLM)
            array_out = rainflow_rinker.rainflow(np.array(TS_turning_points)) # array_out index 0: 'Range', 3: 'Count', 1: 'Mean', 2: 'GAR', 4: 'GAR-ZFLM'
            #array_out = array_out[:, array_out[0, :].argsort()] # sort array_out by cycle range (not needed)
            ranges = list(array_out[4])  # goodman-adjusted range with zero fixed-load mean (GAR-ZFLM)
            counts = list(array_out[3])

            for cycle in range(len(ranges)):
                DEL_non_binned += copy(counts[cycle] * (math.pow(ranges[cycle], k)))
            DEL_non_binned = copy(math.pow(DEL_non_binned / Nreff, 1 / k))

        ## for transparency to check the turning point calculation: (also uncomment the list 'visualize')
        #[plt, ax] = self.easyPlotGraph(time_series, color='b', marker='x', show=False, new_y_axis=False, y_label='load')
        #[plt, ax] = self.easyPlotGraph(TS_turning_points, x_axis=visualize, color='r', marker='x', show=True, new_y_axis=False, ax=ax, y_label='load')
        return DEL_non_binned

    def calcWorstDELsector(self, Mx_timeSeries, My_timeSeries, nmb_sectors=nSectors, k=k_steel):  # , MainResults, file):
        # sum moment vectors in fixed directions
        My_timeSeries_Sector = [[] for n in range(nmb_sectors)]  # np.empty([nmb_sectors, int(time_total / deltat + 10)])
        DEL_Sector = [0 for kk in range(nmb_sectors)]  # np.empty(nmb_sectors)
        DEL_max = 0
        n_max = 0
        for n in range(nmb_sectors):
            for timeStep in range(len(Mx_timeSeries)):
                if abs(float(My_timeSeries[timeStep])) > 0:
                    alpha = copy(math.atan(float(Mx_timeSeries[timeStep]) / float(My_timeSeries[timeStep])))
                else:
                    alpha = copy(math.atan(float(Mx_timeSeries[timeStep]) / eps))
                    print('if this is never triggered, this expression is useless...')
                My_timeSeries_Sector[n].append(
                    math.sqrt(math.pow(Mx_timeSeries[timeStep], 2) + math.pow(My_timeSeries[timeStep], 2)) \
                    * math.cos(math.pi / nmb_sectors * n - alpha) * math.copysign(1, My_timeSeries[timeStep]))

            DEL_Sector[n] = self.calcDELfromTimeSeries(My_timeSeries_Sector[n][:], k)
            if DEL_Sector[n] > DEL_max:
                DEL_max = copy(DEL_Sector[n])
                n_max = n

        # Further evalutations:
        Mxy_timeSeries = [math.sqrt(math.pow(Mx_timeSeries[kk], 2) + math.pow(My_timeSeries[kk], 2)) for kk in
                          range(len(Mx_timeSeries))]
        DELx = self.calcDELfromTimeSeries(Mx_timeSeries, k)
        DELy = self.calcDELfromTimeSeries(My_timeSeries, k)
        DEL_ref = self.calcDELfromTimeSeries(Mxy_timeSeries, k)

        if PrintDetails:
            print('Reference DEL:', DEL_ref, '; -> maximum DEL', DEL_Sector[n_max], ' found in Sector', n_max,
                  'with a delta of', round((DEL_Sector[n_max] - DEL_ref) / DEL_ref * 100, 2),
                  '% to the baseline. DEL_Mx is ',
                  DELx, ' and DEL_My ', DELy)

        eps2 = 100
        if DEL_Sector[n_max] - DELy < -eps2 or DEL_Sector[n_max] - DELx < -eps2:
            print('WARNING: Worst DEL ', DEL_Sector[n_max], ' MUST NOT be smaller than My_DEL ', DELy, ' or Mx_DEL ',
                  DELx, '!!!')
            DEL_Sector[n_max] = max(DELy, DELx)

        # keys = ['runName', 'DEL_Mx', 'DEL_My', 'ref_DEL_Mxy', 'new_max_DEL_Mxy', 'sector', 'rel_difference']
        # MainResults.append(dict(zip(keys, [file, str(DELx), str(DELy), str(DEL_ref), str(DEL_Sector[n_max]), str(n_max), str(round((DEL_Sector[n_max]-DEL_ref)/DEL_ref * 100, 2))])))

        return DEL_Sector[n_max]  # , MainResults

    def return_run_files_in_folder(self, folder, fileEnd = '*.$PJ'):
        import re
        return sorted(glob.glob(os.path.join(folder, fileEnd)), key=lambda value: tuple(map(int, re.findall(r"\d+", value))))
        #return sorted(glob.glob(os.path.join(folder, fileEnd)), key = lambda item: (int(item.partition(' ')[0]) if item[0].isdigit() else float('inf'), item))



    def createFolderIfNotExcisting(self, newfolder):
        try:
            os.mkdir(newfolder)
        except OSError:
            if PrintDetails:
                print("Creation of the directory %s failed. Might already exist" % newfolder)
        else:
            print("Successfully created the directory %s " % newfolder)

    def writeListDictToCSV(self, ListDict, fileNamePath):
        #print('writing output in ', fileNamePath)
        if len(ListDict) == 0:
            print('List dictionary is empty. No output file ', fileNamePath, ' is generated.')
            return
        # with open(fileNamePath, 'w', newline='') as output_file:
        ''' # Works only with Python 3
        with open(fileNamePath, 'w') as output_file:
            dict_writer = csv.DictWriter(output_file, ListDict[0].keys())
            dict_writer.writeheader()
            dict_writer.writerows(ListDict)'''
        i = 0
        while i < 10:
            try:
                if sys.version_info[0] < 3:
                    # Works only with Python 2
                    output_file = open(fileNamePath, 'wb')
                    dict_writer = csv.DictWriter(output_file, ListDict[0].keys())
                    dict_writer.writeheader()
                    dict_writer.writerows(ListDict)
                    output_file.close()
                else:  # Works only with Python 3
                    with open(fileNamePath, 'w', newline='') as output_file:
                        dict_writer = csv.DictWriter(output_file, ListDict[0].keys())
                        dict_writer.writeheader()
                        dict_writer.writerows(ListDict)
            except OSError:
                fileNamePath = fileNamePath.split('.')[0] + '_alt' + '.csv'
                print('could not write output. File might be open. Changing path to', fileNamePath)
                i += 1
            else:
                print('writing output in ' + fileNamePath)
                i = 100
        return fileNamePath
        '''    
        try:
            if sys.version_info[0] < 3:
                # Works only with Python 2
                output_file = open(fileNamePath, 'wb')
                dict_writer = csv.DictWriter(output_file, ListDict[0].keys())
                dict_writer.writeheader()
                dict_writer.writerows(ListDict)
                output_file.close()
            else:  # Works only with Python 3
                with open(fileNamePath, 'w', newline='') as output_file:
                    dict_writer = csv.DictWriter(output_file, ListDict[0].keys())
                    dict_writer.writeheader()
                    dict_writer.writerows(ListDict)
        except OSError:
            print('could not write output. File might be open')
        else:
            print('writing output in ' + fileNamePath)
        '''

    def readListDictFromCSV(self, fileNamePath):
        # with open(fileNamePath, 'w', newline='') as output_file:
        ''' # Works only with Python 3
        with open(fileNamePath, 'w') as output_file:
            dict_writer = csv.DictWriter(output_file, ListDict[0].keys())
            dict_writer.writeheader()
            dict_writer.writerows(ListDict)'''
        try:
            if sys.version_info[0] < 3:
                # Works only with Python 2
                print('Python 2 is currently not supported.')
            else:  # Works only with Python 3
                with open(fileNamePath, 'r', newline='') as input_file:
                    file_dict = csv.DictReader(input_file)
                    list_dict = []
                    for row in file_dict:
                        list_dict.append(row)
        except OSError:
            print('could not write output. File might be open')
        else:
            print('reading in ' + fileNamePath)
        return list_dict

    def calcMeanValuesForSeeds(self, ListOfDicts, nSeeds = -1):
        if nSeeds < 0:
            nSeeds = int(len(ListOfDicts))
            nPopulation = 1
        else:  # nPopulation is a relict of genetic algorithms and used, when multiple runs with nSeeds are performed.
            nPopulation = int(len(ListOfDicts)/nSeeds)
        Keys = ListOfDicts[0].keys()
        New_ListOfDicts = [dict(zip(Keys, range(len(Keys)))) for _ in range(nPopulation)]
        for key in Keys:
            for nPopu in range(nPopulation):
                MeanValue = 0.0
                for nSeed in range(nSeeds):
                    MeanValue += ListOfDicts[nPopu + nPopulation * nSeed].get(key)
                MeanValue = MeanValue/nSeeds
                New_ListOfDicts[nPopu][key] = copy(MeanValue)
        return New_ListOfDicts

    def calcBearingDamageFromTimeSeriesForConstSpeed(self, P_ea_k_time_series, time_total, deltat, p = p_bearing, nmbr_bins=30):
        P_ea_k_time_series = [abs(i) for i in P_ea_k_time_series] # just to ensure that there are only positive values
        max_load = max(P_ea_k_time_series)
        min_load = min(P_ea_k_time_series)
        load_bin_lower_bounds = [i for i in np.linspace(min_load, max_load, nmbr_bins + 1)][:-1]  # x bins have x+1 bounds
        centering_load_bins = (max_load - min_load) / (nmbr_bins * 2)
        bin_load_means = [i for i in np.linspace(min_load + centering_load_bins, max_load - centering_load_bins, nmbr_bins)]
        load_time_fraction_per_bin = [0 for _ in range(nmbr_bins)]
        for load in P_ea_k_time_series:
            bin_idx_of_load = -2
            for idx_load_bin, lower_load_of_bin in enumerate(load_bin_lower_bounds):
                if load > lower_load_of_bin:
                    bin_idx_of_load = idx_load_bin
            if bin_idx_of_load > -1:
                load_time_fraction_per_bin[bin_idx_of_load] += deltat / time_total

        # calculate dynamic equivalent load
        P_ea = 0
        for bin_idx_of_load, bin_load in enumerate(bin_load_means):
            P_ea = P_ea + pow(bin_load, p) * load_time_fraction_per_bin[bin_idx_of_load]
        P_ea = pow(P_ea, 1/p)
        return P_ea


    def calcPitchBearingDamage(self, RunFolder, BladedJob, nmbr_amplitude_bins = bearing_DEL_nbins, p = p_bearing, x = 9/10, bearing_raceway_diameter = 1):  # the bearing diameter can also directly be multiplied to the equivalend load P_ea
        # calculation method used is the DG03 combined with load binning of Matthias Stammler (https://www.repo.uni-hannover.de/bitstream/handle/123456789/16114/Cycle_counting_of_roller_bearing_oscillations.pdf?sequence=1&isAllowed=y)
        # with the load calculation adjusted from a factor of 2 to 2.5 as proposed by (https://wes.copernicus.org/preprints/wes-2020-26/wes-2020-26.pdf)
        [time_total, deltat] = self.calcTotalTimeAndDeltat(RunFolder, BladedJob)
        [fileEnd, idx, DIMENS] = Utility().collectTimeSeriesStructureFromBladedFiles(
            RunFolder=RunFolder, BladedJob=BladedJob, VariableName='Blade 1 pitch angle')
        pitch_angle_time_series = Utility().readTimeSeriesData(RunFolder=RunFolder, BladedJob=BladedJob,
            fileEnd=fileEnd, idx=idx, DIMENS=DIMENS, pos_of_node=1)

        [fileEnd, idx, DIMENS] = Utility().collectTimeSeriesStructureFromBladedFiles(
            RunFolder=RunFolder, BladedJob=BladedJob, VariableName='Blade 1 Mxy (Root axes)')
        blade_root_Mxy_time_series = Utility().readTimeSeriesData(RunFolder=RunFolder, BladedJob=BladedJob,
            fileEnd=fileEnd, idx=idx, DIMENS=DIMENS, pos_of_node=1)

        # -------------- range pair counting ----------------- #
        old_angle = pitch_angle_time_series[0]
        initial_angle = pitch_angle_time_series[0]
        initial_time_step = 0
        frequencies_ops = []  # oscillations per second
        amplitudes = []
        amplitudes_end_time_step = []

        for time_step, angle in enumerate(pitch_angle_time_series):
            if time_step > 2:  # ignores first round
                if math.copysign(1, angle - old_angle) != math.copysign(1, old_angle - older_angle): # easy check if there is a direction change
                    amplitudes.append(abs(old_angle - initial_angle)/2)  # an amplitude is just half of the oscillation
                    amplitudes_end_time_step.append(time_step-1)  # the change of direction had been one timestep before
                    initial_angle = old_angle
                    # since this is only half an oscillation, the time duration of the oscillation is double: (2 * number_time_steps * deltat)
                    frequencies_ops.append(1/(2 * (time_step-1 - initial_time_step) * deltat))
                    initial_time_step = time_step-1
            older_angle = old_angle
            old_angle = angle

        # ------ sort the amplitudes and speeds into amplitude bins ------ #
        if amplitudes:
            min_amplitude = min(amplitudes)
            max_amplitude = max(amplitudes)
            amplitude_bin_lower_bounds = [i for i in np.linspace(min_amplitude, max_amplitude, nmbr_amplitude_bins+1)][:-1]  # x bins have x+1 bounds
            centering_amplitude_bins = (max_amplitude - min_amplitude) / (nmbr_amplitude_bins * 2)
            amplitude_bin_means = [i for i in np.linspace(min_amplitude + centering_amplitude_bins, max_amplitude - centering_amplitude_bins, nmbr_amplitude_bins)]
            count_amplitudes_per_bin = [0 for _ in range(nmbr_amplitude_bins)]
            frequencies_ops_per_bin = [[] for _ in range(nmbr_amplitude_bins)]   # oscillations per second
            amplitude_bin_idx_pointers = []

            for idx_amplitude, amplitude in enumerate(amplitudes):
                bin_idx_of_amplitude = 0  # in case the amplitude is zero
                for bin_idx, lower_amplitude_of_bin in enumerate(amplitude_bin_lower_bounds):
                    if amplitude > lower_amplitude_of_bin:
                        bin_idx_of_amplitude = bin_idx

                count_amplitudes_per_bin[bin_idx_of_amplitude] += 1
                frequencies_ops_per_bin[bin_idx_of_amplitude].append(frequencies_ops[idx_amplitude])
                amplitude_bin_idx_pointers.append(bin_idx_of_amplitude)

            # -------- bin counting for the loads for each amplitude bin ---------- #
            min_blade_Mxy = min(blade_root_Mxy_time_series)
            max_blade_Mxy = max(blade_root_Mxy_time_series)

            nmbr_load_bins = nmbr_amplitude_bins
            amplitude_counter = 0
            load_bin_lower_bounds = [i for i in np.linspace(min_blade_Mxy, max_blade_Mxy, nmbr_load_bins + 1)][:-1]  # x bins have x+1 bounds
            centering_load_bins = (max_blade_Mxy - min_blade_Mxy) / (nmbr_load_bins * 2)
            load_bin_means = [i for i in np.linspace(min_blade_Mxy + centering_load_bins, max_blade_Mxy - centering_load_bins, nmbr_load_bins)]
            load_time_fraction_binning = [[0 for _ in range(nmbr_load_bins)] for _ in range(nmbr_amplitude_bins)]
            for idx_load, load in enumerate(blade_root_Mxy_time_series):
                for idx_load_bin, lower_load_of_bin in enumerate(load_bin_lower_bounds):
                    if load > lower_load_of_bin:
                        bin_idx_of_load = idx_load_bin

                if idx_load > amplitudes_end_time_step[amplitude_counter] and amplitude_counter+1 < len(amplitudes_end_time_step):
                    amplitude_counter += 1

                # print(idx_load, amplitude_counter, amplitude_bin_idx_pointers[amplitude_counter], bin_idx_of_load)
                load_time_fraction_binning[amplitude_bin_idx_pointers[amplitude_counter]][bin_idx_of_load] += deltat/time_total

            # ------------ calculated dynamic load ------------- #
            P_ea_numerator = 0
            P_ea_denominator = 0
            average_speed_of_oscillation_ops = 0  # potentially not needed
            for idx_amplitude_bin in range(nmbr_amplitude_bins):
                if frequencies_ops_per_bin[idx_amplitude_bin]:  # first check whether the total bin might be empty
                    mean_frequency_ops_of_bin = mean(frequencies_ops_per_bin[idx_amplitude_bin])  # oscillations per second (ops)
                    average_speed_of_oscillation_ops += mean_frequency_ops_of_bin * sum(load_time_fraction_binning[idx_amplitude_bin])
                    for idx_load_bin in range(nmbr_load_bins):
                        operating_time_in_s = load_time_fraction_binning[idx_amplitude_bin][idx_load_bin]
                        amplitude_crit = np.inf  # for now, this is just a dummy, but could be used if the critical amplitude is important
                        if amplitude_bin_means[idx_amplitude_bin] < amplitude_crit:
                            x_k = 1
                        else:
                            x_k = x
                        P_ea_denominator_k = mean_frequency_ops_of_bin * operating_time_in_s * pow(amplitude_bin_means[idx_amplitude_bin], x_k)  # N_k * t_k * theta_k^x

                        # local bearing load
                        P_ea_k = 2.5 * load_bin_means[idx_load_bin] / bearing_raceway_diameter  # in future, also axial and radial forces could be added!!! (see adjustment of NREL's DG03 in https://wes.copernicus.org/preprints/wes-2020-26/wes-2020-26.pdf, but root moment is expected to be clearly dominant)

                        P_ea_numerator += pow(P_ea_k, p) * P_ea_denominator_k
                        P_ea_denominator += P_ea_denominator_k

            equivalent_oscillation_amplitude = P_ea_denominator/average_speed_of_oscillation_ops
            P_ea = pow(P_ea_numerator/P_ea_denominator, 1/p)

            if False:
                print(len(amplitudes), amplitudes)
                print(len(frequencies_ops), frequencies_ops)
                print(len(amplitudes_end_time_step), amplitudes_end_time_step)
                print(len(amplitude_bin_idx_pointers), amplitude_bin_idx_pointers)
                print(len(count_amplitudes_per_bin), count_amplitudes_per_bin)
                # print(mean_frequency_per_bin)
                print(load_time_fraction_binning)

                data = np.array(load_time_fraction_binning)
                length = data.shape[0]
                width = data.shape[1]
                x, y = np.meshgrid(np.arange(length), np.arange(width))

                fig = plt.figure()
                ax = fig.add_subplot(1, 1, 1, projection='3d')
                ax.set(xlabel='load_bin')
                ax.set(ylabel='amplitude_bin')
                ax.set(zlabel='accumulated duration in s')
                ax.plot_surface(x, y, data)
                plt.show()

                plot, axis = self.easyPlotGraph(pitch_angle_time_series, show=False)
                plot = self.easyPlotGraph(blade_root_Mxy_time_series, ax=axis, color='r')

        else:
            P_ea = 0
            average_speed_of_oscillation_ops = 0
            equivalent_oscillation_amplitude = 0

            print('# ---- new section for P_ea calculation of pitch bearing without movement in low wind speeds ---- #')
            P_ea_k_standstill_TS = []
            for time_step, blade_root_Mxy in enumerate(blade_root_Mxy_time_series):
                P_ea_k_standstill_TS.append(2.5 * blade_root_Mxy / bearing_raceway_diameter)  # in future, also axial and radial forces could be added!!! (see adjustment of NREL's DG03 in https://wes.copernicus.org/preprints/wes-2020-26/wes-2020-26.pdf, but root moment is expected to be clearly dominant)
            P_ea = self.calcBearingDamageFromTimeSeriesForConstSpeed(P_ea_k_standstill_TS, time_total, deltat, p=p)

        print('P_ea=', P_ea / 1000, 'kN, N_ave=', average_speed_of_oscillation_ops * 60, 'opm, theta_e=',
              equivalent_oscillation_amplitude * 180 / 3.14159265359, 'deg, leveled in', len(amplitudes), 'amplitudes')

       #return P_ea, P_ea_numerator, P_ea_denominator  # if more cycles have to be added, the numerator and denominator are vital
        return P_ea, average_speed_of_oscillation_ops, equivalent_oscillation_amplitude  # if more cycles have to be added, the numerator and denominator are vital




    def easyPlotGraph(self, TimeSeries, x_axis=[], y_label='', color='b', marker='o', show=True, new_y_axis=True, ax=[]):
        if not ax:
            fig, ax = plt.subplots()
            # plt.yscale('log')
        elif new_y_axis:
            ax = ax.twinx()
        if y_label:
            ax.set(ylabel=y_label)
        #ax.set(xlabel='frequency in Hz', ylabel='density ' + 'Nacelle side-side acceleration')
        if x_axis:
            ax.plot(x_axis, TimeSeries, marker=marker, color=color)
        else:
            ax.plot(TimeSeries, marker=marker, color=color)
        if show:
            plt.show()
        return plt, ax

    def easyPlotPSD(self, TimeSeries, deltat=0.1, color='b', legend='', show=True, ax=[]):
        if not ax:
            fig, ax = plt.subplots()
        from scipy.signal import welch
        (f, Gyy) = welch(TimeSeries, fs=1 / deltat, nperseg=4 * 1024)
        fig, ax = plt.subplots()
        ax.plot(f[1:], Gyy[1:], label='time series', color='r')
        ax.set(xlabel='frequency in Hz', ylabel='density')
        plt.yscale('log')
        if show:
            plt.show()
        return plt, ax

    def calcCCC(self, Statistics_n_DELs, ref_Statistics_n_DELs, manipulate_out_of_bound_values=False,
                full_load_operation_CCC = True):
        if not Statistics_n_DELs.get(DEL_keys[0]):
            print('Error while evaluating the CCC! Will set CCC to 20!')
            CCC = 20  # This is necessary if bladed run did not work properly. This CCC will be "ignored"
        if Statistics_n_DELs.get('RotationSpeed_max') > max_rotation_speed_bound and manipulate_out_of_bound_values:
            print('Maximum rotation speed exceeds the limit! Will set CCC to 20!')
            CCC = 20  # To avoid over speed
        else:
            CCC = 1
            if not Statistics_n_DELs.get('Blade_My_DEL') == 0:
                CCC += ((Statistics_n_DELs.get('Blade_My_DEL') / ref_Statistics_n_DELs.get('Blade_My_DEL')   - 1))      * CostShares.get('Blade_costs')
                  # +  Statistics_n_DELs.get('Blade_My_max')  / ref_Statistics_n_DELs.get('Blade_My_max')) / 2 - 1)     * CostShares.get('Blade_costs') \
            if not Statistics_n_DELs.get('Hub_Mx_DEL') == 0:
                CCC += (Statistics_n_DELs.get('Hub_Mx_DEL') / ref_Statistics_n_DELs.get('Hub_Mx_DEL') - 1)              * CostShares.get('DriveTrain_costs')
            if not Statistics_n_DELs.get('Tower_My_sector_max_DEL') == 0:
                CCC += (Statistics_n_DELs.get('Tower_My_sector_max_DEL') / ref_Statistics_n_DELs.get('Tower_My_sector_max_DEL') - 1) * CostShares.get('Tower_costs')
            # CCC -= (Statistics_n_DELs.get('Power_mean') / ref_Statistics_n_DELs.get('Power_mean') - 1)                * CostShares.get('CoE_CAPEX_ratio')
            # might be better if any derivation of the power from mean gets punished for full load operation:
            if full_load_operation_CCC:
                if Statistics_n_DELs.get('Power_mean') > 20000000:
                    CCC += (Statistics_n_DELs.get('Power_mean') / 20000000 - 1)
                else: # to punish a negative deviation from mean power more:
                    CCC -= (Statistics_n_DELs.get('Power_mean') / 20000000 - 1)                                         * CostShares.get('CoE_CAPEX_ratio')
            else:
                CCC -= (Statistics_n_DELs.get('Power_mean') / ref_Statistics_n_DELs.get('Power_mean') - 1)              * CostShares.get('CoE_CAPEX_ratio')

            #    + (Statistics_n_DELs.get('Pitch_LDC') / ref_Statistics_n_DELs.get('Pitch_LDC') - 1)
            #        * CostShares.get('PitchSys_costs'))  # might be over estimated (better use energy consumption or leave away)
        return CCC

    def prepare_n_dimensional_grid_points(self, bounds, matrix_size):
        params = []
        previous_params_len = 0
        for idx_dimension, size in enumerate(matrix_size):
            lower_bound = bounds[idx_dimension][0]
            upper_bound = bounds[idx_dimension][1]
            # step_size = (upper_bound-lower_bound)/(size-1)
            for idx_step, grid_point in enumerate(list(np.linspace(lower_bound, upper_bound, size))):
                if idx_dimension == 0:
                    # loads first dimension grid points in params
                    params.append([grid_point])
                else:
                    # copies the previous dimension grid point to each new dimension grid point
                    for idx_previous_steps in range(previous_params_len):
                        if idx_step == 0:
                            # uses old param list
                            params[idx_previous_steps].append(grid_point)
                        else:
                            # extents the param list
                            params.append([*params[idx_previous_steps][:idx_dimension], grid_point])
            # save current params length for the next dimension
            previous_params_len = len(params)

        from operator import itemgetter
        for idx in reversed(range(len(matrix_size))):
            params = sorted(params, key=itemgetter(idx))

        # no use except control purposes
        grid_points = [list(np.linspace(bounds[idx][0], bounds[idx][1], size)) for idx, size in enumerate(matrix_size)]
        print('prepared', len(params), 'grid points with steps: ', grid_points)
        if PrintDetails:
            print('grid points are', params)
        return params

    def calc_rayleigh_distribution_probability_from_wind_speed(self, wind_speed, wind_speed_step_size=2, V_ref=11.4, auto_level_all_probabilities_to_one=True, lowest_wind_speed=5, highest_wind_speed=25):
        """
        Rayleight distribution is taken from the IEC-61400-1 ed.4 in Chapter 3.68: P_R(V_0)=1-exp[-pi(V_0/(2V_ave)^2]
        """
        lower_probability = 1 - math.exp(-math.pi * pow((wind_speed - wind_speed_step_size / 2) / 2 / V_ref, 2))
        upper_probability = 1 - math.exp(-math.pi * pow((wind_speed + wind_speed_step_size / 2) / 2 / V_ref, 2))
        probability = upper_probability - lower_probability

        if auto_level_all_probabilities_to_one: # helpful to avoid a reduced mean, e.g., load level over all wind speeds
            # probability of wind speeds below the lowest analyzed wind speed
            ignored_probability_lowest = 1 - math.exp(-math.pi * pow((lowest_wind_speed - wind_speed_step_size / 2) / 2 / V_ref,2))
            # probability of wind speeds above the highest analyzed wind speed
            ignored_probability_highest = math.exp(-math.pi * pow((highest_wind_speed + wind_speed_step_size / 2) / 2 / V_ref,2))
            ignored_probability = ignored_probability_lowest + ignored_probability_highest
            probability = probability / (1 - ignored_probability)

        return probability

    def manipulatePRJfiles(self, Params=[], Iteration_integer = -1,  searchWords_local = searchWords,
               ListOfBaselineFiles_local = ListOfBaselineFiles, addToRunFileNames_local = addToRunFileNames,
               infolder=baselineFolder, outfolder='', ChangeDicts=[], ChangeNameDicts=[], shorten_files=True):
        # this function should manipulate bladed project files. Most variables are defined in config.py
        # if a specific line should be changed (that is not external controller typical) use the ChangeDict option, e.g.
        # ChangeDicts.append({'WORD': 'ENDT	 ', 'EXCHANGE': 'ENDT	 320'}), will be ignored if empty (analogue to Params)
        try:
            Params[1][0]
        except:
            if ChangeDicts:
                if len(ChangeDicts) == 1:
                    MultipleRuns = True
            elif len(searchWords_local) == 1:
                MultipleRuns = True
            MultipleRuns = False
        else:
            MultipleRuns = True  # if Params is 2-dimensional than its clearly for two runs

        if MultipleRuns:
            nRuns = len(Params)
            nValues = len(Params[0])
        else:
            nRuns = 1
            nValues = len(Params)

        if not outfolder:
            from datetime import datetime
            outfolder = MainPathToBladedRuns # os.path.join(infolder, datetime.today().strftime('%Y_%m_%d__') + addToRunFileNames_local[0] + '\\')
        self.createFolderIfNotExcisting(outfolder)

        if Iteration_integer >= 0:
            addIterationString = '_g' + str(Iteration_integer) + '_'
        else:
            addIterationString = ''


        outfileNames = []
        for idx_baselinefile, fileName in enumerate(ListOfBaselineFiles_local):
           # for value in Params:
            for idx_run in range(nRuns):

                addToRunFileNamesValues = ''
                for idx_value in range(nValues):
                    try:
                        Value = Params[idx_run][idx_value]
                    except:
                        Value = Params[idx_value]
                    #addToRunFileNamesValues += addForMoreValues + str('%.02f' % Value).replace('.', '_')
                    if addToRunFileNames_local[idx_value] != '':
                        addToRunFileNamesValues += addToRunFileNames_local[idx_value] + str('%.05f' % Value).replace('.', '_')

                NameAdd = addIterationString + addToRunFileNamesValues  # '.prj'

                # infileName = ListOfBaselineOldFiles[idx].replace(fileEnd, '')
                # outfileName = fileName.replace(fileEnd, '')
                infileName = fileName.replace(runFileEnd, '')
                outfileName = fileName.replace(runFileEnd, '') + NameAdd
                if ChangeNameDicts:
                    new_outfileName = outfileName.replace(ChangeNameDicts[idx_baselinefile].get('WORD'),
                                                      ChangeNameDicts[idx_baselinefile].get('EXCHANGE'))
                    if new_outfileName == outfileName:
                        outfileName += ChangeNameDicts[idx_baselinefile].get('EXCHANGE')
                    else:
                        outfileName = new_outfileName

                if len(outfileName) > 65 and shorten_files:
                    print('outfile name ' + outfileName + ' is too long for Bladed (>65). Thus shortened to ' + outfileName[0:59])
                    outfileName = outfileName[0:59]
                outfileNames.append(outfileName + runFileEnd)


                if PrintDetails:
                    print('new filename is: ' + outfileName + ' with length ' + str(len(outfileName)))

                infile = open((os.path.join(infolder, infileName) + '.$PJ'), "r")
                outfile = open((os.path.join(outfolder, outfileName) + '.$PJ'), "w")

                for row in infile:
                    if row.find(infileName) != -1:
                        row = '  <Name>' + outfileName + '</Name>\n'

                    skip_row = False
                    if ChangeDicts:
                        for idx_value, Dict in enumerate(ChangeDicts):
                            if row.find(Dict.get('WORD')) != -1:
                                if PrintDetails:
                                    print('was: ' + row)
                                row = Dict.get('EXCHANGE') + '\n'  # + str(value) + ';' + '\n'
                                if PrintDetails:
                                    print('is now: ' + row)
                                if Dict.get('EXCHANGE') == '':
                                    skip_row = True

                    else:
                        for idx_value, Word in enumerate(searchWords_local):
                            if row.find(Word) != -1:
                                if PrintDetails:
                                    print('was: ' + row)
                                try:
                                    row = row.split(Word)[0] + Word + '=' + str(Params[idx_run][idx_value]) + ';' + '\n'
                                except:
                                    row = row.split(Word)[0] + Word + '=' + str(Params[idx_value]) + ';' + '\n'
                                if PrintDetails:
                                    print('is now: ' + row)
                    if not skip_row:
                        outfile.write(row)

                outfile.close()
                infile.close()

        return outfileNames, outfolder

    # evaluates folder with bladed runs by collecting all job names, parsing files through evaluation functions
    # and wrtiting to a CSV file
    def evaluateFolder(self, folderPlusFirstSnip):
        ListOfBladedJobs = []
        for run_file in glob.glob(folderPlusFirstSnip + '*.$PJ'):
            # ListOfBladedJobs.append(dict(zip(['run_name'], [''.join(run_file)])))
            ListOfBladedJobs.append(run_file.split('\\')[-1])  # .split('.')[0])

        print('job names are: ', ListOfBladedJobs)

        RunFolder = os.path.dirname(folderPlusFirstSnip)
        RunFolderName = RunFolder.split('\\')[-1]

        print('# ----------- starting with run evaluation ------------- #')
        Statistics = Bladed().extractStatisticalBladedResultsData(RunFolder, ListOfBladedJobs)
        DEL_dicts = Bladed().extractDEL_towerHubBlade(RunFolder, ListOfBladedJobs)

        EvaluationDicts = [{'BladedJobName': RunName} for RunName in ListOfBladedJobs]
        [EvaluationDicts[i].update(DEL_dicts[i]) for i in range(len(DEL_dicts))]
        [EvaluationDicts[i].update(Statistics[i]) for i in range(len(DEL_dicts))]

        # Keys that are saved to file in this specific order
        Docu_keys = ['BladedJobName', 'Blade_Mx_DEL', 'Blade_My_DEL', 'Blade_Mz_DEL', 'Blade_Fz_DEL',  # 'Blade_My_max',
                     'Tower_Mx_DEL', 'Tower_My_DEL', 'Tower_My_sector_max_DEL', 'Tower_Mz_DEL',
                     'Hub_Mx_DEL', 'Hub_My_DEL', 'Hub_Mz_DEL', 'Hub_Myz_sector_max_DEL',
                     'Power_mean', 'Pitch_LDC', 'mean_Thrust_Hub_Fx', 'mean_Platform_Pitch', 'max_Platform_Pitch',
                     'max_mooring_tension', 'max_Nacelle_FA_accel']

        Documentation = [{Key: Dict[Key] for Key in Docu_keys} for Dict in EvaluationDicts]
        # print(Documentation)

        outfileName = os.path.join(RunFolder, RunFolderName + '_' + datetime.today().strftime('%Y_%m_%d__') + '_DEL_evaluation.csv')
        Utility().writeListDictToCSV(Documentation, outfileName)

    def searchForEqualStringSequencesInRunNames(self, RunNames):
        # searching for the first sequence of chars that is equal for all run names
        RunNameRef = RunNames[0] # list_dict[0].get(keys[0])
        EqualChars_idx = 1
        for RunName in RunNames:
            for idx in range(len(RunName)):
                if RunName[:-EqualChars_idx] == RunNameRef[:-EqualChars_idx]:
                    if RunName[-EqualChars_idx - 1] == '_' or RunName[-EqualChars_idx - 1].isnumeric():
                        EqualChars_idx += 1
                    break
                else:
                    EqualChars_idx += 1
        FirstSplittingSequences = RunNameRef[:-EqualChars_idx]
        # searching for the second sequence of chars that is equal for all run names
        # first filter out the first numerical content (the start of SecondSplittingSequences)
        for idx, Char in enumerate(RunNameRef[-EqualChars_idx:]):
            if Char.isalpha() and Char != '_':
                if RunNameRef[-EqualChars_idx + idx - 1] == '_':
                    idx = idx - 1
                break
        # than search for the next numerical content (the end of SecondSplittingSequences)
        SecondSplittingSequences = RunNameRef[-EqualChars_idx + idx:]
        for idx, Char in enumerate(SecondSplittingSequences):
            if Char.isnumeric():
                break
        SecondSplittingSequences = SecondSplittingSequences[:idx]
        return FirstSplittingSequences, SecondSplittingSequences

    def plot_threedimensional_data(self, X, Y, Z, xdimension=0, xlabel= '', ylabel='', zlabel=''):
        if not xdimension:
            save_x = X[0]
            for idx, x in enumerate(X):
                if save_x != x:
                    if idx < 2:
                        for idx, x in enumerate(X[1:]):
                            if save_x == x:
                                idx += 1
                                break
                    xdimension = idx
                    if PrintDetails:
                        print('X-Dimension is', xdimension)
                    break

        X = np.array(X)
        Y = np.array(Y)
        Z = np.array(Z)

        X = np.reshape(X, (-1, xdimension))
        Y = np.reshape(Y, (-1, xdimension))
        Z = np.reshape(Z, (-1, xdimension))

        fig, ax = plt.subplots(subplot_kw={"projection": "3d"})
        # Plot the surface.
        surf = ax.plot_surface(X, Y, Z, cmap=cm.coolwarm,
                               linewidth=0, antialiased=False, vmin=Z.min(), vmax=min(Z.min()*1.5, Z.max()))

        # Customize the z axis.
        ax.set_zlim3d(Z.min(), min(Z.min()*1.5, Z.max()))
        # use to set fixed number of axis values
        # from matplotlib.ticker import LinearLocator
        # ax.zaxis.set_major_locator(LinearLocator(10))
        # A StrMethodFormatter is used automatically
        # ax.zaxis.set_major_formatter('{x:.02f}')

        # Add a color bar which maps values to colors.
        useColorBar = False
        if useColorBar:
            fig.colorbar(surf, shrink=0.5, aspect=20, vmin=Z.min(), vmax=min(Z.min()*1.5, Z.max()))

        # Add a legend
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_title(zlabel)

        plt.draw()
        return plt

    # this function reads in the dictionary data from a csv file and loads it into a 3-D surface plot
    def readAndPlotThreeDimensionalDataFromCSVfile(self, filePath, EvaluationKeys = ['all'], WritePlotData = True, Plot = True):
        # loading data from file
        list_dict = self.readListDictFromCSV(filePath)

        keys = list(list_dict[0].keys())
        if PrintDetails:
            print('dict keys are: ', keys)

        # first index is not necessarily the run name
        idx_RunNameKey = 0
        while list_dict[0].get(keys[idx_RunNameKey]).isnumeric():
            idx_RunNameKey += 1
        RunNameKey = keys[idx_RunNameKey]

        # searching for the first sequence of chars that is equal for all run names
        RunNames = [Dict.get(RunNameKey) for Dict in list_dict]
        FirstSplittingSequences, SecondSplittingSequences = self.searchForEqualStringSequencesInRunNames(RunNames)

        if EvaluationKeys[0] == 'all':
            EvaluationKeys = []
            for key in keys[idx_RunNameKey+1:]:
                try:
                    float(list_dict[0].get(key))
                except:
                    pass
                else:
                    EvaluationKeys.append(key)

        for key_idx, EvaluationKey in enumerate(EvaluationKeys):
            # restoring data in two-dimensional field
            X = []
            Y = []
            Z = []
            for idx, Dict in enumerate(list_dict):
                if param_key in keys:
                    X.append(float(Dict.get(param_key).split(',')[0]))
                    Y.append(float(Dict.get(param_key).split(',')[1]))
                else:
                    RunName = Dict.get(RunNameKey)
                    X.append(float(RunName.split(FirstSplittingSequences)[1].split(SecondSplittingSequences)[0].replace('_', '.')))
                    Y.append(float(RunName.split(FirstSplittingSequences)[1].split(SecondSplittingSequences)[1].split('.')[0].replace('_', '.')))
                Z.append(float(Dict.get(EvaluationKey)))

            plt = Utility().plot_threedimensional_data(X, Y, Z, 0.0, FirstSplittingSequences.split('_')[-1],
                                                 SecondSplittingSequences.split('_')[-1], EvaluationKey)

        return X, Y, Z, plt

    def detect_eigenfrequency_from_campbell_linearization(self, run_file_path, mode_name='Tower 1st side-side mode', frequency_position=3, printDetails=True):
        BladedJob = run_file_path.split('\\')[-1]
        RunFolder = os.path.split(run_file_path)[0]  # path_file_path.replace(BladedJob, '')
        # load bladed file structure

        try:
            [fileEnd, idx, DIMENS] = self.collectTimeSeriesStructureFromBladedFiles(RunFolder, BladedJob, mode_name,
                                                                                    LineIdentifier='AXITICK')
            filename = os.path.join(RunFolder, BladedJob).split('.')[0] + fileEnd.replace('$', '%')
            file_data = csv.reader(open(filename), delimiter='\t')
        except OSError:
            if printDetails:
                print('could not open file ' + os.path.join(RunFolder, BladedJob) + ' for bladed file variable position will try next one')
            return -1

        counter = 0
        for row in file_data:
            row = row[0].split('   ')
            if row[0] == 'MEAN':
                if counter == idx:
                    eigenfrequency = str(float(row[frequency_position]))  # damped frequency is position 3
                    if printDetails:
                        print(mode_name, ' extracted at ', eigenfrequency, 'Hz in run', filename)
                    return eigenfrequency
                else:
                    counter += 1



    def detect_tower_eigenfrequency_from_decay_test(self, run_file_path, plot_PSD=False, use_bezier=True, FOWT=False, Evaluation_Parameter='Nacelle fore-aft acceleration'):
        BladedJob = run_file_path.split('\\')[-1]
        RunFolder = os.path.split(run_file_path)[0]  # path_file_path.replace(BladedJob, '')
        # load bladed file structure
        #[fileEnd, idx, DIMENS] = self.collectTimeSeriesStructureFromBladedFiles(RunFolder, BladedJob, 'Nacelle side-side acceleration')
        #[fileEnd, idx, DIMENS] = self.collectTimeSeriesStructureFromBladedFiles(RunFolder, BladedJob, 'Nacelle fore-aft acceleration')
        [fileEnd, idx, DIMENS] = self.collectTimeSeriesStructureFromBladedFiles(RunFolder, BladedJob, Evaluation_Parameter)
        # get time data
        [time_total, deltat] = self.calcTotalTimeAndDeltat(RunFolder, BladedJob)
        # get time series
        time_series = self.readTimeSeriesData(RunFolder, BladedJob, fileEnd, idx, DIMENS)[1:]
        if plot_PSD:
            print(BladedJob)
            Utility().easyPlotGraph(time_series)

        # calc PSD (power spectral density)
        from scipy.signal import welch
        (f, Gyy) = welch(time_series, fs=1 / deltat, nperseg=2 * 1024) #, nperseg=16 * 1024)

        '''
        # calc FFT
        from scipy.fft import fft, fftfreq
        N = len(time_series)
        yf = fft(time_series)
        xf = fftfreq(N, deltat)[:N//2]

        import matplotlib.pyplot as plt
        plt.plot(xf, 2.0 / N * np.abs(yf[0:N // 2]))
        plt.plot(f, Gyy)
        plt.grid()
        plt.show()
        '''

        min_Hz = 0 #0.03
        max_Hz = 2  # 0.523

        if FOWT:
            # erase first part of time series to cut of first frequency peak from platform roll and sway motion
            min_Hz = 0.11
            max_Hz = 1.2 # 0.75
            # for higher tower eigenfrequencies
            # min_Hz = 0.75
            # max_Hz = 5

            '''
            min_Hz = 0.12
            avoid_Hz = 0.65
            avoid_delta_Hz = 0.05
    
            Max_Gyy_lower_f = max([Gyy[idx] for idx, Hz in enumerate(f) if min_Hz < Hz < avoid_Hz-avoid_delta_Hz])
            Max_Gyy_upper_f = max([Gyy[idx] for idx, Hz in enumerate(f) if avoid_Hz-avoid_delta_Hz < Hz])
            if Max_Gyy_lower_f > Max_Gyy_upper_f:
                max_Hz = avoid_Hz-avoid_delta_Hz'''

        # f_reduced = [f_i for f_i in f if min_Hz < f_i < max_Hz]
        f_reduced = []
        Gyy_reduced = []
        for idx, Hz in enumerate(f):
            if min_Hz < Hz < max_Hz:
                f_reduced.append(f[idx])
                Gyy_reduced.append(Gyy[idx])

        # get the maximum peak,shich is supposed to be the tower eigenfrequency
        idx_max = np.argmax(Gyy_reduced)
        if PrintDetails:
            print('tower eigenfrequency detected at ', f_reduced[idx_max], 'Hz')

        # interpolate the five points around the tower eigenfrequency to get a more precise peak
        search_width = 3
        #from scipy.interpolate import make_interp_spline
        #cs = make_interp_spline(f_reduced[idx_max-search_width:idx_max+search_width+1],
        #            Gyy_reduced[idx_max-search_width:idx_max+search_width+1], k=3, bc_type=([(2, 0.0)], [(2, 0.0)]))
        from scipy.interpolate import make_interp_spline
        try:
            cs = make_interp_spline(f_reduced[idx_max - search_width:idx_max + search_width + 1],
                                    Gyy_reduced[idx_max - search_width:idx_max + search_width + 1], k=3,
                                    bc_type=([(2, 0.0)], [(2, 0.0)]))
        except:
            print('WARNING: spline caused an exception in run ', BladedJob, '. PSD searched tower eigenfrequency is ', f_reduced[idx_max], 'Hz')
            return f_reduced[idx_max]
        f_spline = np.arange(f_reduced[idx_max - search_width], f_reduced[idx_max + search_width], 0.0001)
        Gyy_spline = cs(f_spline)
        tower_eigenfrequency = f_spline[np.argmax(Gyy_spline)]


        # plotting PSD and the PSD's peak spline
        fig, ax = plt.subplots()
        plt.yscale('log')
        ax.set_title(BladedJob)
        ax.set(xlabel='frequency in Hz', ylabel='density ' + Evaluation_Parameter)
        ax.plot(f[1:200], Gyy[1:200])
        ax.plot(f_spline, Gyy_spline, marker='o')
        plt.axvline(x=f_reduced[idx_max], color='cornflowerblue', linestyle='dashed', label='max PSD')
        plt.axvline(x=tower_eigenfrequency, color='orange', linestyle='dashed', label='max splined PSD')


        import bezier
        search_width_bezier = 9
        try:
            bezier_curve = bezier.Curve(np.asfortranarray([f_reduced[idx_max - search_width_bezier:idx_max + search_width_bezier + 1],
                                                       Gyy_reduced[idx_max - search_width_bezier:idx_max + search_width_bezier + 1]]), degree=2*search_width_bezier)
        except:
            print('WARNING: bezier_curve caused an exception in run ', BladedJob, '. spline searched tower eigenfrequency is ', tower_eigenfrequency, 'Hz')
            if plot_PSD:
                plt.show()
            return tower_eigenfrequency


        # necessary to get bezier curve:
        line = bezier_curve.plot(100, ax=ax)
        f_spline_bezier = line.get_lines()[-1].get_xdata()
        Gyy_spline_bezier = line.get_lines()[-1].get_ydata()
        plt.axvline(x=f_spline_bezier[np.argmax(Gyy_spline_bezier)], color='green', linestyle='dashed', label='max PSD with bezier curve')

        if plot_PSD:
            plt.show()

        if use_bezier:
            tower_eigenfrequency = f_spline_bezier[np.argmax(Gyy_spline_bezier)]
        print('tower eigenfrequency is more precisely at ', tower_eigenfrequency, 'Hz in run ', BladedJob)

        return tower_eigenfrequency




'''
    def sumAndNormSeedsOfIterations(ListDict, nSeeds=6, JustSumKey='None' ): # input: List Dictionary, number of seeds and an exception where the values should only be normed
        if not sum_relative_values:
            return [{}], [{}]
        runs_info_file = glob.glob(os.path.join(PathMainFolder, 'base_prj_files') + '\*.csv')[0]
        print('Opening runs info file ', runs_info_file)
        file_data = csv.reader(open(runs_info_file), delimiter=',')

        runs_info = []
        info_keys = []
        cnt = 0
        PosOfReference = 0
        for row in file_data:
            if not info_keys:
                info_keys = row
                # print('info_keys are ', info_keys)
            else:
                runs_info.append(dict(zip(info_keys, row)))
                if float(runs_info[cnt].get(info_keys[1])) == 1 and float(runs_info[cnt].get(info_keys[2])) == 1 and PosOfReference == 0:
                #if (float(runs_info[cnt].get(info_keys[1])) == 1 and float(runs_info[cnt].get(info_keys[2])) == 1 or float(runs_info[cnt].get(info_keys[1])) == 0) and PosOfReference == 0:
                    PosOfReference = cnt
                    print('If necessary check position of gain factors 1 and 1! Here position ', PosOfReference)
                cnt += 1

        print(ListDict[0].keys())

        Value_Alarms = []
        Alarm_keys = ['RunNumber', 'RunName', 'seedNumber', 'Component', 'Value', 'Value_ref', 'relativeIncrease']
        eps = 0.5  # percentage of error tolerance without an error message
        iterationCases = int(len(ListDict) / nSeeds)
        ListDict_summed = [dict(zip(ListDict[0].keys(), range(len(ListDict[0].keys())))) for cnt in
                             range(iterationCases)]
        for cnt in range(iterationCases):
            for key in ListDict[0].keys():
                Sum = 0
                for nSeed in range(nSeeds):
                    Value = float(ListDict[cnt + iterationCases * nSeed].get(key))
                    Value_ref = float(ListDict[PosOfReference + iterationCases * nSeed].get(key))
                    #if Value_ref == 0:
                    #    Value_ref = 1
                    #    Value = 1
                    if JustSumKey in key:
                        Value_ref = 1
                    Sum += Value / Value_ref
                    if (Value - Value_ref) / Value_ref > eps:
                        #print('Run ', cnt + iterationCases * nSeed, 'of ', key, 'got a Value of ', Value,
                        #      'with a relative difference of ', (Value - Value_ref) / Value_ref, ' to ', Value_ref)
                        Value_Alarms.append(dict(zip(Alarm_keys, [cnt + iterationCases * nSeed,
                                                #runs_info[cnt].get(info_keys[0]),
                                                runs_info[cnt + iterationCases * nSeed].get(info_keys[0]),
                                                nSeed, key, Value, Value_ref, (Value-Value_ref)/Value_ref ])))

                ListDict_summed[cnt][key] = Sum / nSeeds
        return ListDict_summed, Value_Alarms
        
    def writeListDictToCSV(ListDict, fileNamePath):
        print('writing output in ', fileNamePath)
        if len(ListDict) == 0:
            print('List dictionary is empty. No output file ', fileNamePath, ' is generated.')
            return
        with open(fileNamePath, 'w', newline='') as output_file:
            dict_writer = csv.DictWriter(output_file, ListDict[0].keys())
            dict_writer.writeheader()
            dict_writer.writerows(ListDict)
'''



""" ====================================================================================================================

                        This class contains methods, that are extremely specific for Bladed
                         ------------------------------------------------------------------
            The methods provide:
            1.  Automatic start of Bladed runs for given input project-files (.$PJ) and wait until finished
            2.  DEL (Damage Equivalent Loads) evaluation of tower, hub and blades for given run names
            3.  Basic statistics (max, min, mean values) for given bladed run names
            
            Note: These methods are extremely dependent on the parameters of the config file!

==================================================================================================================== """

class Bladed:
    # def __init__(self): #, BASE_RESULTS_DIRECTORY, PROJECT_FILE_PATH):
    def AutoRunBatch(self, PathToBladedRuns, ListOfBladedJobs, skip_if_existing=False, job_list_name='default'):

        if not ListOfBladedJobs:
            print('Job list is empty. No new runs performed.')
            return 42

        # avoid unnecessary bladed runs:
        if skip_if_existing:
            print('from Jobs:      ', ListOfBladedJobs)
            ListOfBladedJobs = [BladedJob for BladedJob in ListOfBladedJobs
                                if not os.path.isfile(os.path.join(PathToBladedRuns, BladedJob).split('.')[0]+r'.$05')]
                            # and os.path.getsize(os.path.join(PathToBladedRuns, BladedJob).split('.')[0]+r'.$05')>0]
            print('remain the jobs:', ListOfBladedJobs)

        if not ListOfBladedJobs:
            print('Job list is empty. No new runs performed.')
            return 42

        # Bladed installation directory here -----------------------
        BLADED_INSTALL_DIR = r"C:\DNV\Bladed 4.14"
        # ---------------------------------------------------------------
        sys.path.append(BLADED_INSTALL_DIR)  # This allows the import of the .Net dlls in the Bladed install directory
        clr.AddReference("GH.Bladed.Api.Facades")  # This loads the dll which provides the Bladed API into Python
        from GH.Bladed.Api.Facades.EntryPoint import Bladed  # This imports the entry point to the Bladed API into this script
        Bladed.LoggingSettings.LogToConsole = False  # Controls whether logs are output to the console
        # ---------------------------------------------------------------
        # Start batch framework, set the working directory and job list--
        print("Starting the Batch Framework...\n")
        Bladed.BatchApi.StartFramework()
        # Starting batch and define working directory done in UsageExampleUtilities
        # Set job list name
        # Bladed.BatchApi.SetDirectory(r'C:\DNV\Batch\DefaultBatchDirectory')
        Bladed.BatchApi.SetDirectory(bladed_batch_directory)
        # Bladed.BatchApi.SetJobList(r"AutoIterations")
        Bladed.BatchApi.SetJobList(job_list_name)
        # ---------------------------------------------------------------
        # Redirect log file output (useful for debugging purposes)
        Bladed.LoggingSettings.LogFilePath = os.path.join(PathToBladedRuns, r"Bladed_API_Log.txt")
        # Suppress warning messages and allow outputs to be overwritten
        Bladed.ProjectApi.Settings.OverwriteOutputs = True
        Bladed.ProjectApi.Settings.SuppressAllMessageBoxesByChoosingDefaultOption = True

        print('# -------- loading runs into job list ---------- #')
        # PrintList = ''
        try:
            # load job(s) into the batch queue
            for idx, JobName in enumerate(ListOfBladedJobs):
                #JobName = JobName + runFileEnd
                prj = Bladed.ProjectApi.GetProject(os.path.join(PathToBladedRuns, JobName))
                newJobName = JobName.split('.')[0]
                Bladed.ProjectApi.QueueJob(prj, PathToBladedRuns, newJobName)

                sys.stdout.write('\r' + str(idx + 1) + ' of ' + str(len(ListOfBladedJobs)) + ' Job(s) added to queue ')  #: ' + PrintList)
            print(': ' + ", ".join([JobName for JobName in ListOfBladedJobs]))

            # Add queued jobs to batch. This will not return until the operation is complete and it clears the job queue
            Bladed.ProjectApi.AddQueuedJobsToBatch()
            # print("Queued jobs have been added to batch.")

            # Run the simulations added to batch
            print("Starting to run calculations.")
            # Blocking method to run the batched calculations and only return when it has finished running.
            Bladed.BatchApi.RunBlocking()
            if Bladed.BatchApi.HasCompleted():
                print("Batch runs have completed successfully.")
            else:
                print("Batch runs have not completed successfully.")

            # Shut down the Batch framework
            # Throws an exception if the batch framework could not be stopped due to being busy.
            # Bladed.BatchApi.StopFramework()
        except Exception:
            print("ERROR WHILE LOADING AND RUNNING BLADED BATCH!!!!")
        # finally: # Reset the API. Clear all state.
        #     Bladed.Reset()

    ####################################################################################################################
    ####################################################################################################################
    ################################################## Bladed EVALUATIONS ##############################################
    ####################################################################################################################
    ####################################################################################################################

    def extractDEL_towerHubBlade(self, RunFolder, ListOfBladedJobs, use_hub_fixed_blade_coordinate_system=False):
        DEL_dicts = [dict(zip(DEL_keys, range(len(DEL_keys)))) for whatever in range(len(ListOfBladedJobs))]

        Utility().calcTotalTimeAndDeltat(RunFolder, ListOfBladedJobs[0])

        MainResults = []
        cnt_warnings = 0

        if PrintDetails:
            print('# ------------------ Extracting Tower My\' DEL from Bladed ASCII results ------------- #')
        # Bladed Output Properties
        nmbr_load_member = 2
        # nmbr_loads_per_note = 6
        pos_of_node = 3  # every member has two notes; all notes of a single time step are staggered in one column, thus:
                         # pos 1 is first node of first member; 2 is second node of member 1; 3 is first node of member 2 ..
        pos_of_node = TowerNodePosition[0]
        for idx, filename in enumerate(ListOfBladedJobs): #[11:500]:
            if '2B' or '2b' in filename:
                nBlades = 2
            elif '3B' or '3b' in filename:
                nBlades = 3
            else:
                print('Error! Could not find numbers of Blades in file string. Have to be set manually')
            #break
            file = os.path.join(RunFolder, filename).replace(runFileEnd, towerFileEnd)
            if PrintDetails:
                print('current file is called: ', file)  # filename = (file.replace(RunFolder + '\\', '', ))

            TowerMx = []
            TowerMy = []
            TowerMz = []

            try:
                csv_data = csv.reader(open(file), delimiter=' ')
            except OSError:
                print('Something is rotten in the state of denmark!')
                print('cannot find ', file, '. Will skip and set value to 0.')
                DEL_dicts[idx]['Tower_My_sector_max_DEL'] = 0
                continue

            line_count = 0
            load_count = 0
            # nheader = 0
            for row in csv_data:
                # if load_count < int(time_total / deltat) + 1:  # nheader:
                if line_count == load_count * nmbr_load_member * 2 + pos_of_node - 1:
                    row = list(filter(None, row))
                    # time[line_count-nheader] = row[0]
                    TowerMz.append(float(row[0]))
                    TowerMx.append(float(row[1]))
                    TowerMy.append(float(row[2]))
                    # TowerMxy.append(float(row[3]))
                    load_count = load_count + 1
                # else: print('overshooting lines')
                line_count = line_count + 1

            '''
            with open(file) as csv_file:
                csv_data = csv.reader(csv_file, delimiter=' ')
                line_count = 0
                load_count = 0
                # nheader = 0
                for row in csv_data:
                    if load_count < int(time_total/deltat)+1: #nheader:
                        if line_count == load_count * nmbr_load_member * 2:
                            row = list(filter(None, row))
                            # time[line_count-nheader] = row[0]
                            TowerMx.append(float(row[1]))
                            TowerMy.append(float(row[2]))
                            # TowerMxy.append(float(row[3]))
                            load_count = load_count + 1
                    # else: print('overshooting lines')
                    line_count = line_count + 1
                    '''

            # sum moment vectors in fixed directions and search for worst DEL direction
            DEL_max = Utility().calcWorstDELsector(TowerMx, TowerMy, nSectors)
            DEL_dicts[idx]['Tower_My_sector_max_DEL'] = DEL_max
            # DEL_dicts[idx][DEL_keys[2]] = DEL_max
            DEL_dicts[idx]['Tower_Mx_DEL'] = Utility().calcDELfromTimeSeries(TowerMx, k_steel)
            DEL_dicts[idx]['Tower_My_DEL'] = Utility().calcDELfromTimeSeries(TowerMy, k_steel)
            DEL_dicts[idx]['Tower_Mz_DEL'] = Utility().calcDELfromTimeSeries(TowerMz, k_steel)


        if PrintDetails:
            print('# ------------------ Exctracting Hub Mx DEL from Bladed ASCII results --------------- #')
        for idx, filename in enumerate(ListOfBladedJobs):  # [11:500]:
            file = os.path.join(RunFolder, filename).replace(runFileEnd, hubFileEnd)
            if PrintDetails:
                print('current file is called: ', file)  # filename = (file.replace(RunFolder + '\\', '', ))

            try:
                csv_data = csv.reader(open(file), delimiter=' ')
            except OSError:
                print('cannot find ', file, '. Will skip and set value to 0.')
                DEL_dicts[idx]['Hub_My_sector_max_DEL'] = 0
                continue

            HubMx = []
            HubMy = []
            HubMz = []
            HubFx = []
            for row in csv_data:
                row = list(filter(None, row))
                HubMx.append(float(row[0]))
                HubMy.append(float(row[1]))
                HubMz.append(float(row[2]))
                HubFx.append(float(row[4]))

            # sum moment vectors in fixed directions and search for worst DEL direction
            # Note: Hub_My is the major moment direction for a two-bladed turbine
            DEL_max = Utility().calcWorstDELsector(HubMz, HubMy, nSectors)
            DEL_dicts[idx]['Hub_Myz_sector_max_DEL'] = DEL_max
            DEL_dicts[idx]['Hub_Mx_DEL'] = Utility().calcDELfromTimeSeries(HubMx, k_steel)
            DEL_dicts[idx]['Hub_My_DEL'] = Utility().calcDELfromTimeSeries(HubMy, k_steel)
            DEL_dicts[idx]['Hub_Mz_DEL'] = Utility().calcDELfromTimeSeries(HubMz, k_steel)
            DEL_dicts[idx]['Hub_Fx_DEL'] = Utility().calcDELfromTimeSeries(HubFx, k_steel)

            if use_hub_fixed_blade_coordinate_system:
                if PrintDetails:
                    print('# -------- Extracting Blade in and out of plane DELs from Hub coordinate system ------- #')
                BladeMx = []
                BladeMy = []
                BladeMz = []
                BladeFz = []
                for row in csv.reader(open(file), delimiter=' '):
                    row = list(filter(None, row))
                    BladeMx.append(float(row[8]))
                    BladeMy.append(float(row[9]))
                    BladeMz.append(float(row[11]))
                    BladeFz.append(float(row[15]))

                DEL_dicts[idx]['Blade_Mx_hub_root_DEL'] = Utility().calcDELfromTimeSeries(BladeMx, k_composite)
                DEL_dicts[idx]['Blade_My_hub_root_DEL'] = Utility().calcDELfromTimeSeries(BladeMy, k_composite)
                DEL_dicts[idx]['Blade_Mz_hub_root_DEL'] = Utility().calcDELfromTimeSeries(BladeMz, k_composite)
                DEL_dicts[idx]['Blade_Fz_hub_root_DEL'] = Utility().calcDELfromTimeSeries(BladeFz, k_composite)


        if PrintDetails:
            print('# ------ Extracting Blade My DEL and Pitch LDC (load duty cycle) from Bladed ASCII results ------ #')
        # if not use_hub_fixed_blade_coordinate_system:
        for idx, filename in enumerate(ListOfBladedJobs):  # [11:500]:
            # bladeFileEnd = '.$41'
            pitchFileEnd = '.$08'
            Pitch_movement_file = os.path.join(RunFolder, filename).replace(runFileEnd, pitchFileEnd)

            Sum_Blade_Mx_DELs = 0
            Sum_Blade_My_DELs = 0
            Sum_Blade_Mz_DELs = 0
            Sum_Blade_Fz_DELs = 0
            Sum_Pitch_LDCs = 0
            for idx_blade in range(nBlades):
                bladeFileEnd = '.$4' + str(idx_blade + 1)
                Blade_load_file = os.path.join(RunFolder, filename).replace(runFileEnd, bladeFileEnd)

                try:
                    csv_data = csv.reader(open(Blade_load_file), delimiter=' ')
                except OSError:
                    print('cannot find ', file, '. Will skip and set value to 0.')
                    DEL_dicts[idx]['Pitch_LDC'] = 0
                    continue
                BladeMx = []  # blade root my moment
                BladeMy = []  # blade root my moment
                BladeMz = []  # blade root my moment
                BladeFz = []  # blade root my moment
                for row in csv_data:
                    row = list(filter(None, row))
                    BladeMx.append(float(row[0]))
                    BladeMy.append(float(row[1]))
                    BladeMz.append(float(row[3]))
                    BladeFz.append(float(row[7]))
                # DEL_dicts[idx]['Blade_My_DEL'] = calcDELfromTimeSeries(BladeMy)
                Sum_Blade_Mx_DELs += Utility().calcDELfromTimeSeries(BladeMx, k_composite)
                Sum_Blade_My_DELs += Utility().calcDELfromTimeSeries(BladeMy, k_composite)
                Sum_Blade_Mz_DELs += Utility().calcDELfromTimeSeries(BladeMz, k_composite)
                Sum_Blade_Fz_DELs += Utility().calcDELfromTimeSeries(BladeFz, k_composite)

                try:
                    csv_data = csv.reader(open(Pitch_movement_file), delimiter=' ')
                except OSError:
                    print('cannot find ', file, '. Will skip and set value to 0.')
                    DEL_dicts[idx]['Pitch_LDC'] = 0
                    continue
                PitchVelo = []  # pitch velocity
                for row in csv_data:
                    row = list(filter(None, row))
                    PitchVelo.append(float(row[nBlades]))

                Pitch_LDC = 0  # pitch load duty cycle
                for i in range(len(BladeMy) - 1):
                    # Pitch_LDC = Pitch_LDC + 1/2* abs(BladeMy[i]*PitchVelo[i] + BladeMy[i+1]*PitchVelo[i+1]) # valid for trapez-rule
                    Pitch_LDC = Pitch_LDC + abs(BladeMy[i] * PitchVelo[i])  # no real difference

                # DEL_dicts[idx]['Pitch_LDC'] = Pitch_LDC
                Sum_Pitch_LDCs += Pitch_LDC

            DEL_dicts[idx]['Blade_Mx_DEL'] = Sum_Blade_Mx_DELs / nBlades
            DEL_dicts[idx]['Blade_My_DEL'] = Sum_Blade_My_DELs / nBlades
            DEL_dicts[idx]['Blade_Mz_DEL'] = Sum_Blade_Mz_DELs / nBlades
            DEL_dicts[idx]['Blade_Fz_DEL'] = Sum_Blade_Fz_DELs / nBlades
            DEL_dicts[idx]['Pitch_LDC'] = Sum_Pitch_LDCs / nBlades

        return DEL_dicts


    def extractStatisticalBladedResultsData(self, RunFolder, ListOfBladedJobs, ULS_search=False):
        '''# in dict: {'VARIAB': , 'FileEnd': , 'Desired': } # not needed for now: DIMENS[1], GENLAB
        Searching =[{'VARIAB': 'Tower My', 'FileEnd': '.%25', 'Desired': 'MAX'},  # 'DIMENS[1]': 0, 'GENLAB': 'Tower member loads - local coordinates', 'FileEnd': '.%25'},
                    {'VARIAB': 'Generator torque', 'FileEnd': '.%06', 'Desired': 'MAX'},  #  , 'DIMENS[1]': 0, 'GENLAB': 'Generator variables', 'FileEnd': '.%06'},
                    {'VARIAB': 'Electrical power', 'FileEnd': '.%06', 'Desired': 'MEAN'},  # , 'DIMENS[1]': 0, 'GENLAB': 'Generator variables', 'FileEnd': '.%06'}]
                    {'VARIAB': 'Generator torque', 'FileEnd': '.%06', 'Desired': 'MAX'},  # 'DIMENS[1]': 0, 'GENLAB': 'Generator variables'
                    {'VARIAB': 'Blade 1 My (Root axes)', 'FileEnd': '.%41', 'Desired': 'MAX'}, # '%42' Blade2, '%43' Blade3 # 'GENLAB': 'Blade 1 Loads: Root axes'
                    {'VARIAB': 'Blade 1 Mx (Root axes)', 'FileEnd': '.%41', 'Desired': 'MAX'}, # '%42' Blade2, '%43' Blade3 # 'GENLAB': 'Blade 1 Loads: Root axes'
                    {'VARIAB': 'pitch_actuator_duty_cycle', 'FileEnd': '.%29', 'Desired': 'MAXMIN_Delta'},  # 'DIMENS[1]': 0, 'GENLAB': 'External Controller'
                    {'VARIAB': 'Rotor speed', 'FileEnd': '.%05', 'Desired': 'MAX'}, # 'DIMENS[1]': 0, 'GENLAB': 'Drive train variables'
                    {'VARIAB': 'Yaw bearing Mxy', 'FileEnd': '.%24', 'Desired': 'MAX'},  # 'DIMENS[1]': 0, 'GENLAB': 'Yaw bearing loads GL coordinates'
                    {'VARIAB': 'Rotating hub Mx', 'FileEnd': '.%22', 'Desired': 'MAX'},  # 'DIMENS[1]': 0, 'GENLAB': 'Hub loads: rotating GL coordinates'
                    {'VARIAB': 'Blade 1 x-deflection (perpendicular to rotor plane)', 'FileEnd': '.%18', 'Desired': 'MAXMIN_Delta'},  # 'DIMENS[1]': 0, 'GENLAB': 'Blade 1 Deflections'
                    {'VARIAB': 'Blade 1 pitch angle', 'FileEnd': '.%08', 'Desired': 'MAXMIN_Delta'}]  # 'DIMENS[1]': 0, 'GENLAB': 'Pitch system' '''
        # if ULS_search:
        #    Statistics_keys = ULS_Searching_keys
        #    Statistics_Searching = ULS_Searching

        Statistics = [dict(zip(Statistics_keys, [0 for _ in range(len(Statistics_keys))]))
                      for _ in range(len(ListOfBladedJobs))]

        # RefFile = fileList[0].replace(PathMainRunFolder + '\\', '').replace('.$PJ','')

        # Filter additional parameters from a reference run
        for Search in Statistics_Searching:
            DidWork = False
            for JobName in ListOfBladedJobs:
                filename = os.path.join(RunFolder, JobName.replace(runFileEnd, '')) + Search.get('FileEnd')
                try:
                    file_data = csv.reader(open(filename), delimiter='\t')
                except OSError:
                    print('could not open file ' + filename + ' for bladed file variable position will try next one')
                else:
                    DidWork = True
                    break
            if DidWork:
                for row in file_data:
                    if row[0].find('DIMENS') != -1:
                        DIMENS = row[1:]

                    if row[0].find('VARIAB') != -1:
                        if PrintDetails:
                            print('found VARIAB: ', row)
                        ASCII_content = row[1][1:-1].split('\' \'')
                        pstn = 0
                        for Content in ASCII_content:
                            if Content == Search.get('VARIAB'):
                                Search['PSTN'] = int(pstn)
                                Search['PSTNs'] = int(DIMENS[0])
                                # Search['FileEnd'] = PrcntFileType
                            pstn = pstn + 1
            else:
                print('None of the runs did work.... Hopefully next generation is better.')
                return Statistics

        # Search through all relevant files for all desired components
        Statistics_old = []  # Values in 'Searching' List will be overwritten in every sub loop
        keys_old = [Search.get('VARIAB') + '_' + Search.get('Desired') for Search in Statistics_Searching]
        if PrintDetails:
            print('Statistics keys are: ', keys_old)
        HelpList = [0 for key in keys_old]
        for file_idx, file in enumerate(ListOfBladedJobs):
            for search_idx, Search in enumerate(Statistics_Searching):
                filename = os.path.join(RunFolder, file.replace(runFileEnd, Search.get('FileEnd')))

                try:
                    file_data = csv.reader(open(filename), delimiter=' ')
                except OSError:
                    print('Something is rotten in the state of denmark!')
                    print('cannot find ', filename, '. Will skip and leave value as 0.')
                    break

                ScrollingULOADS = 0
                FoundMean = 0
                for row in file_data:
                    row[:] = [x for x in row if x]  # remove empty list elements

                    if row[0] == 'ULOADS' or ScrollingULOADS > 0:
                        if ScrollingULOADS < 2 * Search.get('PSTNs'):
                            # print('ScollingULAODS ', ScollingULOADS, ' is smaller than ', 2*Searching[Search_idx].get('PSTNs'))
                            if ScrollingULOADS == Search.get('PSTN') * 2:
                                Search['MAX'] = float(
                                    row[Search.get('PSTN') + (ScrollingULOADS == 0)])  # +1 if first row to scip string
                                # print('MAX in ', row[Search.get('PSTN') + (ScrollingULOADS == 0)])
                            if ScrollingULOADS == Search.get('PSTN') * 2 + 1:
                                Search['MIN'] = float(row[Search.get('PSTN')])
                                # print('MIN in ', row[Search.get('PSTN')])

                        ScrollingULOADS = ScrollingULOADS + 1

                    if row[0] == 'MEAN' and not FoundMean:  # isinstance(Search.get('MEAN'), float) == 0:
                        Search['MEAN'] = float(row[Search.get('PSTN') + 1])
                        # print('MEAN is', row[Search.get('PSTN')+1])
                        FoundMean = 1

                if not Search.get('MIN'):
                    Search['MAXMIN_Delta'] = 0
                else:
                    Search['MAXMIN_Delta'] = Search.get('MAX') - Search.get('MIN')
                # print('MAXMIN_delta is: ', Search.get('MAXMIN_Delta'))

                HelpList[search_idx] = Search.get(Search.get('Desired'))
                Statistics[file_idx][Statistics_keys[search_idx]] = Search.get(Search.get('Desired'))

            Statistics_old.append(dict(zip(keys_old, HelpList)))

        return Statistics

        # writeListDictToCSV(Statistics, os.path.join(PostProResultsFolder, MainFolder + '_Statistics_all.csv'))


    def collectPeakPerRevolution(self, RunFolder='', BladedJob='', rotation_speed_TS=[], teeter_TS=[], deltat=0, time_total=0, AdaptMean = True, VariableName = 'Teeter angle (delta-3 direction)'):
        if rotation_speed_TS:
            TimeSeries = rotation_speed_TS
        else:
            RotorSpeedVariableName = 'Rotor speed'
            fileEnd, idx, DIMENS = Utility().collectTimeSeriesStructureFromBladedFiles(RunFolder, BladedJob, RotorSpeedVariableName)
            TimeSeries = Utility().readTimeSeriesData(RunFolder, BladedJob, fileEnd, idx, DIMENS)
        meanRotorSpeed__rad_per_s = sum(TimeSeries) / len(TimeSeries)
        pi = 3.14159265359
        searchInterval_s = 2 * pi / meanRotorSpeed__rad_per_s
        print('Rotation speed is', meanRotorSpeed__rad_per_s * 60 / 2 / pi,
              'rpm. The interval to search for peaks in the time series is', searchInterval_s, 's')

        if teeter_TS and deltat and time_total:
            TimeSeries = teeter_TS
        else:
            fileEnd, idx, DIMENS = Utility().collectTimeSeriesStructureFromBladedFiles(RunFolder, BladedJob, VariableName)
            TimeSeries = Utility().readTimeSeriesData(RunFolder, BladedJob, fileEnd, idx, DIMENS)
            [time_total, deltat] = Utility().calcTotalTimeAndDeltat(RunFolder, BladedJob)

        OscillationMeanValue = sum(TimeSeries) / len(TimeSeries)
        if AdaptMean:
            print('Shifting TimeSeries mean by ', OscillationMeanValue)
            for idx, value in enumerate(TimeSeries):
                TimeSeries[idx] = value - OscillationMeanValue
            OscillationMeanValue = sum(TimeSeries) / len(TimeSeries)
            if PrintDetails:
                print('New mean value is', OscillationMeanValue)

        Number_Intervals = int(time_total / searchInterval_s * 1.1)
        Values_per_Interval = int(searchInterval_s / deltat)
        TimeSeriesPeaksPerRotation = []
        idx_Peak = 0
        last_idx_Peak = 0
        # search for (teeter) peak in every revolution
        for idx_Interval in range(Number_Intervals):
            # start search from a lower part of the oscillation and include one full circle afterwards
            OneRotationTimeSeries = TimeSeries[int(idx_Peak + Values_per_Interval * 3/5):int(idx_Peak + Values_per_Interval * 5 / 4)]

            if len(OneRotationTimeSeries) < Values_per_Interval/2:
                if PrintDetails:
                    print('Warning: There is no complete interval time series. Stopped peak search to avoid an error.')
                TimeSeries[last_idx_Peak] = TimeSeries[last_idx_Peak] * 4
                break  # avoid a code error if there is nothing to evaluate any more
            MaxIntervalValue = max(OneRotationTimeSeries)
            # to avoid false peak index due to equal peak values
            idx_Peak = TimeSeries.index(MaxIntervalValue)
            if idx_Peak < last_idx_Peak:
                if PrintDetails:
                    print('Note: This peak has a double in the previous time sequence')
                idx_Peak = TimeSeries[last_idx_Peak:-1].index(MaxIntervalValue) + last_idx_Peak

            closeMaxIntervalValue = max(TimeSeries[idx_Peak:int(idx_Peak + Values_per_Interval / 4)])
            if MaxIntervalValue < closeMaxIntervalValue:
                MaxIntervalValue = closeMaxIntervalValue
                idx_Peak = TimeSeries.index(MaxIntervalValue)
                if idx_Peak < last_idx_Peak:
                    if PrintDetails:
                        print('Note: This peak has a double in the previous time sequence')
                    idx_Peak = TimeSeries[last_idx_Peak:-1].index(MaxIntervalValue) + last_idx_Peak

            TimeSeriesPeaksPerRotation.append(MaxIntervalValue)

            # just for visualization
            if idx_Interval > 0:
                TimeSeries[last_idx_Peak] = TimeSeries[last_idx_Peak] * 4

            last_idx_Peak = idx_Peak

        return TimeSeriesPeaksPerRotation, TimeSeries

        '''
        OneRotationTimeSeries = TimeSeries[idx_Interval      * Values_per_Interval + Interval_shift:
                                          (idx_Interval + 1) * Values_per_Interval + Interval_shift]
        # control if the new peak is not part of the same oscillation
        if idx_Peak - last_idx_Peak < Values_per_Interval / 2:
            if len(TimeSeriesPeaksPerRotation) > 1:
                if TimeSeriesPeaksPerRotation[-1] < MaxIntervalValue:# and TimeSeriesPeaksPerRotation[-1] > OscillationMeanValue:
                    print('Heureka', TimeSeriesPeaksPerRotation[-1], 'is smaller than', MaxIntervalValue,
                          'at index', TimeSeries.index(MaxIntervalValue))
                    TimeSeriesPeaksPerRotation[-1] = MaxIntervalValue

                    print('shifting by ', idx_Peak - (idx_Interval * Values_per_Interval + Interval_shift))
                    Interval_shift += idx_Peak - (idx_Interval * Values_per_Interval + Interval_shift)

            for idx, value in enumerate(OneRotationTimeSeries):
                if value < OscillationMeanValue:
                    break
            Interval_shift += idx
            OneRotationTimeSeries = TimeSeries[idx_Interval      * Values_per_Interval + Interval_shift:
                                              (idx_Interval + 1) * Values_per_Interval + Interval_shift]
            if len(OneRotationTimeSeries) < Values_per_Interval:
                print('Warning: Stopped peak search to avoid an error. There is no complete interval time series.')
                break  # avoid a code error if there is nothing to evaluate any more
            MaxIntervalValue = max(OneRotationTimeSeries)
            '''
    def change_dict_for_DLC12_iterations(self, ref_turbulence_intensity=0.12, lateral_turbulence_fraction=0.8,
                                         upward_turbulence_fraction=0.5,  sim_output_time=200, sim_end_time=3800,
                                         change_wave_files=True, wind_shear=0.14, turbulence_type='kaimal', nSeeds=1,
                                         wind_type='NTM', V_ave=11.4, seastate='NSS'):
        # List of wave files (if needed)
        sea_file_folder = r'H:\BladedWS\FOWTs\environmental_conditions\\'
        ListOfSeaFiles = []
        ListOfSeaFiles.append('wave_NSS_05mps_1_14m_8_415s_g1')
        ListOfSeaFiles.append('wave_NSS_07mps_1_25m_8_16s_g1')
        ListOfSeaFiles.append('wave_NSS_09mps_1_43m_7_83s_g1')
        ListOfSeaFiles.append('wave_NSS_11mps_1_69m_7_545s_g1')
        ListOfSeaFiles.append('wave_NSS_13mps_2_015m_7_45s_g1')
        ListOfSeaFiles.append('wave_NSS_15mps_2_395m_7_55s_g1_175')
        ListOfSeaFiles.append('wave_NSS_17mps_2_83m_7_845s_g1_47')
        ListOfSeaFiles.append('wave_NSS_19mps_3_34m_8_285s_g1_705')
        ListOfSeaFiles.append('wave_NSS_21mps_3_825m_8_755s_g1_82')
        ListOfSeaFiles.append('wave_NSS_23mps_4_275m_9_22s_g1_855')
        ListOfSeaFiles.append('wave_NSS_25mps_4_765m_9_68s_g1_925')
        if seastate != 'NSS':
            print('generating files with severe sea state (SSS)')
            ListOfSeaFiles = []
            ListOfSeaFiles.append('wave_SSS_05mps_7_15m_12_1s_g2_75')
            ListOfSeaFiles.append('wave_SSS_07mps_8_00m_12_7s_g2_75')
            ListOfSeaFiles.append('wave_SSS_09mps_8_05m_12_75s_g2_75')
            ListOfSeaFiles.append('wave_SSS_11mps_8_30m_12_95s_g2_75')
            ListOfSeaFiles.append('wave_SSS_13mps_8_50m_13_10s_g2_75')
            ListOfSeaFiles.append('wave_SSS_15mps_9_15m_13_60s_g2_75')
            ListOfSeaFiles.append('wave_SSS_17mps_9_80m_14_10s_g2_75')
            ListOfSeaFiles.append('wave_SSS_19mps_9_80m_14_10s_g2_75')
            ListOfSeaFiles.append('wave_SSS_21mps_9_80m_14_10s_g2_75')
            ListOfSeaFiles.append('wave_SSS_23mps_9_80m_14_10s_g2_75')
            ListOfSeaFiles.append('wave_SSS_25mps_9_80m_14_10s_g2_75')

        #ListOfSeeds = [121, 264, 473, 551, ]

        if turbulence_type == 'mann':
            turbulence_file_folder = r'h:\Bladedws\bottomfixed\dlc_legacy\ntm_kaimal_windfiles_5to25mps'
        elif turbulence_type == 'kaimal':
            turbulence_file_folder = r'H:\BladedWS\windfiles_kaimal_5to25mps'
        else:
            print('WARNING: desired turbulence_type is not part of the pre-defined list')

        ListOfChangeDicts = []
        for idx, wind_speed in enumerate(range(5, 26, 2)):
            for idx_seed in range(nSeeds):
                if wind_type == 'NTM':
                    # calc longitudinal turbulence intensity according to IEC 61400-1 ed. 4
                    TI = ref_turbulence_intensity * (0.75 * wind_speed + 5.6) / wind_speed
                if wind_type == 'ETM':
                    TI = 2 * ref_turbulence_intensity * (0.072 * (V_ave/2 + 3) * (wind_speed/2 - 4) + 10) / wind_speed

                ChangeDicts = []
                # change the wind
                ChangeDicts.append({'WORD': 'UBAR', 'EXCHANGE': 'UBAR	 ' + '%i' % wind_speed})
                ChangeDicts.append({'WORD': 'TI	', 'EXCHANGE': 'TI	 ' + ('%0.5f' % TI)[1:]})
                ChangeDicts.append(
                    {'WORD': 'TI_V	', 'EXCHANGE': 'TI_V	 ' + ('%0.5f' % (TI * lateral_turbulence_fraction))[1:]})
                ChangeDicts.append(
                    {'WORD': 'TI_W	', 'EXCHANGE': 'TI_W	 ' + ('%0.5f' % (TI * upward_turbulence_fraction))[1:]})
                if turbulence_type == 'kaimal':
                    ChangeDicts.append({'WORD': 'WINDF', 'EXCHANGE': r'WINDF	' + turbulence_file_folder + r'\ntm_kaimal_%02imps_s%01i%02i.wnd' % (wind_speed, int(idx_seed + 1), wind_speed)})
                else:
                    ChangeDicts.append({'WORD': 'WINDF', 'EXCHANGE': r'WINDF	' + turbulence_file_folder + r'\wind_%02imps_s%02i.wnd' % (wind_speed, wind_speed)})
                    # old: ChangeDicts.append({'WORD': 'WINDF', 'EXCHANGE': r'WINDF	h:\bladedws\fowts\environmental_conditions\wind_%02imps_s%02i.wnd' % (wind_speed, wind_speed)})

                ChangeDicts.append({'WORD': 'WSHEAR', 'EXCHANGE': 'WSHEAR	 ' + ('%0.2f' % wind_shear)[1:]})
                if change_wave_files:  # waves
                    ChangeDicts.append({'WORD': '        <SpectrumFilePath>', 'EXCHANGE': '        <SpectrumFilePath>' + sea_file_folder + ListOfSeaFiles[idx] + r'.SEA</SpectrumFilePath>'})
                # change simulation time
                ChangeDicts.append({'WORD': 'OUTSTR', 'EXCHANGE': 'OUTSTR	 %i' % sim_output_time})
                ChangeDicts.append({'WORD': 'ENDT', 'EXCHANGE': 'ENDT	 %i' % sim_end_time})
                ListOfChangeDicts.append(ChangeDicts)

        return ListOfChangeDicts

    def change_dict_for_tower_steel_youngs_modulus__v2(self, multiplier, baseline_file_path, n_tower_sections=9):

        infile = open((baseline_file_path + '.$PJ'), "r")
        found_material = False
        # found_tower_properties = False
        n = n_tower_sections
        for row in infile:
            if found_material:  # happens one row after the material property identifier has been found
                row_filtered = row.replace('\n', '')
                row_splitted = row_filtered.split('\t ')
                old_youngs_modulus = row_splitted[2]
                new_youngs_modulus = '%.1E' % (float(old_youngs_modulus) * multiplier)
                ChangeDicts = [{'WORD': row_filtered, 'EXCHANGE': row_filtered.replace(old_youngs_modulus, new_youngs_modulus)}]
                if PrintDetails:
                    print('was: ' + row)
                found_material = False

            if row.find('NOMATS') != -1:
                found_material = True

            if row.find('TOWEAX') != -1 or row.find('TOWEIY') != -1 or row.find('TOWEIZ') != -1 or n < n_tower_sections:
                if n == n_tower_sections:
                    n = 0
                row_filtered = row.replace('\n', '')
                row_splitted = row_filtered.split(' ')
                old_value_one = row_splitted[-1]
                old_value_two = row_splitted[-2]
                new_value_one = '%.3E' % (float(old_value_one) * multiplier)
                new_value_two = '%.3E' % (float(old_value_two) * multiplier)

                ChangeDicts.append({'WORD': row_filtered, 'EXCHANGE': row_filtered.replace(old_value_one, new_value_one).replace(old_value_two, new_value_two)})

                n += 1

        return ChangeDicts


    def automized_bulk_mstarts_in_files_changer(self, masterfile='', childmainfolder='', slavefile='', outmainfolder = '', change_snip = '', new_snip= '',
            mstart_names=['MSTART CONSTANTS', 'MSTART WINDSEL', 'MSTART SIMCON', 'MSTART WINDV', 'MSTART GENFAIL', 'MSTART PITCHFAIL', 'MSTART INITCON', 'MSTART IDLING', 'MSTART BRAKE', 'MSTART PLOAD']):
        """
        This script is supposed to use a Bladed baseline file ("slavefile"), where all turbine parameters are as desired
        and copy all mstarts, the wave-*.SEA-file etc., which specify the operation status, environmental and fault
        conditions, of all files of a baseline folder ("childmainfolder") into a new Bladed project file in the
        "out_folder". If needed, the run names of the childmainfolder can be adapted a "change_snip" and exchanged by
        the "new_snip". This function should also work with sub-folders.

        :param masterfile:      Bladed run files from which the simulated environment and conditions are taken
        :param childmainfolder: (main) folder, that contains the masterfiles
        :param slavefile:       Bladed run file, that possesses the desired turbine and control parameters
        :param outmainfolder:   (main) folder in which the combined Bladed run files are stored
        :param change_snip:     String that is a part of the masterfile which should be changed
        :param new_snip:        String that should be replaced by change_snip
        :param mstart_names:    Contains all "mstart" sections that should be copied from the masterfile in the new file
        :return:                outfiles
        """

        if not masterfile:
            print(' ---> Missing masterfile. Using predefined mstart names ---> ', mstart_names)

        subfolders = [folder[0] for folder in os.walk(childmainfolder)]
        print('found folders ---> ', subfolders)

        Utility().createFolderIfNotExcisting(outmainfolder)
        childfiles = []
        outfiles = []
        for subfolder in subfolders:
            childfiles = Utility().return_run_files_in_folder(subfolder)
            if childfiles:
                print('found in folder ---> ', subfolder, ' the files --->', childfiles)
                new_subfolder = subfolder.replace(childmainfolder, outmainfolder).replace(change_snip, new_snip)
                print('creating folder ---> ', new_subfolder)
                Utility().createFolderIfNotExcisting(new_subfolder)

                for childfile in childfiles:
                    outfile = childfile.replace(subfolder, new_subfolder).replace(change_snip, new_snip)
                    print('      compiling ---> ', outfile)
                    self.mstarts_in_files_changer(masterfile=masterfile, childfile=childfile, slavefile=slavefile, outfile=outfile, mstart_names=mstart_names)
                    outfiles.append(outfile)

        return outfiles


    def mstarts_in_files_changer(self, masterfile='', childfile='', slavefile='', outfile='', mstart_names=[]):

        child_infile = open(childfile, "r").readlines()

        list_of_MSTART_change_dicts = []
        if masterfile:
            master_infile = open(masterfile, "r").readlines()
            for idx_old, master_infile_row in enumerate(master_infile):
                if master_infile_row.find('MSTART') != -1:
                    mstart_name = master_infile_row
                    mstart_idx = idx_old
                if master_infile_row.find('MEND') != -1:
                    mend_idx = idx_old + 1
                    for idx_new, child_infile_row in enumerate(child_infile):
                        if child_infile_row.find(mstart_name) != -1:
                            if not master_infile[mstart_idx:mend_idx] == child_infile[idx_new:idx_new + (mend_idx- mstart_idx)]:
                                list_of_MSTART_change_dicts.append({'MSTART': mstart_name,
                                                                    'EXCHANGE': child_infile[idx_new:idx_new + (mend_idx - mstart_idx)]})
                                # print(child_infile[idx_new:idx_new + (mend_idx - mstart_idx)])
                                break
        else:
            for mstart_name in mstart_names:
                mstart_idx = 0
                for idx, child_infile_row in enumerate(child_infile):
                    if child_infile_row.find(mstart_name) != -1:
                        mstart_idx = idx
                    if mstart_idx != 0 and child_infile_row.find('MEND') != -1:
                        list_of_MSTART_change_dicts.append({'MSTART': mstart_name,
                                                            'EXCHANGE': child_infile[mstart_idx:idx + 1]})
                        # print(child_infile[idx_new:idx_new + (mend_idx - mstart_idx)])
                        break

        for idx, child_infile_row in enumerate(child_infile):
            if child_infile_row.find('<Calculation>') != -1:
                calculation_type = child_infile_row.split('>')[1].split('<')[0]
                break

        # change *.SEA-file
        for idx, child_infile_row in enumerate(child_infile):
            if child_infile_row.find('<SpectrumFilePath>') != -1:
                SEA_file = child_infile_row.split('>')[1].split('<')[0]
                break

        slave_infile = open(slavefile, "r").readlines()
        mstart_idx = 0
        for MSTART_change_dict in list_of_MSTART_change_dicts:
            for idx, row in enumerate(slave_infile):
                if row.find(MSTART_change_dict.get('MSTART')) != -1:
                    mstart_idx = idx
                if mstart_idx != 0 and row.find('MEND') != -1:
                    slave_infile[mstart_idx:idx + 1] = MSTART_change_dict.get('EXCHANGE')
                    mstart_idx = 0
                    break

        trigger = False
        for idx, row in enumerate(slave_infile):
            if row.find('<RunConfiguration>') != -1:
                trigger = True
            if row.find('<Name>') != -1 and trigger:
                trigger = False
                slave_infile[idx] = '  <Name>' + outfile.split('\\')[-1].split('.')[0] + '</Name>\n'
            if row.find('CALCULATION	') != -1:
                slave_infile[idx] = 'CALCULATION	' + calculation_type + '\n'
            if row.find('<SpectrumFilePath>') != -1:
                slave_infile[idx] = '        <SpectrumFilePath>' + SEA_file + '</SpectrumFilePath>\n'
            if row.find('<Calculation>') != -1:
                slave_infile[idx] = '  <Calculation>' + calculation_type + '</Calculation>\n'
                #break

        slave_outfile = open(outfile, "w")
        for row in slave_infile:
            slave_outfile.write(row)
        slave_outfile.close()

        return list_of_MSTART_change_dicts


    def ULS_DLCs_evaluation_summarizer(self, documentation_path, search_for_ULS_among_blades=True):
        # partial safety factor. Note: DLC2.2 is stuck pitch, but has often been falsely labeled as DLC2.1
        PSF_dict = {'DLC13': 1.35, 'DLC14': 1.35, 'DLC15': 1.35, 'DLC16': 1.35, 'DLC22': 1.10, 'DLC23': 1.35,
                    'DLC51': 1.35, 'DLC61': 1.35, 'DLC62': 1.10, 'DLC63': 1.35, 'DEFAULT': 1.35, 'DLC12': 1.25}

        def ULS_checker(key, ULS, ULS_jobname, ULS_check, job_name):
            PSF = PSF_dict.get('DLC' + job_name.split('DLC')[-1][0:2])
            if not PSF:
                print('   ---> could not find DLC' + job_name.split('DLC')[-1][0:2], 'in', PSF_dict,
                      ' Will use default value.')
                PSF = PSF_dict.get('DEFAULT')
            if key.find('AMAX') != -1:
                if abs(ULS) < abs(ULS_check):
                    ULS = ULS_check
                    ULS_jobname = job_name
            elif key.find('MAX') != -1:
                if ULS < ULS_check:
                    ULS = ULS_check
                    ULS_jobname = job_name
            elif key.find('MIN') != -1:
                if ULS > ULS_check:
                    ULS = ULS_check
                    ULS_jobname = job_name
            else:  # ULS:
                ULS_check = ULS_check * PSF
                if abs(ULS) < abs(ULS_check):
                    ULS = ULS_check
                    ULS_jobname = job_name
            return [ULS, ULS_jobname]

        results_list_dict = Utility().readListDictFromCSV(documentation_path)
        ULS_summary_list_dict = []
        found_seed = False
        for legend in ['DLC', 'run', 'ULS']:
            ULS_summary_list_dict.append({documentation_path.split('\\')[-1]: legend})

        keys = list(results_list_dict[0].keys())[1:]
        for key_idx, key in enumerate(keys):
        # for key_idx, key in enumerate(list(results_list_dict[0].keys())[1:]):
            ULS = float(results_list_dict[0].get(key))
            ULS_jobname = results_list_dict[0].get(list(results_list_dict[0].keys())[0])
            seed_nmbr_memory = []
            seed_ULS_memory = []
            run_name_details = ''
            for idx, result_dict in enumerate(results_list_dict):
                job_name_key = list(result_dict.keys())[0]
                job_name = result_dict.get(job_name_key).split('\\')[-1].split('.')[0]
                local_ULS = float(result_dict.get(key))
                found_seed = False
                for seed_identifier in ['_s', '_azi']:
                    if job_name.find(seed_identifier) != -1:
                        seed_nmbr = job_name.split(seed_identifier)[-1]  # [0:3]
                        seed_name_idx = job_name.index(seed_identifier + seed_nmbr)
                        if seed_nmbr.isnumeric():
                            found_seed = True
                            if (seed_nmbr in seed_nmbr_memory or run_name_details != job_name[
                                                                                     0:seed_name_idx]) and seed_ULS_memory:
                                mean_ULS_memory = mean(seed_ULS_memory)
                                [ULS, ULS_jobname] = ULS_checker(key=key, ULS=ULS, ULS_jobname=ULS_jobname,
                                                                 ULS_check=mean_ULS_memory, job_name=job_name_memory)
                                seed_nmbr_memory = []  # = [seed_nmbr]
                                seed_ULS_memory = []  # = [local_ULS]

                            seed_nmbr_memory.append(seed_nmbr)
                            seed_ULS_memory.append(local_ULS)

                if not found_seed and idx:
                    if seed_ULS_memory:
                        mean_ULS_memory = mean(seed_ULS_memory)
                        [ULS, ULS_jobname] = ULS_checker(key=key, ULS=ULS, ULS_jobname=ULS_jobname,
                                                         ULS_check=mean_ULS_memory,
                                                         job_name=job_name_memory)
                        seed_nmbr_memory = []  # = [seed_nmbr]
                        seed_ULS_memory = []  # = [local_ULS]

                    [ULS, ULS_jobname] = ULS_checker(key=key, ULS=ULS, ULS_jobname=ULS_jobname, ULS_check=local_ULS,
                                                     job_name=result_dict.get(job_name_key))

                try:  # seed_name_idx might not be defined yet
                    run_name_details = job_name[0:seed_name_idx]
                except:
                    pass
                job_name_memory = result_dict.get(job_name_key)

            if found_seed:
                mean_ULS_memory = mean(seed_ULS_memory)
                [ULS, ULS_jobname] = ULS_checker(key=key, ULS=ULS, ULS_jobname=ULS_jobname, ULS_check=mean_ULS_memory,
                                                 job_name=job_name_memory)

            DLC_number = ULS_jobname.split('DLC')[-1][0:2]
            DLC_name = 'DLC' + DLC_number[0] + '.' + DLC_number[1]
            print(key, 'ULS is', ULS, 'for run', ULS_jobname)
            # ULS_summary_list_dict.append({job_name_key:ULS_jobname, 'DLC': DLC_name, 'Load': key, 'ULS': ULS})
            ULS_summary_list_dict[0][key] = DLC_name
            ULS_summary_list_dict[1][key] = ULS_jobname
            ULS_summary_list_dict[2][key] = ULS

        print(ULS_summary_list_dict)

        # search for the maximum among all blades
        if search_for_ULS_among_blades:
            ULS_check_among_blades_indexes = []
            ULS_check_among_blades_indexes_blacklist = []
            for key_idx, key in enumerate(keys):
                if key.find('Blade') != -1 and not key_idx in ULS_check_among_blades_indexes_blacklist:
                    ULS_check_among_blades_indexes.append([key_idx])
                    for blade_number in range(2, 4, 1):
                        search_key = key.replace('1', str(blade_number))
                        for check_key_idx, check_key in enumerate(keys):
                            if search_key == check_key:
                                ULS_check_among_blades_indexes[-1].extend([check_key_idx])
                                ULS_check_among_blades_indexes_blacklist.append(check_key_idx)

            for ULS_check_among_blades_index in ULS_check_among_blades_indexes:
                if len(ULS_check_among_blades_index) > 1:  # check whether there are other blade ULS to find highest
                    first_index = ULS_check_among_blades_index[0]
                    first_key = keys[first_index]
                    change_key = keys[first_index].replace('1', 'all')
                    DLC_name = ULS_summary_list_dict[0].get(keys[first_index])
                    ULS_jobname = ULS_summary_list_dict[1].get(keys[first_index])
                    ULS = ULS_summary_list_dict[2].get(keys[first_index])
                    for check_blade_index in ULS_check_among_blades_index[1:]:  # list starts from second value
                        check_ULS = ULS_summary_list_dict[2].get(keys[check_blade_index])
                        if change_key.find('MIN') != -1:
                            if ULS > check_ULS:
                                UlS = copy(check_ULS)
                                DLC_name = ULS_summary_list_dict[0].get(keys[check_blade_index])
                                ULS_jobname = ULS_summary_list_dict[1].get(keys[check_blade_index])
                        else:  # accounts for AMAX, MAX and ULS
                            if abs(ULS) < abs(check_ULS):
                                ULS = copy(check_ULS)
                                DLC_name = ULS_summary_list_dict[0].get(keys[check_blade_index])
                                ULS_jobname = ULS_summary_list_dict[1].get(keys[check_blade_index])

                    # update the summary dictionaries
                    ULS_summary_list_dict[0][first_key] = copy(DLC_name)
                    ULS_summary_list_dict[1][first_key] = copy(ULS_jobname)
                    ULS_summary_list_dict[2][first_key] = copy(ULS)

                    ULS_summary_list_dict_update = []
                    for legend in ['DLC', 'run', 'ULS']:
                        ULS_summary_list_dict_update.append({documentation_path.split('\\')[-1]: legend})
                    for key_idx, key in enumerate(keys):
                        if key == first_key:
                            keys[key_idx] = change_key
                        ULS_summary_list_dict_update[0][keys[key_idx]] = ULS_summary_list_dict[0].get(key)
                        ULS_summary_list_dict_update[1][keys[key_idx]] = ULS_summary_list_dict[1].get(key)
                        ULS_summary_list_dict_update[2][keys[key_idx]] = ULS_summary_list_dict[2].get(key)
                    ULS_summary_list_dict = copy(ULS_summary_list_dict_update)

            # shorten dictionary from further blades. Has to be done after the ULS check among the blades.
            for ULS_check_among_blades_index in ULS_check_among_blades_indexes:
                if len(ULS_check_among_blades_index) > 1:
                    for check_blade_index in ULS_check_among_blades_index[1:]:
                        ULS_summary_list_dict[0].pop(keys[check_blade_index])
                        ULS_summary_list_dict[1].pop(keys[check_blade_index])
                        ULS_summary_list_dict[2].pop(keys[check_blade_index])

        documentation_path = documentation_path.split('.')[0] + '_summary.csv'
        Utility().writeListDictToCSV(ULS_summary_list_dict, documentation_path)








""" ====================================================================================================================

              This class contains a cost function that runs Bladed automatically and post-processes Bladed results
                         ------------------------------------------------------------------

            1. Reference run (for the control cost criterion (CCC)) gets evaluated during the initialization
            2. Method runs trough the following steps and memorizes the result every time being executed:
                2.1  Manipulates Bladed project files (.$PJ) for the given parameters
                2.2  Runs new project files (if not already existing)
                2.3  Evaluates Statistics and DELs (Damage Equivalent Loads) and combines the result in one list
                2.4  Store results in a file (which can be used later or in between executing the function)
            The main parameter that is evaluated in typical optimization loops is the output parameter "CCC",
            the control cost criterion. However, other parameters would be possible as well.                

==================================================================================================================== """
class BladedOptimizationFunction: # (object):
    def __init__(self, ListOfBaselineFiles, searchWords, addToRunFileNames, documentation_path):
        self.ListOfBaselineFiles = ListOfBaselineFiles
        self.searchWords = searchWords
        self.addToRunFileNames = addToRunFileNames
        self.DocString = DocString
        self.documentation_path = documentation_path

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

        if self.Statistics_ref[0].get('Power_mean') > 20000000*0.95:
            self.full_load_operation_CCC = True
            print('full load operation detected.')
        else:
            self.full_load_operation_CCC = False
            print('partial load operation detected')

        print('maximum rotation speed is: ' + str(self.Statistics_ref[0].get('RotationSpeed_max'))
              + ' and max allowed is: ' + str(max_rotation_speed_bound))

    def BladedOptimizationFunction(self, Params):

        print('\n\n# -------------- THIS IS GENERATION ' + str(self.Iteration_idx) + ' -------------- #\n\n')

        print('The Params are: ', Params)
        # Params = [Params[i] for i in range(nParams)]

        print('# ------- starting to manipulate Bladed job files ------- #')
        ListOfBladedJobs, RunFolder = Utility().manipulatePRJfiles(Params, self.Iteration_idx, searchWords_local=self.searchWords,
               ListOfBaselineFiles_local=self.ListOfBaselineFiles, addToRunFileNames_local=self.addToRunFileNames)

        print('# -------- starting to run Bladed jobs in Batch --------- #')
        Bladed().AutoRunBatch(RunFolder, ListOfBladedJobs, skip_if_existing=True,
                              job_list_name=self.documentation_path.split('\\')[-1].split('.')[0])

        print('# ----------- starting with CCC calculation ------------- #')
        Statistics = Bladed().extractStatisticalBladedResultsData(RunFolder, ListOfBladedJobs)
        DEL_dicts = Bladed().extractDEL_towerHubBlade(RunFolder, ListOfBladedJobs)
        [Statistics[i].update(DEL_dicts[i]) for i in range(len(Statistics))]

        '''if nSeeds > 1:
            print('calculation mean of ' + str(nSeeds) + ' Seeds')
            print('CAUTION: is not validated any more')
            Statistics = Utility().calcMeanValuesForSeeds(Statistics)  #, nSeeds)
            DEL_dicts = Utility().calcMeanValuesForSeeds(DEL_dicts)    #, nSeeds) '''

        CCCs = [Utility().calcCCC(Statistic, self.Statistics_ref[0],
                                  full_load_operation_CCC=self.full_load_operation_CCC) for Statistic in Statistics]

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

        Utility().writeListDictToCSV(self.Documentation, self.documentation_path)

        # for later visualization
        self.Plot_documentary.append(
            dict(zip(['Iteration', 'global_best_CCC', 'step_best_CCC', 'AverageCCC']
                     + ['step_best_Parameters ' + str(j + 1) for j in range(nParams)]
                     + ['global_best_Parameters ' + str(j + 1) for j in range(nParams)],
                     [self.Iteration_idx, global_best_CCC, self.MinCCC[-1], sum(CCCs) / len(CCCs)]
                     + [j for j in self.BestParameters[-1]]
                     + [j for j in global_best_Params])))
        Utility().writeListDictToCSV(self.Plot_documentary, self.documentation_path.split('.')[0] + '_plot.csv')

        print('global_best_CCC: ', global_best_CCC, '   with global_best_Params: ', global_best_Params)

        self.Iteration_idx += 1

        if len(Statistics) == 1:
            return CCCs[-1]    # Otherwise, there is a List of a List with only a single value
        else:
            return CCCs







''' DELETE AFTER TIME:

    def change_dict_for_tower_steel_youngs_modulus(self, multiplier, FOWT=True):
        # data has to be copied out of project file...
        if FOWT:
            ChangeDicts = [{'WORD': '\'Steel\'	 7850	 ', 'EXCHANGE': '\'Steel\'	 7850	 %.1fE+11	 7.93E+10' % (2 * multiplier)}]

            ChangeDicts.append({'WORD': 'TOWEAX 1.377E+11 1.451E+11', 'EXCHANGE': 'TOWEAX %.3f' % (1.377 * multiplier) + 'E+11 %.3f' % (1.451 * multiplier) + 'E+11'})
            ChangeDicts.append({'WORD': ' 1.596E+11 1.673E+11', 'EXCHANGE': ' %.3fE+11 %.3fE+11' % (1.596 * multiplier, 1.673 * multiplier)})
            ChangeDicts.append({'WORD': ' 1.824E+11 1.908E+11', 'EXCHANGE': ' %.3fE+11 %.3fE+11' % (1.824 * multiplier, 1.908 * multiplier)})
            ChangeDicts.append({'WORD': ' 2.066E+11 2.157E+11', 'EXCHANGE': ' %.3fE+11 %.3fE+11' % (2.066 * multiplier, 2.157 * multiplier)})
            ChangeDicts.append({'WORD': ' 2.323E+11 2.421E+11', 'EXCHANGE': ' %.3fE+11 %.3fE+11' % (2.323 * multiplier, 2.421 * multiplier)})
            ChangeDicts.append({'WORD': ' 2.593E+11 2.698E+11', 'EXCHANGE': ' %.3fE+11 %.3fE+11' % (2.593 * multiplier, 2.698 * multiplier)})
            ChangeDicts.append({'WORD': ' 2.877E+11 2.989E+11', 'EXCHANGE': ' %.3fE+11 %.3fE+11' % (2.877 * multiplier, 2.989 * multiplier)})
            ChangeDicts.append({'WORD': ' 3.175E+11 3.294E+11', 'EXCHANGE': ' %.3fE+11 %.3fE+11' % (3.175 * multiplier, 3.294 * multiplier)})
            ChangeDicts.append({'WORD': ' 3.487E+11 3.502E+11', 'EXCHANGE': ' %.3fE+11 %.3fE+11' % (3.487 * multiplier, 3.502 * multiplier)})

            ChangeDicts.append({'WORD': 'TOWEIY 1.034E+12 1.209E+12', 'EXCHANGE': 'TOWEIY %.3fE+12 %.3fE+12' % (1.034 * multiplier, 1.209 * multiplier)})
            ChangeDicts.append({'WORD': ' 1.329E+12 1.531E+12', 'EXCHANGE': ' %.3fE+12 %.3fE+12' % (1.329 * multiplier, 1.531 * multiplier)})
            ChangeDicts.append({'WORD': ' 1.668E+12 1.909E+12', 'EXCHANGE': ' %.3fE+12 %.3fE+12' % (1.668 * multiplier, 1.909 * multiplier)})
            ChangeDicts.append({'WORD': ' 2.067E+12 2.352E+12', 'EXCHANGE': ' %.3fE+12 %.3fE+12' % (2.067 * multiplier, 2.352 * multiplier)})
            ChangeDicts.append({'WORD': ' 2.53E+12 2.864E+12',  'EXCHANGE': ' %.3fE+12 %.3fE+12' % (2.53 * multiplier,  2.864 * multiplier)})
            ChangeDicts.append({'WORD': ' 3.066E+12 3.454E+12', 'EXCHANGE': ' %.3fE+12 %.3fE+12' % (3.066 * multiplier, 3.454 * multiplier)})
            ChangeDicts.append({'WORD': ' 3.681E+12 4.128E+12', 'EXCHANGE': ' %.3fE+12 %.3fE+12' % (3.681 * multiplier, 4.128 * multiplier)})
            ChangeDicts.append({'WORD': ' 4.382E+12 4.894E+12', 'EXCHANGE': ' %.3fE+12 %.3fE+12' % (4.382 * multiplier, 4.894 * multiplier)})
            ChangeDicts.append({'WORD': ' 5.178E+12 5.249E+12', 'EXCHANGE': ' %.3fE+12 %.3fE+12' % (5.178 * multiplier, 5.249 * multiplier)})

            # note, this is equal to the lines above except of TOWEIY
            ChangeDicts.append({'WORD': 'TOWEIZ 1.034E+12 1.209E+12', 'EXCHANGE': 'TOWEIZ %.3fE+12 %.3fE+12' % (1.034 * multiplier, 1.209 * multiplier)})
            ChangeDicts.append({'WORD': ' 1.329E+12 1.531E+12', 'EXCHANGE': ' %.3fE+12 %.3fE+12' % (1.329 * multiplier, 1.531 * multiplier)})
            ChangeDicts.append({'WORD': ' 1.668E+12 1.909E+12', 'EXCHANGE': ' %.3fE+12 %.3fE+12' % (1.668 * multiplier, 1.909 * multiplier)})
            ChangeDicts.append({'WORD': ' 2.067E+12 2.352E+12', 'EXCHANGE': ' %.3fE+12 %.3fE+12' % (2.067 * multiplier, 2.352 * multiplier)})
            ChangeDicts.append({'WORD': ' 2.53E+12 2.864E+12' , 'EXCHANGE': ' %.3fE+12 %.3fE+12' % (2.53 * multiplier,  2.864 * multiplier)})
            ChangeDicts.append({'WORD': ' 3.066E+12 3.454E+12', 'EXCHANGE': ' %.3fE+12 %.3fE+12' % (3.066 * multiplier, 3.454 * multiplier)})
            ChangeDicts.append({'WORD': ' 3.681E+12 4.128E+12', 'EXCHANGE': ' %.3fE+12 %.3fE+12' % (3.681 * multiplier, 4.128 * multiplier)})
            ChangeDicts.append({'WORD': ' 4.382E+12 4.894E+12', 'EXCHANGE': ' %.3fE+12 %.3fE+12' % (4.382 * multiplier, 4.894 * multiplier)})
            ChangeDicts.append({'WORD': ' 5.178E+12 5.249E+12', 'EXCHANGE': ' %.3fE+12 %.3fE+12' % (5.178 * multiplier, 5.249 * multiplier)})

        elif False:
            # data has to be copied out of project file...
            ChangeDicts = [{'WORD': '\'Steel\'	 8500	 ', 'EXCHANGE': '\'Steel\'	 8500	 %.1fE+11	 7.93E+10' % (2.1 * multiplier)}]

            ChangeDicts.append({'WORD': 'TOWEAX 3.717E+11 3.667E+11', 'EXCHANGE': 'TOWEAX %.3f' % (3.717 * multiplier) + 'E+11 %.3f' % (3.667 * multiplier) + 'E+11'})
            ChangeDicts.append({'WORD': ' 3.452E+11 3.328E+11', 'EXCHANGE': ' %.3fE+11 %.3fE+11' % (3.452 * multiplier, 3.328 * multiplier)})
            ChangeDicts.append({'WORD': ' 3.121E+11 3.004E+11', 'EXCHANGE': ' %.3fE+11 %.3fE+11' % (3.121 * multiplier, 3.004 * multiplier)})
            ChangeDicts.append({'WORD': ' 2.804E+11 2.695E+11', 'EXCHANGE': ' %.3fE+11 %.3fE+11' % (2.804 * multiplier, 2.695 * multiplier)})
            ChangeDicts.append({'WORD': ' 2.567E+11 2.463E+11', 'EXCHANGE': ' %.3fE+11 %.3fE+11' % (2.567 * multiplier, 2.463 * multiplier)})
            ChangeDicts.append({'WORD': ' 2.279E+11 2.181E+11', 'EXCHANGE': ' %.3fE+11 %.3fE+11' % (2.279 * multiplier, 2.181 * multiplier)})
            ChangeDicts.append({'WORD': ' 2.005E+11 1.919E+11', 'EXCHANGE': ' %.3fE+11 %.3fE+11' % (2.005 * multiplier, 1.919 * multiplier)})
            ChangeDicts.append({'WORD': ' 1.75E+11 1.669E+11', 'EXCHANGE': ' %.3fE+11 %.3fE+11' % ( 1.750 * multiplier, 1.669 * multiplier)})
            ChangeDicts.append({'WORD': ' 1.508E+11 1.432E+11', 'EXCHANGE': ' %.3fE+11 %.3fE+11' % (1.508 * multiplier, 1.432 * multiplier)})

            ChangeDicts.append({'WORD': 'TOWEIY 5.672E+12 5.445E+12', 'EXCHANGE': 'TOWEIY %.3fE+12 %.3fE+12' % (5.672 * multiplier, 5.445 * multiplier)})
            ChangeDicts.append({'WORD': ' 5.129E+12 4.593E+12', 'EXCHANGE': ' %.3fE+12 %.3fE+12' % (5.129 * multiplier, 4.593 * multiplier)})
            ChangeDicts.append({'WORD': ' 4.31E+12 3.844E+12', 'EXCHANGE': ' %.3fE+12 %.3fE+12'  % ( 4.31 * multiplier, 3.844 * multiplier)})
            ChangeDicts.append({'WORD': ' 3.591E+12 3.188E+12', 'EXCHANGE': ' %.3fE+12 %.3fE+12' % (3.591 * multiplier, 3.188 * multiplier)})
            ChangeDicts.append({'WORD': ' 3.038E+12 2.683E+12', 'EXCHANGE': ' %.3fE+12 %.3fE+12' % (3.038 * multiplier, 2.683 * multiplier)})
            ChangeDicts.append({'WORD': ' 2.485E+12 2.176E+12', 'EXCHANGE': ' %.3fE+12 %.3fE+12' % (2.485 * multiplier, 2.176 * multiplier)})
            ChangeDicts.append({'WORD': ' 2.001E+12 1.754E+12', 'EXCHANGE': ' %.3fE+12 %.3fE+12' % (2.001 * multiplier, 1.754 * multiplier)})
            ChangeDicts.append({'WORD': ' 1.601E+12 1.391E+12', 'EXCHANGE': ' %.3fE+12 %.3fE+12' % (1.601 * multiplier, 1.391 * multiplier)})
            ChangeDicts.append({'WORD': ' 1.257E+12 1.075E+12', 'EXCHANGE': ' %.3fE+12 %.3fE+12' % (1.257 * multiplier, 1.075 * multiplier)})

            ChangeDicts.append({'WORD': 'TOWEIZ 5.672E+12 5.445E+12', 'EXCHANGE': 'TOWEIZ %.3fE+12 %.3fE+12' % (5.672 * multiplier, 5.445 * multiplier)})
            ChangeDicts.append({'WORD': ' 5.129E+12 4.593E+12', 'EXCHANGE': ' %.3fE+12 %.3fE+12' % (5.129 * multiplier, 4.593 * multiplier)})
            ChangeDicts.append({'WORD': ' 4.31E+12 3.844E+12', 'EXCHANGE': ' %.3fE+12 %.3fE+12' % ( 4.31  * multiplier, 3.844 * multiplier)})
            ChangeDicts.append({'WORD': ' 3.591E+12 3.188E+12', 'EXCHANGE': ' %.3fE+12 %.3fE+12' % (3.591 * multiplier, 3.188 * multiplier)})
            ChangeDicts.append({'WORD': ' 3.038E+12 2.683E+12', 'EXCHANGE': ' %.3fE+12 %.3fE+12' % (3.038 * multiplier, 2.683 * multiplier)})
            ChangeDicts.append({'WORD': ' 2.485E+12 2.176E+12', 'EXCHANGE': ' %.3fE+12 %.3fE+12' % (2.485 * multiplier, 2.176 * multiplier)})
            ChangeDicts.append({'WORD': ' 2.001E+12 1.754E+12', 'EXCHANGE': ' %.3fE+12 %.3fE+12' % (2.001 * multiplier, 1.754* multiplier)})
            ChangeDicts.append({'WORD': ' 1.601E+12 1.391E+12', 'EXCHANGE': ' %.3fE+12 %.3fE+12' % (1.601 * multiplier, 1.391 * multiplier)})
            ChangeDicts.append({'WORD': ' 1.257E+12 1.075E+12', 'EXCHANGE': ' %.3fE+12 %.3fE+12' % (1.257 * multiplier, 1.075 * multiplier)})

        else:
            # data has to be copied out of project file...
            ChangeDicts = [{'WORD': '\'Steel\'	 8500	 ', 'EXCHANGE': '\'Steel\'	 8500	 %.1fE+11	 7.93E+10' % (2.1 * multiplier)}]

            ChangeDicts.append({'WORD': 'TOWEAX 1.432E+11 1.508E+11', 'EXCHANGE': 'TOWEAX %.3f' % (1.432 * multiplier) + 'E+11 %.3f' % (1.508 * multiplier) + 'E+11'})
            ChangeDicts.append({'WORD': ' 1.669E+11 1.75E+11', 'EXCHANGE': ' %.3fE+11 %.3fE+11' % ( 1.669 * multiplier, 1.75 * multiplier)})
            ChangeDicts.append({'WORD': ' 1.919E+11 2.007E+11', 'EXCHANGE': ' %.3fE+11 %.3fE+11' % (1.919 * multiplier, 2.007 * multiplier)})
            ChangeDicts.append({'WORD': ' 2.183E+11 2.281E+11', 'EXCHANGE': ' %.3fE+11 %.3fE+11' % (2.183 * multiplier, 2.281 * multiplier)})
            ChangeDicts.append({'WORD': ' 2.465E+11 2.568E+11', 'EXCHANGE': ' %.3fE+11 %.3fE+11' % (2.465 * multiplier, 2.568 * multiplier)})
            ChangeDicts.append({'WORD': ' 2.696E+11 2.804E+11', 'EXCHANGE': ' %.3fE+11 %.3fE+11' % (2.696 * multiplier, 2.804 * multiplier)})
            ChangeDicts.append({'WORD': ' 3.003E+11 3.122E+11', 'EXCHANGE': ' %.3fE+11 %.3fE+11' % (3.003 * multiplier, 3.122 * multiplier)})
            ChangeDicts.append({'WORD': ' 3.329E+11 3.452E+11', 'EXCHANGE': ' %.3fE+11 %.3fE+11' % (3.329 * multiplier, 3.452 * multiplier)})
            ChangeDicts.append({'WORD': ' 3.667E+11 3.718E+11', 'EXCHANGE': ' %.3fE+11 %.3fE+11' % (3.667 * multiplier, 3.718 * multiplier)})
            ChangeDicts.append({'WORD': ' 4.515E+11 4.613E+11', 'EXCHANGE': ' %.3fE+11 %.3fE+11' % (4.515 * multiplier, 4.613 * multiplier)})
            ChangeDicts.append({'WORD': ' 5.574E+11 5.772E+11', 'EXCHANGE': ' %.3fE+11 %.3fE+11' % (5.574 * multiplier, 5.772 * multiplier)})
            ChangeDicts.append({'WORD': ' 6.841E+11 7.07E+11', 'EXCHANGE': ' %.3fE+11 %.3fE+11' % (6.841 * multiplier, 7.07 * multiplier)})
            ChangeDicts.append({'WORD': ' 8.094E+11 8.363E+11', 'EXCHANGE': ' %.3fE+11 %.3fE+11' % (8.094 * multiplier, 8.363 * multiplier)})
            ChangeDicts.append({'WORD': ' 9.5E+11 9.799E+11', 'EXCHANGE': ' %.3fE+11 %.3fE+11' % (9.5 * multiplier, 9.799 * multiplier)})

            ChangeDicts.append({'WORD': 'TOWEIY 1.076E+12 1.256E+12', 'EXCHANGE': 'TOWEIY %.3fE+12 %.3fE+12' % (1.076 * multiplier, 1.256 * multiplier)})
            ChangeDicts.append({'WORD': ' 1.389E+12 1.603E+12', 'EXCHANGE': ' %.3fE+12 %.3fE+12' % (1.389 * multiplier, 1.603 * multiplier)})
            ChangeDicts.append({'WORD': ' 1.756E+12 2.007E+12', 'EXCHANGE': ' %.3fE+12 %.3fE+12' % (1.756 * multiplier, 2.007 * multiplier)})
            ChangeDicts.append({'WORD': ' 2.182E+12 2.489E+12', 'EXCHANGE': ' %.3fE+12 %.3fE+12' % (2.182 * multiplier, 2.489 * multiplier)})
            ChangeDicts.append({'WORD': ' 2.688E+12 3.039E+12', 'EXCHANGE': ' %.3fE+12 %.3fE+12' % (2.688 * multiplier, 3.039 * multiplier)})
            ChangeDicts.append({'WORD': ' 3.189E+12 3.588E+12', 'EXCHANGE': ' %.3fE+12 %.3fE+12' % (3.189 * multiplier, 3.588 * multiplier)})
            ChangeDicts.append({'WORD': ' 3.841E+12 4.314E+12', 'EXCHANGE': ' %.3fE+12 %.3fE+12' % (3.841* multiplier, 4.314 * multiplier)})
            ChangeDicts.append({'WORD': ' 4.598E+12 5.129E+12', 'EXCHANGE': ' %.3fE+12 %.3fE+12' % (4.598 * multiplier, 5.129 * multiplier)})
            ChangeDicts.append({'WORD': ' 5.445E+12 5.673E+12', 'EXCHANGE': ' %.3fE+12 %.3fE+12' % (5.445 * multiplier, 5.673 * multiplier)})
            ChangeDicts.append({'WORD': ' 6.876E+12 7.335E+12', 'EXCHANGE': ' %.3fE+12 %.3fE+12' % (6.876 * multiplier, 7.335 * multiplier)})
            ChangeDicts.append({'WORD': ' 8.842E+12 9.818E+12', 'EXCHANGE': ' %.3fE+12 %.3fE+12' % (8.842 * multiplier, 9.818 * multiplier)})
            ChangeDicts.append({'WORD': ' 1.161E+13 1.281E+13', 'EXCHANGE': ' %.3fE+13 %.3fE+13' % (1.161 * multiplier, 1.281 * multiplier)})
            ChangeDicts.append({'WORD': ' 1.464E+13 1.615E+13', 'EXCHANGE': ' %.3fE+13 %.3fE+13' % (1.464 * multiplier, 1.615 * multiplier)})
            ChangeDicts.append({'WORD': ' 1.83E+13 2.008E+13', 'EXCHANGE': ' %.3fE+13 %.3fE+13' % (1.83 * multiplier, 2.008 * multiplier)})

            ChangeDicts.append({'WORD': 'TOWEIZ 1.076E+12 1.256E+12', 'EXCHANGE': 'TOWEIZ %.3fE+12 %.3fE+12' % (1.076 * multiplier, 1.256 * multiplier)})
            ChangeDicts.append({'WORD': ' 1.389E+12 1.603E+12', 'EXCHANGE': ' %.3fE+12 %.3fE+12' % (1.389 * multiplier, 1.603 * multiplier)})
            ChangeDicts.append({'WORD': ' 1.756E+12 2.007E+12', 'EXCHANGE': ' %.3fE+12 %.3fE+12' % (1.756 * multiplier, 2.007 * multiplier)})
            ChangeDicts.append({'WORD': ' 2.182E+12 2.489E+12', 'EXCHANGE': ' %.3fE+12 %.3fE+12' % (2.182 * multiplier, 2.489 * multiplier)})
            ChangeDicts.append({'WORD': ' 2.688E+12 3.039E+12', 'EXCHANGE': ' %.3fE+12 %.3fE+12' % (2.688 * multiplier, 3.039 * multiplier)})
            ChangeDicts.append({'WORD': ' 3.189E+12 3.588E+12', 'EXCHANGE': ' %.3fE+12 %.3fE+12' % (3.189 * multiplier, 3.588 * multiplier)})
            ChangeDicts.append({'WORD': ' 3.841E+12 4.314E+12', 'EXCHANGE': ' %.3fE+12 %.3fE+12' % (3.841 * multiplier, 4.314 * multiplier)})
            ChangeDicts.append({'WORD': ' 4.598E+12 5.129E+12', 'EXCHANGE': ' %.3fE+12 %.3fE+12' % (4.598 * multiplier, 5.129 * multiplier)})
            ChangeDicts.append({'WORD': ' 5.445E+12 5.673E+12', 'EXCHANGE': ' %.3fE+12 %.3fE+12' % (5.445 * multiplier,  5.673 * multiplier)})
            ChangeDicts.append({'WORD': ' 6.876E+12 7.335E+12', 'EXCHANGE': ' %.3fE+12 %.3fE+12' % (6.876 * multiplier, 7.335 * multiplier)})
            ChangeDicts.append({'WORD': ' 8.842E+12 9.818E+12', 'EXCHANGE': ' %.3fE+12 %.3fE+12' % (8.842 * multiplier, 9.818 * multiplier)})
            ChangeDicts.append({'WORD': ' 1.161E+13 1.281E+13', 'EXCHANGE': ' %.3fE+13 %.3fE+13' % (1.161 * multiplier, 1.281 * multiplier)})
            ChangeDicts.append({'WORD': ' 1.464E+13 1.615E+13', 'EXCHANGE': ' %.3fE+13 %.3fE+13' % (1.464 * multiplier, 1.615 * multiplier)})
            ChangeDicts.append({'WORD': ' 1.83E+13 2.008E+13', 'EXCHANGE': ' %.3fE+13 %.3fE+13' % (1.83 * multiplier, 2.008 * multiplier)})

        return ChangeDicts'''

'''# ----------------------------------------------------------------------------------------------------------------
# Functions mostly used for genetic algorithm optimization
# ----------------------------------------------------------------------------------------------------------------

class GA_utility:
    def calcProbabilities(self, FitnessFunctions):
        # Function should calculate probabilities vom the respective FitnessFunction values.
        # The sum of all probabilities should be 1.
        Probabilities = []
        for value in FitnessFunctions:
            Probabilities.append(value / sum(FitnessFunctions))
        return Probabilities

    def calcProbabilitiesByRank(self, FitnessFunctions):
        # Function should calculate probabilities vom the respective FitnessFunction values.
        # Fitnesses will be ranked and probability distributed for the ranking.
        # The sum of all probabilities should be 1.
        Probabilities = [0 for _ in FitnessFunctions]
        P1 = 0.3
        for cnt, idx in enumerate(np.argsort(FitnessFunctions)):
            Probabilities[idx] = np.power(1 - P1, cnt) * P1
            if cnt == (len(FitnessFunctions-1)):
                Probabilities[idx] = Probabilities[idx] / P1
        return Probabilities

    def calcProbabilityIntervals(self, Probabilities):
        # Function should order the probabilities in an order between 0 and 1.
        ProbabilityIntervalls = []
        Memory = 0
        for Probability in Probabilities:
            ProbabilityIntervalls.append([Memory, Memory + Probability])
            Memory += Probability
        return ProbabilityIntervalls

    def reproduction(self, GA_Strings, ProbabilityIntervals):
        # It mimics the random roulette principal including the respective probabilities.
        # It transfers the mating pool to the reproduction pool
        New_GA_Strings = []
        idx_List = []
        for _ in range(len(GA_Strings)):
            RandomNumber = random.uniform(0, 1)
            for idx, ProbabilityInterval in enumerate(ProbabilityIntervals):
                if ProbabilityInterval[0] <= RandomNumber and RandomNumber <= ProbabilityInterval[1]:
                    New_GA_Strings.append(GA_Strings[idx])
                    idx_List.append(idx)
        if PrintDetails:
            print(idx_List)
        return New_GA_Strings

    def reproductionWithDiversity(self, GA_Strings, ProbabilityIntervals):
        # It mimics the random roulette principal including the respective probabilities.
        # It transfers the mating pool to the reproduction pool
        New_GA_Strings = []
        idx_List = []
        for _ in range(len(GA_Strings)):
            RandomNumber = random.uniform(0, 1)
            for idx, ProbabilityInterval in enumerate(ProbabilityIntervals):
                if ProbabilityInterval[0] <= RandomNumber and RandomNumber <= ProbabilityInterval[1]:
                    New_GA_Strings.append(GA_Strings[idx])
                    idx_List.append(idx)
        if PrintDetails:
            print(idx_List)
        return New_GA_Strings

    def crossover(self, GA_Strings, p_cross, check_p_cross):
        # crossing "genes" if crossing probability (p_cross, default = 0.8) allows for it in random loops
        for idx_string in range(int(len(GA_Strings)/2)):
            if random.uniform(0, 1) <= p_cross:
                RandomPosition = int(random.uniform(1, len(GA_Strings[0]) - 1)) # starting with 1 instead of 0 to force a crossing
                Partner1 = list(GA_Strings[idx_string * 2])
                Partner2 = list(GA_Strings[idx_string * 2 + 1])
                for idx in range(RandomPosition):
                    Memory = copy(Partner1[idx])
                    Partner1[idx] = copy(Partner2[idx])
                    Partner2[idx] = copy(Memory)
                GA_Strings[idx_string * 2] = ''.join(Partner1)
                GA_Strings[idx_string * 2 + 1] = ''.join(Partner2)
                check_p_cross[1] += 1
            check_p_cross[0] += 1
        return GA_Strings, check_p_cross

    def mutation(self, GA_Strings, p_mutate, check_p_mutate):
        # mutate (1=0 or 0=1) every bit in the GA_Strings with the probability of p_mutate (default = 0.05)
        New_GA_Strings = []
        for GA_String in GA_Strings:
            GA_String_List = list(GA_String)
            for idx in range(len(GA_String_List)):
                if random.uniform(0, 1) <= p_mutate:
                    if GA_String_List[idx] == '0':
                        GA_String_List[idx] = '1'
                    elif GA_String_List[idx] == '1':
                        GA_String_List[idx] = '0'
                    else:
                        print('Something is rotten in the state of denmark')
                    check_p_mutate[1] += 1
                check_p_mutate[0] += 1
            New_GA_Strings.append(''.join(GA_String_List))
        return New_GA_Strings, check_p_mutate

    def bitStringToDezimal(self, GA_Strings, SolutionIntervals):
        # turns string of bits into parameters inside the defined intervals
        nParams = len(SolutionIntervals)
        Params = [[0 for i in range(nParams)] for ii in range(len(GA_Strings))]
        for idx, GA_String in enumerate(GA_Strings):
            nBits = int(len(GA_String) / nParams)
            for idx_Params in range(nParams):
                BitParam = int(GA_String[idx_Params * nBits: (idx_Params + 1) * nBits], 2)  # 2 for binary
                if PrintDetails:
                    print('BitParam: ', BitParam, 'Bit-String:', GA_String[idx_Params * nBits: (idx_Params + 1) * nBits], GA_String)
                Params[idx][idx_Params] = SolutionIntervals[idx_Params][0] + (SolutionIntervals[idx_Params][1]
                             - SolutionIntervals[idx_Params][0]) / (pow(2, nBits) - 1) * BitParam
        return Params

    def findeUnchangedRuns(self, GA_Strings, New_GA_Strings):  # , ListOfBladedJobs):
        # If job parameters haven't been altered than it is unnecessarily time consuming to run those jobs again
        OldIdxOfUnchangedBladedJobs = []
        NewIdxOfUnchangedBladedJobs = []
        for old_idx, GA_String in enumerate(GA_Strings):
            for new_idx, New_GA_String in enumerate(New_GA_Strings):
                if GA_String == New_GA_String:
                    if new_idx not in NewIdxOfUnchangedBladedJobs:
                        OldIdxOfUnchangedBladedJobs.append(old_idx)
                        NewIdxOfUnchangedBladedJobs.append(new_idx)
                    else:
                        if PrintDetails:
                            print('WARNING! CROSSING DUPLICATE! WILL JUMP HERE! (GA_utility().findeUnchangedRuns())')
        return OldIdxOfUnchangedBladedJobs, NewIdxOfUnchangedBladedJobs'''




