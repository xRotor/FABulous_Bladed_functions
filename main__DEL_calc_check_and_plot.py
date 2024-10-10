from ANSFAB__Utility import Utility
import math
import rainflow
from collections import deque, defaultdict
from copy import copy
import rainflow_jenni_rinker as rainflow_rinker
import numpy as np


EvaluationKeys = 'Tower My'
EvaluationKeys = 'Stationary hub Fz'
#EvaluationKeys = 'Blade 1 Mx (Root axes)'
#EvaluationKeys = 'Blade 1 My (Root axes)'

RunFolder = r'H:\BladedWS\BottomFixed\DLC_legacy\temptemptemp_test_shorterNames_test'
#BladedJobs = [r'2b101v15_ref_ex5_lookuptabledamp_dlc12_kaimal.prj', r'2b101v15_ref_ex5_lookuptabledamp_dlc12_kai.prj']
BladedJobs = [r'2b101v15_ref_ex5_lookuptabledamp_dlc12_kai.prj', r'2b101v15_ref_ex5_lookuptabledamp_dlc12_kaimal.prj']

colors = ['b', 'r', 'y']
markers = ['x', '', 'o']
ax = []
time_series_list = []
DEL_v1 = []
DEL_v2 = []
DEL_v3 = []
for ii, BladedJob in enumerate(BladedJobs):
    [fileEnd, idx, DIMENS] = Utility().collectTimeSeriesStructureFromBladedFiles(RunFolder, BladedJob, EvaluationKeys)
    [time_total, deltat] = Utility().calcTotalTimeAndDeltat(RunFolder, BladedJob)
    time_series = Utility().readTimeSeriesData(RunFolder, BladedJob, fileEnd, idx, DIMENS, pos_of_node=1)#[1:]
    [plt, ax] = Utility().easyPlotGraph(time_series, color=colors[ii], marker='', show=False, new_y_axis=False, ax=ax, y_label='load')

    DEL = desired_value = Utility().calcDELfromTimeSeries_old_legacy(time_series, k=10)

    DEL = 0.0
    nbins = 100
    Nreff = -1e20
    Referenz_Frequency = 1.0
    Nreff = time_total * Referenz_Frequency
    k = 4
    DELs = []
    if time_series:  # just to be sure that its not emtpy
        RFC = copy(rainflow.count_cycles(time_series, nbins=nbins))
        for bin in range(nbins):
            DEL += copy(RFC[bin][1] * (math.pow(RFC[bin][0], k)))
            DELs.append(DEL)
        DEL = copy(math.pow(DEL / Nreff, 1 / k))

    print('DEL is:', DEL)
    DEL_v1.append(DEL)
    #[plt, ax] = Utility().easyPlotGraph(DELs, color=colors[ii], marker=markers[ii], show=False, new_y_axis=False, ax=ax, y_label='DELs')



    # ----------- replicate old ---------------- #
    counts_dict = defaultdict(float)
    from rainflow import extract_cycles
    cycles = (
        (rng, count)
        for rng, mean, count, i_start, i_end in extract_cycles(time_series)
    )

    binsize = (max(time_series) - min(time_series)) / nbins
    nmax = 0
    for rng, count in cycles:
        n = int(math.ceil(rng / binsize))  # using int for Python 2 compatibility
        counts_dict[n * binsize] += count
        nmax = max(n, nmax)
    for i in range(1, nmax):
        counts_dict.setdefault(i * binsize, 0.0)
    RFC = sorted(counts_dict.items())

    ranges = [RFC[bin][0] for bin in range(nbins)]
    counts = [RFC[bin][1] for bin in range(nbins)]
    #[plt, ax] = Utility().easyPlotGraph(counts, x_axis=ranges, color=colors[ii], marker=markers[ii], show=False,new_y_axis=False, ax=ax, y_label='counts')

    # ------------- new approach --------------- #
    TS_turning_points = [time_series[0]]
    visualize = [0]
    for idx, load in enumerate(time_series[1:-1]):  # the first idx is 0 but should refer to the second value's index
        if np.sign(time_series[idx + 1] - time_series[idx]) != np.sign(time_series[idx + 2] - time_series[idx + 1]):
            if load != TS_turning_points[-1]:  # typically important for repetitive zeros
                if len(TS_turning_points) > 2 and np.sign(TS_turning_points[-1] - TS_turning_points[-2]) == np.sign(load - TS_turning_points[-1]):  # needed for numerical issues when there is no actual turning point
                    TS_turning_points.pop()
                    visualize.pop()
                TS_turning_points.append(load)
                visualize.append(idx + 1)
    #TS_turning_points = [time_series[0]] + [load for idx, load in enumerate(time_series[1:-1]) if np.sign(time_series[idx+1]-time_series[idx]) != np.sign(time_series[idx+2]-time_series[idx+1])]

    [plt, ax] = Utility().easyPlotGraph(TS_turning_points, color=colors[ii], marker=markers[ii], show=False, new_y_axis=False, ax=ax, y_label='load')
    print('turning point 1535 is at', visualize[1535])

    array_out = rainflow_rinker.rainflow(np.array(TS_turning_points))

    # sort array_out by cycle range
    #array_out = array_out[:, array_out[0, :].argsort()]  # 0: 'Range', 3: 'Count', 1: 'Mean', 2: 'GAR', 4: 'GAR-ZFLM'
    ranges = list(array_out[0])
    #ranges = [rng*2 for rng in ranges]
    counts = list(array_out[3])


    DEL_non_binned = 0.0
    for cycle in range(len(ranges)):
        DEL_non_binned += copy(counts[cycle] * (math.pow(ranges[cycle], k)))
    DEL_non_binned = copy(math.pow(DEL_non_binned / Nreff, 1 / k))
    #[plt, ax2] = Utility().easyPlotGraph(counter, x_axis=ranges, color=colors[ii+1], marker=markers[ii], show=True, new_y_axis=False, ax=ax2, y_label='counts')

    binsize = (max(time_series) - min(time_series)) / nbins
    nmax = 0
    counts_dict = defaultdict(float)
    for i, count in enumerate(counts):
        rng = ranges[i]
        n = int(math.ceil(rng / binsize))  # using int for Python 2 compatibility
        counts_dict[n * binsize] += count
        nmax = max(n, nmax)
    for i in range(1, nmax):
        counts_dict.setdefault(i * binsize, 0.0)
    RFC = sorted(counts_dict.items())

    ranges = [RFC[bin][0] for bin in range(nmax)]
    counts = [RFC[bin][1] for bin in range(nmax)]

    #[plt, ax] = Utility().easyPlotGraph(counts, x_axis=ranges, color=colors[ii+1], marker=markers[ii], show=True, new_y_axis=False, ax=ax, y_label='counts')

    DELs_v2 = []
    DEL = 0.0
    for bin in range(nmax):
        DEL += copy(counts[bin] * (math.pow(ranges[bin], k)))
        DELs_v2.append(DEL)
    DEL = copy(math.pow(DEL / Nreff, 1 / k))

    #[plt, ax] = Utility().easyPlotGraph(DELs_v2, color=colors[ii+1], marker=markers[ii], show=True, new_y_axis=False, ax=ax, y_label='DELs')


    print('DEL is:', DEL, 'Rinkers rainflow')
    print('DEL is:', DEL_non_binned, 'for non binned cyles of Rinkers rainflow')
    DEL_v2.append(DEL)
    DEL_v3.append(DEL_non_binned)
    # # print cycle range, cycle count, cycle mean, goodman-adjusted range (GAR), and
    # #   goodman-adjusted range with zero fixed-load mean (GAR-ZFLM)
    # print('\nCalculated cycle count:')
    # print('\n{:>7s}{:>8s}{:>8s}{:>8s}{:>12s}'.format('Range', 'Count',
    #                                                  'Mean', 'GAR', 'GAR-ZFLM'))
    # print('----------------------------------------------')
    # for ii in range(len(array_out.T)):
    #     print('{:7.1f}{:8.1f}{:8.1f}{:8.1f}{:12.1f}'.format(*array_out[[0, 3, 1, 2, 4], ii]))




    time_series_list.append(time_series)

