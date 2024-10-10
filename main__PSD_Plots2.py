############################################ DESCRIPTION ###############################################################
# This script should handle time series from bladed and plot those e.g. as power spectral density or as fatigue damage #
# over the frequency (see: "fatigue damage spectrum" OR fatigue damage equivalent PSD) for a better fatigue evaluation.#
# -- Code by Fabian Anstock HAW Hamburg                                                                                #
########################################################################################################################

import csv
import glob
import ANSFAB__DEL_BladeTowerHubMy_max_sector
from ANSFAB__Utility import Utility
import matplotlib.pyplot as plt
import numpy as np
import scipy.signal
from fatiguepy import *
#from pyyeti import psd, fdepsd
import math
import rainflow
import copy
import os

folder_n_file_s = []
# folder_n_file_s.append(r'C:\xBladed\FOWTs\DLC12_full_2B_0yaw_v3\2BVolt20_v3_noDamp_00y_11mps_s11')
# folder_n_file_s.append(r'C:\xBladed\FOWTs\DLC12_full_2B_0yaw_v3__calm_sea\2BVolt20_v3_calmSea_00y_11mps_s11')
# folder_n_file_s.append(r'C:\xBladed\FOWTs\DLC12_full_3B_volturn05_tow044Hz_0yaw\3B20Volt05_tower044Hz_00y_11mps_s11')
# folder_n_file_s.append(r'C:\xBladed\FOWTs\DLC12_full_3B_0yaw_orgTower\3BVolt20_v4_noDamp_orgTower_00y_11mps_s11')
# folder_n_file_s.append(r'C:\xBladed\FOWTs\DLC12_full_3B_0yaw\3BVolt20_v4_noDamp_00y_11mps_s11')


folder_n_file_s.append(r'C:\xBladed\FOWTs\DLC12_full_2B_0yaw_v6_03\2B20Volt_v06_03_simple_PI_00y_11mps_s11')
# folder_n_file_s.append(r'C:\xBladed\FOWTs\DLC12_full_2B_0yaw_v6_03_calm_sea\2B20Volt_v06_03_calmSea_simple_PI_00y_11mps_s11')
# folder_n_file_s.append(r'C:\xBladed\FOWTs\DLC12_full_2B_volturn8_new_tower0435Hz_0yaw\2B20Volt_v08_stiff_tower0_435Hz_00y_11mps_s11')
folder_n_file_s.append(r'C:\xBladed\FOWTs\DLC12_full_3B_volturn06_03_originalTower_0yaw\3B20Volt06_03_originalTower_00y_11mps_s11')
folder_n_file_s.append(r'C:\xBladed\FOWTs\DLC12_full_3B_volturn08_tower0435Hz_0yaw\3B20Volt08_0435Hztower_00y_11mps_s11')
folder_n_file_s.append(r'C:\xBladed\FOWTs\DLC12_full_3B_volturn06_03_orgTowerFake0435Hz_0yaw\3B20Volt06_orgTower0435HzFake_00y_11mps_s11')
folder_n_file_s.append(r'C:\xBladed\FOWTs\DLC12_full_2B_0yaw_v6_03_teeter\2B20Volt06_03_teeter_simple_PI_00y_11mps_s11')

folder_n_file_s.append(r'C:\xBladed\FOWTs\DLC12_full_2B_0yaw_v9\2B20Volt_v09_simple_PI_00y_11mps_s11')
folder_n_file_s.append(r'C:\xBladed\FOWTs\DLC12_full_2B_0yaw_v6_03__post_fatigue_blade_v17\2B20Volt_v06_03_s_PI_fatgiue_blade_v17_00y_11mps_s11')

