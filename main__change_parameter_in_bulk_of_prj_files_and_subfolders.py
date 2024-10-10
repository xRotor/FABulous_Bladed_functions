from ANSFAB__Utility import Utility
import os
import numpy as np
from ANSFAB__Utility import Bladed


baseline_folder = r'H:\BladedWS\FOWTs\DLC_ULS____projekt_file_dummy\2B20Volt_v009_baseline\DLC6X__2B20Volt_v009_baseline'
baseline_folder = r'H:\BladedWS\BottomFixed\DLC_legacy\ExtremeDLCs_2B101teeter'
baseline_folder = r'H:\BladedWS\FOWTs\DLC_ULS____projekt_file_dummy\2B20Volt_v009_baseline'
baseline_folder = r'H:\BladedWS\FOWTs\DLC_ULS\2B20Volt_v009_baseline_IAG_stall'
#out_folder = r'H:\BladedWS\FOWTs\DLC_ULS____projekt_file_dummy\2B20Volt_v009_baseline\DLC6X__2B20Volt_v009_baseline__test'

addString = r'_IAG_stall'

ChangeDicts = []
ChangeDicts.append({'WORD': r'  <DynamicStallModel>BeddoesIncomp</DynamicStallModel>', 'EXCHANGE': r'  <DynamicStallModel>IAGModel</DynamicStallModel>'})
ChangeDicts.append({'WORD': r'  <UseKirchoffFlow>false</UseKirchoffFlow>', 'EXCHANGE': r'  <UseKirchoffFlow>true</UseKirchoffFlow>'})
ChangeDicts.append({'WORD': r'  <UseImpulsiveContributions>false</UseImpulsiveContributions>', 'EXCHANGE': r'  <UseImpulsiveContributions>true</UseImpulsiveContributions>'})
ChangeDicts.append({'WORD': r'  <VortexTravelTimeConstant>7.5</VortexTravelTimeConstant>', 'EXCHANGE': r'  <VortexTravelTimeConstant>6</VortexTravelTimeConstant>'})
ChangeDicts.append({'WORD': r'  <AttachedFlowConstantA1>0.165</AttachedFlowConstantA1', 'EXCHANGE': r'  <AttachedFlowConstantA1>0.3</AttachedFlowConstantA1>'})
ChangeDicts.append({'WORD': r'  <AttachedFlowConstantA2>0.335</AttachedFlowConstantA2>', 'EXCHANGE': r'  <AttachedFlowConstantA2>0.7</AttachedFlowConstantA2>'})
ChangeDicts.append({'WORD': r'  <AttachedFlowConstantb1>0.0455</AttachedFlowConstantb1>', 'EXCHANGE': r'  <AttachedFlowConstantb1>0.7</AttachedFlowConstantb1>'})
ChangeDicts.append({'WORD': r'  <AttachedFlowConstantb2>0.3</AttachedFlowConstantb2>', 'EXCHANGE': r'  <AttachedFlowConstantb2>0.53</AttachedFlowConstantb2>'})


addString = r'__teeter'
ChangeDicts = []
ChangeDicts.append({'WORD': r'TEETER	N', 'EXCHANGE': r'TEETER	Y'})
ChangeDicts.append({'WORD': r'P15: use2B_teetering=0; // 1 if 2B teetering, 4 if LIPC else 0', 'EXCHANGE': r'P15: use2B_teetering=1; // 1 if 2B teetering, 4 if LIPC else 0'})


baseline_folder = r'H:\BladedWS\BottomFixed\DLC_legacy\ExtremeDLCs_2B101v19_LIPC_bode_v1_light_blades__IAG_stall'
addString = r'_new'
ChangeDicts = []
ChangeDicts.append({'WORD': r'OPSTP	 .01', 'EXCHANGE': r'OPSTP	 .1'})
#ChangeDicts.append({'WORD': r'ddsdsdsvdsddfddf', 'EXCHANGE': r'OPSTP	 .1'})

