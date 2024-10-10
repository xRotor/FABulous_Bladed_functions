from ANSFAB__Utility import Utility
import scipy.signal
import matplotlib.pyplot as plt
import numpy as np

RunFolder = r'H:\BladedWS\FOWTs\DLC_ULS\2B20Volt_v009_baseline_IAG_stall_v2\DLC12__2B20Volt_v009_baseline_IAG_stall'
BladedJob = r'2B20Volt_v009_baseline_DLC12__17mps_s117_IAG_stall'
RunFolder = r'H:\BladedWS\FOWTs\DecayTowerVibrationTest'
BladedJob = r'3B20Volt_2B_v009_towerBendingDecayTest_about_x__gain1_11'
BladedJob = r'3B20Volt_2B_v009_towerBendingDecayTest_about_x__gain1_11_hi_res'

# Utility().calcBearingDamage(RunFolder, BladedJob)



[time_total, deltat] = Utility().calcTotalTimeAndDeltat(RunFolder, BladedJob)
[fileEnd, idx, DIMENS] = Utility().collectTimeSeriesStructureFromBladedFiles(
            RunFolder=RunFolder, BladedJob=BladedJob, VariableName='Nacelle side-side displacement')
TimeSeries = Utility().readTimeSeriesData(RunFolder=RunFolder, BladedJob=BladedJob,
            fileEnd=fileEnd, idx=idx, DIMENS=DIMENS, pos_of_node=1)[5000:]

start = int(400/deltat)
end = int(454/deltat)
TimeSeries = [TimeSeries[start]*5 for _ in TimeSeries[:start]] + [i*5 for i in TimeSeries[start:end]] + [TimeSeries[end]*5 for _ in TimeSeries[end:]]

FilterOrderN = 2
max_frequency = 0.1  # 0.16
fs = 1 / deltat
sos = scipy.signal.butter(FilterOrderN, Wn=max_frequency, fs=fs, btype='lp', output='sos')  # low pass
# sos = scipy.signal.butter(FilterOrderN, Wn, fs=fs, btype='bandpass', output='sos')
TimeSeries_filtered = scipy.signal.sosfilt(sos, TimeSeries)
TimeSeries_filtered =[i for i in TimeSeries_filtered[105:]] + [TimeSeries_filtered[105] for _ in TimeSeries_filtered[:105]]
TimeSeries_filtered = [TimeSeries[idx] - TimeStep for idx, TimeStep in enumerate(TimeSeries_filtered)]
#TimeSeries_filtered = [TimeSeries_filtered[start-1000] for _ in TimeSeries_filtered[:start-1000]] + [i for i in TimeSeries_filtered[start-1000:end+1000]] + [TimeSeries_filtered[end+1000] for _ in TimeSeries_filtered[end+1000:]]
TimeSeries_filtered = [0 for _ in TimeSeries_filtered[:start-1000]] + [i for i in TimeSeries_filtered[start-1000:end+1000]] + [0 for _ in TimeSeries_filtered[end+1000:]]

(f, Gyy) = scipy.signal.welch(TimeSeries, fs=1/deltat, nperseg=4 * 1024)
fig, ax = plt.subplots()
ax.plot(f[1:], Gyy[1:], label='time series', color='r')
ax.set(xlabel='frequency in Hz',  ylabel='density')
plt.yscale('log')

(f, Gyy) = scipy.signal.welch(TimeSeries_filtered, fs=1/deltat, nperseg=4 * 1024)
ax.plot(f[1:], Gyy[1:], label='filtered', color='b')

x_axis = [i for i in np.linspace(0, len(TimeSeries)*deltat, len(TimeSeries))]
#plt, ax = Utility().easyPlotGraph(TimeSeries, x_axis=x_axis, marker='',  show=False)
x_axis = [i for i in np.linspace(0, len(TimeSeries_filtered)*deltat, len(TimeSeries_filtered))]
plt, ax = Utility().easyPlotGraph(TimeSeries_filtered, x_axis=x_axis,  show=False, marker='', color='r') # , ax=ax)



BladedJob = r'3B20_bfixed_ref___towerBendingDecayTest_in_y_stronger_longerer'
[time_total, deltat] = Utility().calcTotalTimeAndDeltat(RunFolder, BladedJob)
[fileEnd, idx, DIMENS] = Utility().collectTimeSeriesStructureFromBladedFiles(
            RunFolder=RunFolder, BladedJob=BladedJob, VariableName='Nacelle side-side displacement')
TimeSeries = Utility().readTimeSeriesData(RunFolder=RunFolder, BladedJob=BladedJob,
            fileEnd=fileEnd, idx=idx, DIMENS=DIMENS, pos_of_node=1)  # [15000:]
x_axis = [i for i in np.linspace(0, len(TimeSeries)*deltat, len(TimeSeries))]

plt, ax = Utility().easyPlotGraph(TimeSeries, x_axis=x_axis, ax=ax, new_y_axis=False, marker='', color='g')



results_list_dict = []
for timeStep in range(0, len(TimeSeries), 4):
    results_list_dict.append({'time': x_axis[timeStep]})
    results_list_dict[-1]['Fixed_Bottom__StS_movment_m'] = TimeSeries[timeStep]
    if timeStep < len(TimeSeries_filtered):
        results_list_dict[-1]['FOWT__StS_movment_m'] = TimeSeries_filtered[timeStep]
    else:
        results_list_dict[-1]['FOWT__StS_movment_m'] = TimeSeries_filtered[-1]

documentation_path = RunFolder + r'\decayTestResults.csv'
documentation_path = Utility().writeListDictToCSV(results_list_dict, documentation_path)





''' looked smooth:
BladedJob = r'3B20Volt_2B_v009_towerBendingDecayTest_about_x__gain1_11'
FilterOrderN = 1
max_frequency = 0.1  # 0.16
fs = 1 / deltat
sos = scipy.signal.butter(FilterOrderN, Wn=max_frequency, fs=fs, btype='lp', output='sos')  # low pass
# sos = scipy.signal.butter(FilterOrderN, Wn, fs=fs, btype='bandpass', output='sos')
TimeSeries_filtered = scipy.signal.sosfilt(sos, TimeSeries)
TimeSeries_filtered =[i for i in TimeSeries_filtered[21:]] + [TimeSeries_filtered[21] for _ in TimeSeries_filtered[:21]]
'''