folder_n_file_s = []
folder_n_file_s.append(r'H:\BladedWS\FOWTs\Best_of_BruteForce_full_time_series\2B20Volt_v009_1_15mps_full_TS')
folder_n_file_s.append(r'H:\BladedWS\FOWTs\Best_of_BruteForce_full_time_series\2b20volt_v009_1_15mps_g0_FA_damper_full_TS')
folder_n_file_s.append(r'H:\BladedWS\FOWTs\Best_of_BruteForce_full_time_series\2b20volt_v009_1_15mps_g0_ppitch_damper_full_TS')
folder_n_file_s.append(r'H:\BladedWS\FOWTs\Best_of_BruteForce_full_time_series\2b20volt_v009_1_15mps_g0__g1_ppitch_n_surge_damper_full_TS')
#folder_n_file_s.append(r'H:\BladedWS\FOWTs\Best_of_BruteForce_full_time_series\3B20Volt_v008_15mps_full_TS')
#folder_n_file_s.append(r'H:\BladedWS\FOWTs\Best_of_BruteForce_full_time_series\3B20Volt_v008_15mps_opt1_FA_damper_full_TS')
#folder_n_file_s.append(r'H:\BladedWS\FOWTs\Best_of_BruteForce_full_time_series\3b20volt_v008_15mps_g0_ppitch_damper_full_TS')
#folder_n_file_s.append(r'H:\BladedWS\FOWTs\Best_of_BruteForce_full_time_series\3b20volt_v008_15mps_g0__g0_ppitch_n_surge_damper_full_TS')



# outdated:
# folder_n_file_s.append(r'C:\xBladed\FOWTs\DLC12_full_3B_volturn07_03_new_tower0435Hz_0yaw\3B20Volt07_new0435Hztower_00y_11mps_s11')
# folder_n_file_s.append(r'C:\xBladed\FOWTs\DLC12_full_3B_volturn07_03_tow044Hz_0yaw\3B20Volt07_03_tower044Hz_00y_11mps_s11')
# folder_n_file_s.append(r'C:\xBladed\FOWTs\DLC12_full_2B_volturn7_03__tower044Hz_0yaw\2B20Volt_v07_03_tower0_44Hz_00y_11mps_s11')

mps = 11  # simulation mean wind speed in m/s (usually in 2 m/s bins)
for idx, path in enumerate(folder_n_file_s):
    folder_n_file_s[idx] = path.replace('11mps_s11', str(mps) + 'mps_s' + str(mps))

DEL_dict = {}
DEL_dict['VARIAB'] = 'Tower Mz'
# DEL_dict['VARIAB'] = 'Pitch Excitation Force'
# DEL_dict['VARIAB'] = 'Time from start of simulation'
# DEL_dict['VARIAB'] = 'Time from start of simulation'
# DEL_dict['VARIAB'] = 'Input water surface deviation from calm'
#DEL_dict['VARIAB'] = 'Nacelle side-side acceleration'

#folder_n_file_s = []
#folder_n_file_s.append(r'C:\xBladed\FOWTs\tower_hz_test_runs\3B20Volt07__tower5_fineTuning_v06_DLC61')
#folder_n_file_s.append(r'C:\xBladed\FOWTs\tower_hz_test_runs\3B20Volt06__originalTower_fake0435Hz_v04_DLC61')
#folder_n_file_s.append(r'C:\xBladed\FOWTs\tower_hz_test_runs\2B20Volt06__originalTower_ref_DLC61')
#DEL_dict['VARIAB'] = 'Nacelle fore-aft acceleration'

PlotControl = 3

nbins = 180

if PlotControl < 3:
    folder_n_file_s = [folder_n_file_s[0]]
    nbins = int(nbins/10)


# might work to leave this unchanged for other variables, because it might only be needed for the tower nodes anyhow
DEL_dict['POSOFNODE'] = 3  # some variables are loads have members and two notes each; all nodes of a single time step
# are staggered in one column, thus: pos 1 is first node of first member; 2 is second node of member 1; 3 is first node of member 2 ..

# DEL_dict['GENLAB'] = 'Tower member loads - local coordinates' # not needed any more

PrintDetails = True

