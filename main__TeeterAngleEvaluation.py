""" ====================================================================================================================

                                              teeter angle evaluation
                         ------------------------------------------------------------------

                    -> Reading Bladed time series
                    -> Searching for peaks of teeter angle excursions
                    -> Doin' statistical stuff

==================================================================================================================== """

from ANSFAB__Utility import Bladed, Utility
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

RunFolder = r'H:\BladedWS\CheckTeeterAngleScaling\runs'
BladedJobs = ['2B20MW_v18_teeter_15mps_highRes_without_dampers_n_imbal.$PJ', r'CART2_ref_15mps_highRes__Bladed4_13.$PJ', r'CART2_ref_15mps_highRes_smallWindField__Bladed4_13.$PJ',
                r'2B20MW_v18_teeter_15mps_highRes_roughness0_001_no_dampers_n_imbal.$PJ', r'2B20MW_v18_teeter_15mps_highRes_roughness0_006_no_dampers_n_imbal.$PJ', r'2B20MW_v18_teeter_15mps_highRes_roughness0_083_no_dampers_n_imbal.$PJ',
                r'2B20MW_v18_teeter_15mps_highRes_roughness0_133_no_dampers_n_imbal.$PJ', r'2B20MW_v18_teeter_15mps_highRes_shearExpo0_14_no_dampers_n_imbal.$PJ',
                r'CART2_ref_15mps_highRes__roughness0_001__Bladed4_13.$PJ', r'CART2_ref_15mps_highRes__roughness0_03__Bladed4_13.$PJ', r'CART2_ref_15mps_highRes__roughness0_006__Bladed4_13.$PJ', r'CART2_ref_15mps_highRes__roughness0_083__Bladed4_13.$PJ',
                r'CART2_ref_15mps_highRes__shearExpo0_14__Bladed4_13.$PJ']
BladedJobs = ['2B20MW_v18_teeter_15mps_highRes_without_dampers_n_imbal_noGravity_shearExpo0_14', r'2B20MW_v18_teeter_15mps_highRes_without_dampers_n_imbal_noGravity_roughness0_083',r'CART2_ref_15mps_highRes_noGravity_shearExpo0_14_Bladed4_13', r'CART2_ref_15mps_highRes_noGravity_roughness0_083_Bladed4_13']

pi = 3.14159265

if True:
    for BladedJob in BladedJobs:
        TimeSeriesPeaksPerRotation, TimeSeries = Bladed().collectPeakPerRevolution(RunFolder, BladedJob, AdaptMean=True)
        print('The standard deviation is ', np.std(TimeSeriesPeaksPerRotation) * 180/pi,
              'deg , the mean is ', sum(TimeSeriesPeaksPerRotation)/len(TimeSeriesPeaksPerRotation) * 180/pi,
              'deg and a max value', max(TimeSeriesPeaksPerRotation) * 180/pi, 'for the peaks in run', BladedJob)

        print('\n')


        plt.plot(TimeSeries)
        plt.ylabel('teeter angle in rad')
        plt.grid()
    plt.show()
else:

    path = r'H:\BladedWS\CheckTeeterAngleScaling\2B_Energy_6MW_data\PowerProduction\2B6_NormalProduction_restructered.xlsx'
    number_headers = 3
    data_sheet = pd.read_excel(path, index_col=0, header=number_headers)
    # time series in first row are the keys of the first time series
    time_TS = data_sheet.get(data_sheet.keys()[0]).keys().to_list()
    # teeter angle time series in second row:
    teeter_TS = data_sheet.get(data_sheet.keys()[0]).to_list()
    teeter_TS_in_deg = teeter_TS
    teeter_TS = [i*pi/180 for i in teeter_TS]  # convert deg to rad
    # rotation speed is the fourth row
    rotation_speed_TS = data_sheet.get(data_sheet.keys()[2]).to_list()
    rotation_speed_TS = [i*2*pi/60 for i in rotation_speed_TS]  # convert rpm in rad/s

    TimeSeriesPeaksPerRotation, TimeSeries = Bladed().collectPeakPerRevolution(rotation_speed_TS=rotation_speed_TS, teeter_TS=teeter_TS, deltat=time_TS[1]-time_TS[0], time_total=time_TS[-1], AdaptMean=True)
    print('The standard deviation is ', np.std(TimeSeriesPeaksPerRotation) * 180/pi,
          'deg , the mean is ', sum(TimeSeriesPeaksPerRotation)/len(TimeSeriesPeaksPerRotation) * 180/pi,
          'deg and a max value', max(TimeSeriesPeaksPerRotation) * 180/pi, 'for the peaks in run', path)


    plt.plot(time_TS, TimeSeries)
    #plt.plot(time_TS, rotation_speed_TS)
    plt.ylabel('teeter angle in rad')
    plt.grid()
    plt.show()










'''VariableName = 'Teeter angle (delta-3 direction)'
RotorSpeedVariableName = 'Rotor speed'
fileEnd, idx, DIMENS = Utility().collectTimeSeriesFromBladedFiles(RunFolder, BladedJob, RotorSpeedVariableName)
TimeSeries = Utility().readTimeSeriesData(RunFolder, BladedJob, fileEnd, idx, DIMENS)
meanRotorSpeed__rad_per_s = sum(TimeSeries)/len(TimeSeries)
pi = 3.14159265359
searchInterval_s = 2 * pi / meanRotorSpeed__rad_per_s
print('Rotation speed is', meanRotorSpeed__rad_per_s * 60 / 2 / pi,
      'rpm. The interval to search for peaks in the time series is', searchInterval_s, 's')


fileEnd, idx, DIMENS = Utility().collectTimeSeriesFromBladedFiles(RunFolder, BladedJob, VariableName)
TimeSeries = Utility().readTimeSeriesData(RunFolder, BladedJob, fileEnd, idx, DIMENS)
[time_total, deltat] = Utility().calcTotalTimeAndDeltat(RunFolder, BladedJob)

from math import floor  # round to lower value; just in case
Number_Intervals = floor(time_total / searchInterval_s)
Values_per_Interval = int(searchInterval_s / deltat)
TimeSeriesPeaksPerRotation = []
idx_Peak = 0
Interval_shift = 0
for idx_Interval in range(Number_Intervals):
    OneRotationTimeSeries = TimeSeries[idx_Interval    * Values_per_Interval + Interval_shift:
                                      (idx_Interval+1) * Values_per_Interval + Interval_shift]
    MaxIntervalValue = max(OneRotationTimeSeries)
    if TimeSeries.index(MaxIntervalValue) - idx_Peak < Values_per_Interval/2:
        for idx, value in enumerate(OneRotationTimeSeries):
            if value < 0:
                break
        Interval_shift += idx
        OneRotationTimeSeries = TimeSeries[idx_Interval      * Values_per_Interval + Interval_shift:
                                          (idx_Interval + 1) * Values_per_Interval + Interval_shift]
        MaxIntervalValue = max(OneRotationTimeSeries)

    TimeSeriesPeaksPerRotation.append(MaxIntervalValue)
    idx_Peak = TimeSeries.index(MaxIntervalValue)

    # just for visualization
    TimeSeries[idx_Peak] = TimeSeriesPeaksPerRotation[-1]*4'''