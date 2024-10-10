from ANSFAB__Utility import Utility
import numpy as np
from ANSFAB__Utility import Bladed
import os


baseline_folder = r'H:\BladedWS\BottomFixed\DLC_legacy\3Bref_IEA_Monopile'

search_string = 'WINDF	H:\BladedWS\BottomFixed\DLC_legacy\DLC12windFileNew2_from5to25'

Include_Childfolder = True























replace_row = ''


infiles = []
if Include_Childfolder:
    subfolders = [folder[0] for folder in os.walk(baseline_folder)]
    print('found folders ---> ', subfolders)

    for subfolder in subfolders:
        childfiles = Utility().return_run_files_in_folder(subfolder)
        if childfiles:
            print('found in folder ---> ', subfolder, ' the files --->', childfiles)

            infiles.extend(childfiles)
else:
    #run_files = [path.split('\\')[-1] for path in Utility().return_run_files_in_folder(baseline_folder)]
    infiles.extend(Utility().return_run_files_in_folder(baseline_folder))


#for idx_file, run_file in enumerate(run_files):
#    infile = open(os.path.join(baseline_folder, run_file), "r")
#    outfileName = run_file.replace(old_string, new_string)
#    outfile = open(os.path.join(out_folder, outfileName), "w")
recognized_folders = []
for idx_file, infile in enumerate(infiles):
    # print('adapting: ', infile)
    run_file = infile.split('\\')[-1].split('.')[0]
    folder = infile.replace(infile.split('\\')[-1],'')

    infile = open(infile, "r")
    for row in infile:
        if isinstance(search_string, str):
            if row.find(search_string) != -1:
                    print('found string in', run_file)
                    if not folder in recognized_folders:
                        recognized_folders.append(folder)
                    #print('replacing', row, 'by', replace_row)
                    #row = replace_row
        else:
            for search_string_i, replace_row_i in zip(search_string, replace_row):
                if row.find(search_string_i) != -1:
                    print('found string in', run_file)
                    if not folder in recognized_folders:
                        recognized_folders.append(folder)
                    #print('replacing', row, 'by', replace_row_i)
                    #row = replace_row_i
    infile.close()

print('\nfound string:', search_string, 'in folders:', *recognized_folders, sep='\n')















search_string = 'USPD	 15'
replace_row = 'USPD	 5\n'
search_string = 'WSHEAR	 '
replace_row = 'WSHEAR	 .14\n'
search_string = 'ENDT	 3630'
replace_row = 'ENDT	 630\n'
search_string = '        <Filepath>H:\BladedWS\BottomFixed\DTU_discon_v31_LIPC_123PP_bode_based__with_use_teetering_4_for_LIPC_param.dll</Filepath>\n'
search_string = '        <Filepath>H:\BladedWS\BottomFixed\DTU_discon_v25_5_3.dll</Filepath>\n'
replace_row = '        <Filepath>H:\BladedWS\BottomFixed\DTU_discon_v31_LIPC_OWT_and_v55_FOWT_fusion__newInitPitchAngle.dll</Filepath>\n'
search_string = 'P6: maxOverspeedFactor=1.8 // factor on omega_r[default = 1.12]\n'
replace_row = 'P6: maxOverspeedFactor=1.8; // factor on omega_r[default = 1.12]\n'
search_string = '        <Filepath>H:\BladedWS\BottomFixed\DTU_discon_v31_LIPC_OWT_and_v55_FOWT_fusion_Debug.dll</Filepath>\n'
replace_row = '        <Filepath>H:\BladedWS\BottomFixed\DTU_discon_v31_LIPC_OWT_and_v55_FOWT_fusion__newInitPitchAngle.dll</Filepath>\n'

search_string = 'P12: towerFrequencyToAvoid='
replace_row = 'P12: towerFrequencyToAvoid=0; // 0=not used, else frequency is tried to be avoided by 2P/3P; best 0.162\n'


search_string = 'P11: factor_Pitch_FATowDamper='
replace_row = 'P11: factor_Pitch_FATowDamper=0;  // 0=not used, default [2:0.4,5:0.4,7:0.3,9:0,11:0,13:0.04,15:0.05,17:0.04,19:0.15,21:0.14,23:0.1,25:0.12]\n'