fig, ax = plt.subplots()
collect_DEL_spectra = []
collect_accumulated_DEL_spectra = []
collect_run_names = []
count_spectra = 0

# loop it all:
for run_idx, folder_n_file in enumerate(folder_n_file_s):
    run_name = folder_n_file.split('\\')[-1]
    # search through files to catch right time series (make this a function later on!)
    InfoFiles = glob.glob(folder_n_file + '.%*')
    if PrintDetails:
        print('Found: ', InfoFiles)

    foundIt = False
    counter = 0
    for InfoFile in InfoFiles:
        csv_data = csv.reader(open(InfoFile), delimiter='\t')
        for row in csv_data:
            if row[0] == 'DIMENS':  # dimensions need to be stored before, because it is marked in the lines above VARIAB
                DIMENS = row[1:]
            if row[0] == 'VARIAB':   # old alternative: if row[0].find('VARIAB') != -1:
                for idx, Parameter in enumerate(row[1].split('\' ')):
                    if Parameter.replace('\'','') == DEL_dict.get('VARIAB'):
                        DEL_dict['VARIAB_IDX'] = idx
                        DEL_dict['DIMENS'] = DIMENS
                        fileEnd = '.$' + InfoFile.split('.%')[-1]
                        DEL_dict['fileEnd'] = fileEnd
                        if PrintDetails:
                            print('found (', Parameter.replace('\'',''), ') at index ', idx, ' in file with ending: ', fileEnd, ' and dimensions: ', DIMENS)
                        counter += 1
                        #foundIt = True
            #if foundIt:
            #    break
    if counter > 1:
        print('WARNING: There might be a false friend in the data. There is more then one variable with the same name!!!')

    # get time data
    [time_total, deltat] = Utility().calcTotalTimeAndDeltat(os.path.split(folder_n_file)[0],folder_n_file.split('\\')[-1])

    # search through the desired time series
    filePath = folder_n_file + DEL_dict.get('fileEnd')
    try:
        csv_data = csv.reader(open(filePath), delimiter=' ')
    except OSError:
        print('cannot find ', filePath, '. Will skip and set value to 0.')
        continue
    TimeSeries = []  # blade root my moment

    if len(DEL_dict.get('DIMENS')) == 3:  # otherwise the third dimension is missing in the 2D csv data file
        dimenTwo = float(DEL_dict.get('DIMENS')[1])
        pos_of_note = DEL_dict.get('POSOFNODE')  # some members have two notes; all notes of a single time step are
    else:
        dimenTwo = 1
        if DEL_dict.get('POSOFNODE') > 1:
            print('ERROR OCCURRED IN DESIRED POSITION OF NODES!!! Will set node position to 1')
        pos_of_note = 1

    # nmbr_loads_per_note = 6
    # staggered in one column, thus: pos 1 is first node of first member; 2 is second node of member 1; 3 is first node of member 2 ..
    line_count = 0
    load_count = 0
    # nheader = 0
    for row in csv_data:
        if load_count < int(time_total / deltat) + 1:  # nheader:
            if line_count == load_count * dimenTwo + pos_of_note - 1:
                row = list(filter(None, row))
                # time[line_count-nheader] = row[0]
                TimeSeries.append(float(row[DEL_dict['VARIAB_IDX']]))
                load_count = load_count + 1
        # else: print('overshooting lines')
        line_count = line_count + 1

    #### copied from other script ####
    Referenz_Frequency = 1  # Hz
    Nreff = time_total * Referenz_Frequency
    var_nbins = 100
    def calcDELfromTimeSeries(timeSeries, k):
        DEL = 0.0
    #    if timeSeries:  # just to be sure that its not emtpy
        RFC = copy.copy(rainflow.count_cycles(timeSeries, nbins=var_nbins))
        for bin in range(var_nbins):
            DEL += copy.copy(RFC[bin][1] * (math.pow(RFC[bin][0], k)))
        DEL = copy.copy(math.pow(DEL / Nreff, 1/k))
        return DEL
    #### copied from other script ####

    if False:
        ax.plot(np.arange(0, time_total+deltat, deltat), TimeSeries, label=DEL_dict.get('VARIAB'))
        ax.set(xlabel='time in t')  # y can be automized later on, ylabel='dimensions in m')
    elif False:
        fs = 1/deltat  # time step or: sampling frequency
        # f contains the frequency components
        # S is the PSD
        # (f, S) = scipy.signal.periodogram(TimeSeries, fs, scaling='density')
        (f, S) = scipy.signal.welch(TimeSeries, fs, nperseg=1 * 1024) # 4 * 1024)
        ax.plot(f[1:], S[1:], label=folder_n_file.split('\\')[-1] + DEL_dict.get('VARIAB')+ ' density')
        (f, S) = scipy.signal.welch(TimeSeries, fs, scaling='spectrum', nperseg=2 * 1024)
        #ax.plot(f[1:], S[1:], label=folder_n_file.split('\\')[-1] + DEL_dict.get('VARIAB') + ' spectrum')

        S_nonDensity = []
        S_accumulate = []
        sum_S = 0
        for idx, value in enumerate(S):
            S_nonDensity.append(value * f[idx])
            sum_S += value * f[idx]
            S_accumulate.append(sum_S)
        # ax.plot(f[1:], S_nonDensity[1:], label=DEL_dict.get('VARIAB') + ' without density')
        # ax.plot(f[1:], S_accumulate[1:], label=folder_n_file.split('\\')[-1] + DEL_dict.get('VARIAB') + ' accumulated')
        ax.set(xlabel='frequency in Hz',  ylabel='density')
        plt.yscale('log')
    elif False:
        (f, Gyy) = scipy.signal.welch(TimeSeries, fs=1/deltat, nperseg=4 * 1024)
        ax.plot(f[1:], Gyy[1:], label=DEL_dict.get('VARIAB'))

        # moments = prob_moment.Probability_Moment(Gyy, f)
        # m4 = moments.momentn(4)
        # ax.plot(moments.f, moments.Y, label=DEL_dict.get('VARIAB')+' moments')
        m4_comp = ANSFAB__DEL_BladeTowerHubMy_max_sector.calcDELfromTimeSeries(TimeSeries, 4)

        # Steel SAE 1015
        b = -0.138
        sigmaf = 1020
        A = (2 ** b) * sigmaf
        k = -1 / b
        C = A ** k


        si = 0.0
        sf = abs(max(TimeSeries) - min(TimeSeries))
        ds = sf / 128
        s = np.arange(si, sf, ds)
        #TB = Tovo_Benasciutti.TB(4, C, Gyy, f, xf, s)
        TB = Dirlik.DK(4, C, Gyy, f, time_total, s)
        pTB = TB.PDF()
        ax.plot(TB.f, TB.PDF(), label=DEL_dict.get('VARIAB') + ' TB PDF')
        ax.plot(TB.f, TB.counting_cycles(), label=DEL_dict.get('VARIAB') + ' TB cycles')
        #ax.plot(TB.f, TB.pNB, label=DEL_dict.get('VARIAB') + ' TB pNB')
        ax.plot(TB.f, TB.s, label=DEL_dict.get('VARIAB') + ' TB s')
        ax.plot(TB.f, TB.loading_spectrum(), label=DEL_dict.get('VARIAB') + ' TB loading spectrum')
        plt.yscale('log')
    else:
        # PlotControl = 3



        # split time series in frequency bins by bandpass filters
        # nbins = 200
        FilterOrderN = 20
        fs = 1 / deltat
        Wn = [0.1, 0.2]  # * 2 * np.pi
        max_frequency = 1  # fs/2-eps
        frequency_delta = max_frequency/nbins

        frequency_bin_timeSeries = []
        lower_value = 0
        for i in range(nbins):
            Wn = [lower_value, lower_value+frequency_delta]
            lower_value += frequency_delta
            if i == 0:  # low frequencies are low pass filtered
                sos = scipy.signal.butter(FilterOrderN, Wn[1], fs=fs, btype='lp', output='sos')  # butterworth filter
            elif i == nbins-1:  # high frequencies are high pass filtered
                sos = scipy.signal.butter(FilterOrderN, Wn[0], fs=fs, btype='hp', output='sos')
            else:  # middle frequencies are band pass filtered
                sos = scipy.signal.butter(FilterOrderN, Wn, fs=fs, btype='bandpass', output='sos')
            frequency_bin_timeSeries.append(scipy.signal.sosfilt(sos, TimeSeries))

            if PlotControl == 1:  # plotting time series
                ax.set(xlabel='time in s', ylabel=DEL_dict.get('VARIAB'))
                ax.plot(np.arange(0, time_total + deltat, deltat), frequency_bin_timeSeries[i][:], label=DEL_dict.get('VARIAB') + ' filtered bin ' + str(i))
            elif PlotControl == 2:  # plotting power spectral densities
                ax.set(xlabel='frequency in Hz', ylabel='density ' + DEL_dict.get('VARIAB'))
                (f, Gyy) = scipy.signal.welch(frequency_bin_timeSeries[i][:], fs=1 / deltat, nperseg=4 * 1024)
                ax.plot(f[1:], Gyy[1:], label=DEL_dict.get('VARIAB') + ' filtered bin ' + str(i))

        # summing all bin time series back to one, for validation and DEL accumulation over frequencies
        k = 4  # SN-Curve exponent (for steel)
        accumulated_DEL = []
        for i in range(nbins):
            if i == 0:  # scip first round
                summed_TimeSeries = copy.copy(frequency_bin_timeSeries[0][:])
                #summed_TimeSeries = copy.copy(frequency_bin_timeSeries[-1][:])
            else:
                for n in range(len(TimeSeries)):
                    summed_TimeSeries[n] += frequency_bin_timeSeries[i][n]
                    #summed_TimeSeries[n] += frequency_bin_timeSeries[nbins-1-i][n] # other direction adding
            accumulated_DEL.append(calcDELfromTimeSeries(summed_TimeSeries, k))

        # ALTERNATIVE:
        # split time series in frequency steps ONLY BY LOW-PASS FILTERING (It does accumulate the damage directly):
        summed_bin_TimeSeries = []
        summed_bin_TimeSeries2 = []
        accumulated_DEL3 = []
        accumulated_DEL_reversed = []
        for i in range(nbins):
            sos = scipy.signal.butter(FilterOrderN, frequency_delta*(i+1), fs=fs, btype='lp', output='sos')  # low pass
            sos2 = scipy.signal.butter(FilterOrderN, frequency_delta*(nbins-i), fs=fs, btype='hp', output='sos')  # low pass
            if i < nbins - 1:  # low frequencies are low pass filtered
                summed_bin_TimeSeries.append(scipy.signal.sosfilt(sos, TimeSeries))
                summed_bin_TimeSeries2.append(scipy.signal.sosfilt(sos2, TimeSeries))
            else:  # last part is unfiltered
                summed_bin_TimeSeries.append(TimeSeries)
                summed_bin_TimeSeries2.append(TimeSeries)
            accumulated_DEL3.append(calcDELfromTimeSeries(summed_bin_TimeSeries[-1][:], k))
            accumulated_DEL_reversed.append(calcDELfromTimeSeries(summed_bin_TimeSeries2[-1][:], k))

            if PlotControl == 1:  # plotting time series
                ax.set(xlabel='time in s', ylabel=DEL_dict.get('VARIAB'))
                ax.plot(np.arange(0, time_total + deltat, deltat), summed_bin_TimeSeries[i][:], label=DEL_dict.get('VARIAB') + ' filtered bin v2' + str(i))
            elif PlotControl == 2:  # plotting power spectral densities
                ax.set(xlabel='frequency in Hz', ylabel='density ' + DEL_dict.get('VARIAB'))
                (f, Gyy) = scipy.signal.welch(summed_bin_TimeSeries[i][:], fs=1 / deltat, nperseg=4 * 1024)
                (f, Gyy) = scipy.signal.welch(summed_bin_TimeSeries2[i][:], fs=1 / deltat, nperseg=4 * 1024)
                ax.plot(f[1:], Gyy[1:], label=DEL_dict.get('VARIAB') + ' filtered bin v2' + str(i))

        # calculation DELs from high to low frequencies
        accumulated_DEL4 = []
        accumulated_DEL_reversed.reverse()
        for i in range(nbins):
            if i == 0:
                accumulated_DEL4.append(accumulated_DEL_reversed[i]-accumulated_DEL_reversed[i+1])
            elif i == nbins-1:
                accumulated_DEL4.append(accumulated_DEL_reversed[0])
            else:
                accumulated_DEL4.append(accumulated_DEL_reversed[i]-accumulated_DEL_reversed[i+1]+accumulated_DEL4[-1])

        if PlotControl == 1:
            ax.plot(np.arange(0, time_total + deltat, deltat), summed_TimeSeries, label=DEL_dict.get('VARIAB') + ' filtered summed')
            ax.plot(np.arange(0, time_total + deltat, deltat), TimeSeries, 'r', label=DEL_dict.get('VARIAB'))
        elif PlotControl == 2:
            (f, Gyy) = scipy.signal.welch(summed_TimeSeries, fs=1 / deltat, nperseg=4 * 1024)
            ax.plot(f[1:], Gyy[1:], label=DEL_dict.get('VARIAB') + ' filtered summed')

            (f, Gyy) = scipy.signal.welch(TimeSeries, fs=1/deltat, nperseg=4 * 1024)
            ax.plot(f[1:], Gyy[1:], 'r+', label=DEL_dict.get('VARIAB'))
            plt.yscale('log')

        # calc DELs for each frequency
        frequency_bin_DELs = []
        accumulated_DEL2 = []
        summed_post_DEL = 0
        summed_post_DEL2 = 0
        for i in range(nbins):
            temp_DEL = calcDELfromTimeSeries(frequency_bin_timeSeries[i][:], k)
            frequency_bin_DELs.append(copy.copy(temp_DEL))
            summed_post_DEL += pow(temp_DEL, k)
            summed_post_DEL2 += temp_DEL
            accumulated_DEL2.append(sum(frequency_bin_DELs))  # "fair" weighted DEL accumulation
        summed_post_DEL = pow(summed_post_DEL, 1/k)

        ref_DEL = calcDELfromTimeSeries(TimeSeries, k)
        summed_pre_DEL = calcDELfromTimeSeries(summed_TimeSeries, k)
        print('ref DEL is: ', ref_DEL, ' summed DEL after bin over frequecies is: ', summed_post_DEL, summed_post_DEL2,
              ' summed before DEL calc ', summed_pre_DEL)

        useSmartAccumulation = True
        if useSmartAccumulation:  # then useSmartAccumulation (fake the height of the DEL curve and filter bumps)
            for i, DEL in enumerate(accumulated_DEL):
                #accumulated_DEL[i] = accumulated_DEL[i] * ref_DEL/accumulated_DEL[-1]  # scale to fit true DEL
                if i > 0:
                    accumulated_DEL[i] = max(accumulated_DEL[i], accumulated_DEL[i-1])  # avoid wrong bumps
                if 0 < i < len(accumulated_DEL3)-2:
                    if accumulated_DEL3[i] < accumulated_DEL3[i-1]:   # for linear interpolation
                        if accumulated_DEL3[i+1] < accumulated_DEL3[i-1]:
                            accumulated_DEL3[i] = (accumulated_DEL3[i-1] + max(accumulated_DEL3[i-1],
                                                                           accumulated_DEL3[i+2])) / 2
                        else:
                            accumulated_DEL3[i] = (accumulated_DEL3[i-1] + accumulated_DEL3[i+2]) / 2

        if PlotControl == 3:
            ax.set(xlabel='frequency in Hz', ylabel='accumulated damage ' + DEL_dict.get('VARIAB'))
            colors = [['r-.', 'r--', 'r-'], ['g-.', 'g--', 'g-'], ['m-.', 'm--', 'm-'], ['c-.', 'c--', 'c-'], ['b-.', 'b--', 'b-'], ['k-.', 'k--', 'k-'], ['y-.', 'y--', 'y-'], ['r-.', 'r-', 'r--'], ['g-.', 'g-', 'g--'], ['m-.', 'm-', 'm--'], ['c-.', 'c-', 'c--'], ['b-.', 'b-', 'b--'], ['k-.', 'k-', 'k--'], ['y-.', 'y-', 'y--']]
            #ax.plot([0, max_frequency], [ref_DEL, ref_DEL], colors[run_idx][0], label=folder_n_file.split('\\')[-1] + ' ' + DEL_dict.get('VARIAB') + ' ref total DEL')

            ax.plot(np.arange(0, max_frequency, frequency_delta), frequency_bin_DELs, colors[run_idx][1],  label=run_name + ' ' + DEL_dict.get('VARIAB'))# + ' DEL per bin')
            #ax.plot(np.arange(0, max_frequency, frequency_delta), accumulated_DEL, colors[run_idx][2], label=run_name + ' '  + DEL_dict.get('VARIAB') + ' DEL accumulated')
            ax.plot(np.arange(0, max_frequency, frequency_delta), accumulated_DEL3, colors[run_idx][2])#, label=run_name + ' '  + DEL_dict.get('VARIAB') + ' DEL accumulated v3')
            #ax.plot(np.arange(0, max_frequency, frequency_delta), accumulated_DEL4, colors[run_idx][0], label=run_name + ' '  + DEL_dict.get('VARIAB') + ' DEL accumulated v4')
            # ax.plot(np.arange(0, max_frequency, frequency_delta), accumulated_DEL2, colors[run_idx][0], label=DEL_dict.get('VARIAB') + ' DEL "fair" accumulated')

        collect_DEL_spectra.append(frequency_bin_DELs)
        collect_accumulated_DEL_spectra.append(accumulated_DEL3)
        collect_run_names.append(run_name)
        count_spectra += 1