baseline_folder = r'H:\BladedWS\FOWTs\DLC_ULS\2B20Volt_v009_baseline_IAG_stall__teeter_v4__teeterStopAt4rpm'
addString = r'_noWaves'
ChangeDicts = []
ChangeDicts.append({'WORD': r'<SpectrumFilePath>H:\BladedWS\FOWTs', 'EXCHANGE': r'        <SpectrumFilePath>H:\BladedWS\FOWTs\environmental_conditions\wave_calm_sea.SEA</SpectrumFilePath>'})
#ChangeDicts.append({'WORD': r'ddsdsdsvdsddfddf', 'EXCHANGE': r'OPSTP	 .1'})


baseline_folder = r'H:\BladedWS\FOWTs\DLC_ULS\2B20Volt_v009_baseline_IAG_stall__teeter_v4__teeterStopAt4rpm'
baseline_folder = r'H:\BladedWS\FOWTs\DLC_ULS\3B20Volt_v008_baseline_IAG_stall_v2'
baseline_folder = r'H:\BladedWS\FOWTs\DLC_ULS\2B20Volt_v009_baseline_IAG_stall_v2'
addString = r'_noWind'
ChangeDicts = []

#ChangeDicts.append({'WORD': r'WMODEL	', 'EXCHANGE': r'WMODEL	1'})
#ChangeDicts.append({'WORD': r'UBAR	', 'EXCHANGE': r'USPD	2'})
#ChangeDicts.append({'WORD': r'USPD	', 'EXCHANGE': r'USPD	2'})
#ChangeDicts.append({'WORD': r'VWSSTRT	', 'EXCHANGE': r'USPD	2'})
#ChangeDicts.append({'WORD': r'HWSSTRT	', 'EXCHANGE': r'WDIR	 0'})


ChangeDicts.append({'WORD': r'MooringInitState', 'EXCHANGE': r'MooringInitState 0 0 0 0 0 0'})
ChangeDicts.append({'WORD': r'TURBHTTYPE	', 'EXCHANGE': r''})
ChangeDicts.append({'WORD': r'TI	', 'EXCHANGE': r''})
ChangeDicts.append({'WORD': r'TI_V	', 'EXCHANGE': r''})
ChangeDicts.append({'WORD': r'TI_W	', 'EXCHANGE': r''})
ChangeDicts.append({'WORD': r'WINDF	', 'EXCHANGE': r''})
ChangeDicts.append({'WORD': r'INTERPYZ	', 'EXCHANGE': r''})
ChangeDicts.append({'WORD': r'CIRCWIND	', 'EXCHANGE': r''})
ChangeDicts.append({'WORD': r'DIRAMP	', 'EXCHANGE': r''})
ChangeDicts.append({'WORD': r'DIRSTIME	', 'EXCHANGE': r''})
ChangeDicts.append({'WORD': r'DIRTIMEP	', 'EXCHANGE': r''})
ChangeDicts.append({'WORD': r'DIRTYPE	', 'EXCHANGE': r''})
ChangeDicts.append({'WORD': r'DIRRATE	', 'EXCHANGE': r''})
ChangeDicts.append({'WORD': r'GUSTPROPAGATION	', 'EXCHANGE': r''})

