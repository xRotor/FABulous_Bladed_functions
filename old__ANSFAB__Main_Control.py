import os
import matplotlib.pyplot as plt
# custom scripts:
from ANSFAB__Bladed_Utility_Functions import listRunNamesInFolder, searchForBladedOutputParams, readTimeSeries,\
    calcDELfromTimeSeries, writeListDictToCSV

##################################################################
# Main folder of the desired bladed runs ------------------------
RunFolder = r'H:\BladedWS\FOWTs\2B_FA_damper_itr_inc_Hz_filt'
RunFolder = r'H:\BladedWS\FOWTs\2B_FA_damper_itr_inc_1P_Hz_filt'
RunFolder = r'H:\BladedWS\FOWTs\2B_FA_damper_teeter_itr_inc_Hz_filt'
RunFolder = r'H:\BladedWS\FOWTs\3B_tow0_FA_damper_itr_inc_1P_Hz_filt'
RunFolder = r'H:\BladedWS\FOWTs\3B_FA_damper_itr'
RunFolder = r'H:\BladedWS\FOWTs\3B_FA_damper_itr_inc_Hz_filt'
##################################################################


Params = [{'GENLAB': 'Tower member loads - local coordinates', 'VARIAB': 'Tower My'},
          {'GENLAB': 'Tower member loads - local coordinates', 'VARIAB': 'Tower Mz'}]

RunNames = listRunNamesInFolder(RunFolder)
print(RunNames)

Params = searchForBladedOutputParams(RunFolder, RunNames, Params)
print(Params)

Params = readTimeSeries(RunFolder, RunNames, Params)
# print(Params)

time_total = float(Params[0].get('DIMENS')[-1]) / Params[0].get('STEP')
for idx_Param, Param in enumerate(Params):
    DELs = []
    for idx_Run, RunName in enumerate(RunNames):
        DELs.append(calcDELfromTimeSeries(Param.get('TIMESERIES')[idx_Run], time_total))
    Params[idx_Param]['DEL'] = DELs

ListDict = []
for idx, RunName in enumerate(RunNames):
    ListDict.append({'RunName': RunName, 'Tower Mx DEL': Params[0].get('DEL')[idx], 'Tower My DEL': Params[1].get('DEL')[idx]})

writeListDictToCSV(ListDict, 'H:\BladedWS\FOWTs\Evaluation_3B_FA_damper_itr_inc_Hz_filt.csv')



if True:
    initial_plot = plt.figure(figsize=(7, 5))
    plt.xlabel('Runs')
    plt.ylabel('DELs')
    plt.title(RunFolder)
    for idx in range(2):
        plt.plot(RunNames, Params[idx].get('DEL'), label=Params[idx].get('VARIAB'))
    # plt.plot(range(int(Params[0].get('DIMENS')[-1])), Params[0].get('TIMESERIES')[0], label=Params[0].get('VARIAB'))
    plt.legend()
    # plt.legend(bbox_to_anchor=(1.04, 1), loc="upper left")
    plt.xticks(rotation=90)
    plt.show()