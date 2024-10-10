from ANSFAB__Utility import Utility
from ANSFAB__Utility import Bladed


folder = r'H:\BladedWS\FOWTs\BruteOptimize_3B20Volt_v009\baselinefile'
out_folder = r'H:\BladedWS\FOWTs\Best_of_BruteForce_full_time_series'
ChangeNameDicts = [{'WORD': 'default', 'EXCHANGE': '_FA_damper_full_TS'}]
ChangeNameDicts = [{'WORD': 'default', 'EXCHANGE': '_full_TS'}]

baseline_files = ['3B20Volt_v009_15mps']

ChangeDicts = []
ChangeDicts.append({'WORD': 'WINDF', 'EXCHANGE': r'WINDF	h:\bladedws\fowts\environmental_conditions\wind_15mps_s15.wnd'})
ChangeDicts.append({'WORD': 'OUTSTR', 'EXCHANGE': 'OUTSTR	 199'})
ChangeDicts.append({'WORD': 'ENDT', 'EXCHANGE': 'ENDT	 3799'})
ChangeDicts.append({'WORD': '        <SpectrumFilePath>', 'EXCHANGE': '        <SpectrumFilePath>H:\BladedWS\FOWTs\environmental_conditions\wave_NSS_15mps_2_395m_7_55s_g1_175.SEA</SpectrumFilePath>'})
# ChangeDicts.append({'WORD': '', 'EXCHANGE': ''})

for baseline_file in baseline_files:
    outfileName, out_folder = Utility().manipulatePRJfiles(ListOfBaselineFiles_local=[baseline_file], infolder=folder,
                                        outfolder=out_folder, ChangeDicts=ChangeDicts, ChangeNameDicts=ChangeNameDicts)
    print(outfileName)
