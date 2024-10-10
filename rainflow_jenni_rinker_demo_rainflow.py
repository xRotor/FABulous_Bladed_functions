#!/usr/bin/env python
"""
Demonstration of rainflow cycle counting

Contact: Jennifer Rinker, Duke University
Email:   jennifer.rinker-at-duke.edu
"""
import matplotlib.pyplot as plt
import rainflow_jenni_rinker as rf
import numpy as np

if (__name__ == '__main__'):

    # array of turning points
    array_ext = np.array([3,-2,4,2,5,-1,1,0,3])
    

    from ANSFAB__Utility import Utility
    EvaluationKeys = 'Blade 1 Mx (Root axes)'
    #EvaluationKeys = 'Blade 1 My (Root axes)'

    RunFolder = r'H:\BladedWS\BottomFixed\DLC_legacy\temptemptemp_test_shorterNames_test'
    BladedJob = r'2b101v15_ref_ex5_lookuptabledamp_dlc12_kai.prj'
    [fileEnd, idx, DIMENS] = Utility().collectTimeSeriesStructureFromBladedFiles(RunFolder, BladedJob, EvaluationKeys)
    [time_total, deltat] = Utility().calcTotalTimeAndDeltat(RunFolder, BladedJob)
    time_series = Utility().readTimeSeriesData(RunFolder, BladedJob, fileEnd, idx, DIMENS, pos_of_node=1)#[1:]
    #array_ext = np.array(time_series[100:1000:10])
    time_series.insert(100, 0)
    time_series.insert(100, 0)
    time_series.insert(100, 0)
    time_series.insert(100, 0)
    time_series.insert(100, 0)
    time_series.insert(100, 0)

    [plt, ax] = Utility().easyPlotGraph(time_series, color='b', marker='x', show=False, new_y_axis=False, y_label='DELs')


    #array_ext = np.array([time_series[0]] + [load for idx, load in enumerate(time_series[1:-1]) if np.sign(time_series[idx + 1] - time_series[idx]) != np.sign(time_series[idx + 2] - time_series[idx + 1])])  # the first idx is 0 but should refer to the second value's index
    #visualize = [0] + [idx+1 for idx, load in enumerate(time_series[1:-1]) if np.sign(time_series[idx+1]-time_series[idx]) != np.sign(time_series[idx+2]-time_series[idx+1])]

    TS_turning_points = [time_series[0]]
    visualize = [0]
    for idx, load in enumerate(time_series[1:-1]):  # the first idx is 0 but should refer to the second value's index
        if np.sign(time_series[idx + 1] - time_series[idx]) != np.sign(time_series[idx + 2] - time_series[idx + 1]):
            if load != TS_turning_points[-1]:
                TS_turning_points.append(load)
                visualize.append(idx + 1)
    array_ext = np.array(TS_turning_points)

    [plt, ax] = Utility().easyPlotGraph(array_ext, x_axis=visualize, color='r', marker='x', show=True, new_y_axis=False, ax=ax, y_label='DELs')



    # calculate cycle counts with default values for lfm (0),
    #  l_ult (1e16), and uc_mult (0.5)
    array_out = rf.rainflow(array_ext)
    
    # sort array_out by cycle range
    array_out = array_out[:,array_out[0,:].argsort()]
    
    # ---------------------------- printing/plotting ------------------------------

    # print cycle range, cycle count, cycle mean, goodman-adjusted range (GAR), and
    #   goodman-adjusted range with zero fixed-load mean (GAR-ZFLM)
    print('\nCalculated cycle count:')
    print('\n{:>7s}{:>8s}{:>8s}{:>8s}{:>12s}'.format('Range','Count',
                                      'Mean','GAR','GAR-ZFLM'))
    print('----------------------------------------------')
    for i in range(len(array_out.T)):
        print('{:7.1f}{:8.1f}    {:8.1f}  {:8.1f}{:12.1f}'.format(*array_out[[0,3,1,2,4],i]))
        
    # plot turning points for vizualization
    plt.figure(1,figsize=(6.5,3.5))
    plt.clf()
    
    plt.plot(array_ext)
    plt.grid('on')
    plt.xlabel('Time')
    plt.ylabel('Turning Points')
    plt.title('Turning Points for Rainflow Demo - J. Rinker')
    plt.tight_layout()
    
    plt.show()
    