ChangeDicts.append({'WORD': r'WSSTRT	', 'EXCHANGE': r''})
ChangeDicts.append({'WORD': r'WSAMP	', 'EXCHANGE': r''})
ChangeDicts.append({'WORD': r'WSSTIME	', 'EXCHANGE': r''})
ChangeDicts.append({'WORD': r'WSTIMEP	', 'EXCHANGE': r''})
ChangeDicts.append({'WORD': r'WSTYPE	', 'EXCHANGE': r''})
ChangeDicts.append({'WORD': r'DIRSTRT	', 'EXCHANGE': r''})
ChangeDicts.append({'WORD': r'DIRAMP	', 'EXCHANGE': r''})
ChangeDicts.append({'WORD': r'DIRSTIME	', 'EXCHANGE': r''})
ChangeDicts.append({'WORD': r'DIRTIMEP	', 'EXCHANGE': r''})
ChangeDicts.append({'WORD': r'DIRTYPE	', 'EXCHANGE': r''})
ChangeDicts.append({'WORD': r'HWSSTRT	', 'EXCHANGE': r''})
ChangeDicts.append({'WORD': r'HWSAMP	', 'EXCHANGE': r''})
ChangeDicts.append({'WORD': r'HWSSTIME	', 'EXCHANGE': r''})
ChangeDicts.append({'WORD': r'HWSTIMEP	', 'EXCHANGE': r''})
ChangeDicts.append({'WORD': r'HWSTYPE	', 'EXCHANGE': r''})
ChangeDicts.append({'WORD': r'VWSSTRT	', 'EXCHANGE': r''})
ChangeDicts.append({'WORD': r'VWSAMP	', 'EXCHANGE': r''})
ChangeDicts.append({'WORD': r'VWSSTIME	', 'EXCHANGE': r''})
ChangeDicts.append({'WORD': r'VWSTIMEP	', 'EXCHANGE': r''})
ChangeDicts.append({'WORD': r'VWSTYPE	', 'EXCHANGE': r''})
ChangeDicts.append({'WORD': r'VDCSTRT	', 'EXCHANGE': r''})
ChangeDicts.append({'WORD': r'VDCAMP	', 'EXCHANGE': r''})
ChangeDicts.append({'WORD': r'VDCSTIME	', 'EXCHANGE': r''})
ChangeDicts.append({'WORD': r'VDCTIMEP	', 'EXCHANGE': r''})
ChangeDicts.append({'WORD': r'VDCTYPE	', 'EXCHANGE': r''})

ChangeDicts.append({'WORD': r'MEANHTTYPE	', 'EXCHANGE': r''})
ChangeDicts.append({'WORD': r'USPD	', 'EXCHANGE': r''})
ChangeDicts.append({'WORD': r'REFHT	', 'EXCHANGE': r''})
ChangeDicts.append({'WORD': r'WDIR	', 'EXCHANGE': r''})
ChangeDicts.append({'WORD': r'FLINC	', 'EXCHANGE': r''})


ChangeDicts.append({'WORD': r'WMODEL	', 'EXCHANGE': r'WMODEL	1\nMEANHTTYPE	1\nUSPD	 2\nREFHT	 160\nWDIR	 0\nFLINC	 0'})

out_folder = baseline_folder + addString
Utility().createFolderIfNotExcisting(out_folder)
subfolders = [folder[0] for folder in os.walk(baseline_folder)]


for subfolder in subfolders:
    print('loading runs in folder: ', subfolder)
    if subfolder != baseline_folder:
        out_subfolder = subfolder.replace(baseline_folder, out_folder) + addString
        Utility().createFolderIfNotExcisting(out_subfolder)

    baseline_files = [path.split('\\')[-1] for path in Utility().return_run_files_in_folder(subfolder)]
    for baseline_file in baseline_files:
        ChangeNameDicts = [{'WORD': 'v009_', 'EXCHANGE': 'v009_teeter_'}]
        ChangeNameDicts = [{'WORD': 'fdgdffdsgxvxrrxtdx', 'EXCHANGE': ''}]
        ChangeNameDicts = [{'WORD': 'v009_', 'EXCHANGE': 'v009_noWind_'}]
        #ChangeNameDicts = [{'WORD': 'v008_', 'EXCHANGE': 'v008_noWind_'}]

        outfileName, out_subfolder = Utility().manipulatePRJfiles(ListOfBaselineFiles_local=[baseline_file], infolder=subfolder,
                                            outfolder=out_subfolder, ChangeDicts=ChangeDicts, ChangeNameDicts=ChangeNameDicts, shorten_files=False)
        print(outfileName)