# largest_error_size = 0
# step_of_largest_error = 0
# for i, step_value in enumerate(time_series_list[0]):
#     if largest_error_size < abs(step_value - time_series[i]):
#         largest_error_size = abs(step_value - time_series[i])
#         step_of_largest_error = i
# print('found ', largest_error_size, ' at step', step_of_largest_error, ' at ', step_of_largest_error * deltat, 's as largest difference of the time series with ', largest_error_size/(max(time_series)-min(time_series))*100, '% compared to largest possible amplitude')


plt.show()



print('rel. differences for classic DEL calc: %.2f' % ((DEL_v1[0]/DEL_v1[1]-1)*100), '%,', ' new binned DEL: %.2f'
      % ((DEL_v2[0]/DEL_v2[1]-1)*100), '%,', 'new non binned DEL: %.2f' % ((DEL_v3[0]/DEL_v3[1]-1)*100), '%')

print('rel. differences to classic DEL calc1: %.2f' % ((DEL_v1[0]/DEL_v2[0]-1)*100), '%', ' to new binned DEL and %.2f'
      % ((DEL_v1[0]/DEL_v3[0]-1)*100), '% to new non-binned DEL')

print('rel. differences to classic DEL calc2: %.2f' % ((DEL_v1[1]/DEL_v2[1]-1)*100), '%', ' to new binned DEL and %.2f'
      % ((DEL_v1[1]/DEL_v3[1]-1)*100), '% to new non-binned DEL')



