# store results in tab stop file for latex
outputpath = '\\'.join(folder_n_file.split('\\')[:-2]) + r'\2B_vs_3B_Volturn20MW_DEL_over_Hz_Latex_output.txt'
print('writing output to: ', outputpath)
try:
    outfile = open(outputpath, 'w')
    firstline = 'Hz'
    for idx, run_name in enumerate(collect_run_names):
        firstline = firstline + '\t' + 'y_' + run_name + '\t' + 'y_accu_' + run_name
        #firstline = firstline + '\t' + 'y_' + str(idx+1) + '\t' + 'y_accu_' + str(idx+1)
    print(firstline)
    outfile.write(firstline)
    for row_idx, Hz in enumerate(np.arange(0, max_frequency, frequency_delta)):
        row_string = '\n%.3f' %Hz
        for spectrum_idx in range(count_spectra):
            row_string += '\t%.3f' %collect_DEL_spectra[spectrum_idx][row_idx]
            row_string += '\t%.3f' %collect_accumulated_DEL_spectra[spectrum_idx][row_idx]
        outfile.write(row_string)
    outfile.close()



    #with open(outputpath, 'w', newline='') as output_file:
    #    dict_writer = csv.DictWriter(output_file, ListDict[0].keys())
    #    dict_writer.writeheader()
    #    dict_writer.writerows(ListDict)
except:
    print('something is rotten in the state of denmark')


ax.grid()
ax.legend(loc='lower right')
plt.show()