search_string = '        <Filepath>H:\BladedWS\BottomFixed'
replace_row = '        <Filepath>H:\BladedWS\BottomFixed\DTU_discon_v31_LIPC_OWT_and_v55_FOWT_fusion__newInitPitchAngle.dll</Filepath>\n'

search_string = 'ENDT	 '
replace_row = 'ENDT	 330\n'

search_string = 'OPSTP'
replace_row = 'OPSTP	 .04\n'




if False: # change to IAG-stall
    search_string = []
    replace_row = []
    search_string.append('  <DynamicStallModel>')
    replace_row.append(  '  <DynamicStallModel>IAGModel</DynamicStallModel>\n')
    search_string.append('  <UseKirchoffFlow>')
    replace_row.append(  '  <UseKirchoffFlow>true</UseKirchoffFlow>\n')
    search_string.append('  <UseImpulsiveContributions>')
    replace_row.append(  '  <UseImpulsiveContributions>true</UseImpulsiveContributions>\n')
    search_string.append('  <VortexTravelTimeConstant>')
    replace_row.append(  '  <VortexTravelTimeConstant>6</VortexTravelTimeConstant>\n')
    search_string.append('  <AttachedFlowConstantA1>')
    replace_row.append(  '  <AttachedFlowConstantA1>0.3</AttachedFlowConstantA1>\n')
    search_string.append('  <AttachedFlowConstantA2>')
    replace_row.append(  '  <AttachedFlowConstantA2>0.7</AttachedFlowConstantA2>\n')
    search_string.append('  <AttachedFlowConstantb1>')
    replace_row.append(  '  <AttachedFlowConstantb1>0.7</AttachedFlowConstantb1>\n')
    search_string.append('  <AttachedFlowConstantb2>')
    replace_row.append(  '  <AttachedFlowConstantb2>0.53</AttachedFlowConstantb2>\n')

if False: # change to imbalance
    #2Bv15 new normal imbalance
    search_string = []
    replace_row = []
    search_string.append('MTOLM')
    replace_row.append(  'MTOLM	 778\n')
    search_string.append('MTOLR')
    replace_row.append(  'MTOLR	 38.45\n')
    search_string.append('ATOLB')
    replace_row.append(  'ATOLB	-5.23598354139262E-03, 5.23598354139262E-03\n')

    # 3B ref new normal imbalance
    replace_row = []
    replace_row.append(  'MTOLM	 589\n')
    replace_row.append(  'MTOLR	 37.00\n')
    replace_row.append(  'ATOLB	 0, 5.23598354139262E-03,-5.23598354139262E-03\n')












# if False:  # old version for the manipulation of wind files:
#     baseline_folder = r'H:\BladedWS\windfiles_kaimal_5to25mps'
#     out_folder = r'H:\BladedWS\NTM_Kaimal__baseline_v2'
#
#     baseline_files = [path.split('\\')[-1] for path in Utility().return_run_files_in_folder(baseline_folder)]
#     Utility().createFolderIfNotExcisting(out_folder)
#
#     old_string = '121'
#     new_strings = ['264', '473', '551', '627', '961']
#     wind_speeds = ['05', '07', '09', '11', '13', '15', '17', '19', '21', '23', '25']
#
#     for idx_seed, new_string in enumerate(new_strings):
#         for idx_file, baseline_file in enumerate(baseline_files):
#             old_string = '1' + wind_speeds[idx_file]
#             new_string = str(idx_seed+2) + wind_speeds[idx_file]
#             infile = open(os.path.join(baseline_folder, baseline_file), "r")
#             outfileName = baseline_file.replace(old_string, new_string)
#             outfile = open(os.path.join(out_folder, outfileName), "w")
#
#             for row in infile:
#                 #if row.find(infileName) != -1:
#                 #    row = '  <Name>' + outfileName + '</Name>\n'
#                 if row.find(old_string) != -1:
#                     if row.find('SEED') != -1 or row.find('OUTFILE') != -1:
#                         print('replacing', row, 'by', row.replace(old_string, new_string))
#                         row = row.replace(old_string, new_string)
#                 outfile.write(row)
#
#             outfile.close()
#             infile.close()