if False:
    import numpy as np
    import matplotlib.pyplot as plt
    from matplotlib import cm
    import math

    filePath = r'C:\xBladed\FOWTs\PythonScripts\iterTowerDamp2_2023_04_20___DEL_evaluation.csv'
    FirstSplittingSequences = '2B20Volt_v009_1_15mps_itr_FA_G'
    SecondSplittingSequences = '_Hz'

    filePath = r'C:\xBladed\FOWTs\PythonScripts\CheckPI_gains_2023_04_20___DEL_evaluation.csv'
    FirstSplittingSequences = '2B20Volt_v009_1_15mps_gain_P'
    SecondSplittingSequences = '_I'





    # loading data from file
    list_dict = Utility().readListDictFromCSV(filePath)

    keys = list(list_dict[0].keys())
    print('dict keys are: ', keys)

    # searching for the first sequence of chars that is equal for all run names
    RunNameRef = list_dict[0].get(keys[0])
    EqualChars_idx = 1
    for Dict in list_dict:
        RunName = Dict.get(keys[0])
        for idx in range(len(RunName)):
            if RunName[:-EqualChars_idx] == RunNameRef[:-EqualChars_idx]:
                if RunName[-EqualChars_idx-1] == '_' or RunName[-EqualChars_idx-1].isnumeric():
                    EqualChars_idx += 1
                break
            else:
                EqualChars_idx += 1
    FirstSplittingSequences = RunNameRef[:-EqualChars_idx]

    # searching for the second sequence of chars that is equal for all run names
    # first filter out the first numerical content (the start of SecondSplittingSequences)
    for idx, Char in enumerate(RunNameRef[-EqualChars_idx:]):
        if Char.isalpha() and Char != '_':
            if RunNameRef[-EqualChars_idx+idx-1] == '_':
                idx = idx - 1
            break
    # than search for the next numerical content (the end of SecondSplittingSequences)
    SecondSplittingSequences = RunNameRef[-EqualChars_idx+idx:]
    for idx, Char in enumerate(SecondSplittingSequences):
        if Char.isnumeric():
            break
    SecondSplittingSequences = SecondSplittingSequences[:idx]

    if EvaluationKeys[0] == 'all':
        EvaluationKeys = keys[1:]

    for key_idx, EvaluationKey in enumerate(EvaluationKeys):
        # restoring data in two-dimensional field
        X = []
        Y = []
        Z = []
        for idx, Dict in enumerate(list_dict):
            RunName = Dict.get(keys[0])
            X.append(float(RunName.split(FirstSplittingSequences)[1].split(SecondSplittingSequences)[0].replace('_', '.')))
            Y.append(float(RunName.split(FirstSplittingSequences)[1].split(SecondSplittingSequences)[1].split('.')[0].replace('_', '.')))
            Z.append(float(Dict.get(EvaluationKey)))

        save_x = X[0]
        for idx, x in enumerate(X):
            if save_x != x:
                xdimension = idx
                # print('X-Dimension is', xdimension)
                break

        X = np.array(X)
        Y = np.array(Y)
        Z = np.array(Z)

        X = np.reshape(X, (-1, xdimension))
        Y = np.reshape(Y, (-1, xdimension))
        Z = np.reshape(Z, (-1, xdimension))


        fig, ax = plt.subplots(subplot_kw={"projection": "3d"})
        # Plot the surface.
        surf = ax.plot_surface(X, Y, Z,  cmap=cm.coolwarm,
                               linewidth=0, antialiased=False, vmin=Z.min(), vmax=min(Z.min()*1.5, Z.max()))

        # Customize the z axis.
        # ax.set_zlim(Z.min(), min(Z.min()*1.5, Z.max()))
        # use to set fixed number of axis values
        # from matplotlib.ticker import LinearLocator
        # ax.zaxis.set_major_locator(LinearLocator(10))
        # A StrMethodFormatter is used automatically
        # ax.zaxis.set_major_formatter('{x:.02f}')

        # Add a color bar which maps values to colors.
        useColorBar = False
        if useColorBar:
            fig.colorbar(surf, shrink=0.5, aspect=20)

        # Add a legend
        ax.set_xlabel(FirstSplittingSequences.split('_')[-1])
        ax.set_ylabel(SecondSplittingSequences.split('_')[-1])
        ax.set_title(EvaluationKey)

        plt.draw()
    plt.show()
