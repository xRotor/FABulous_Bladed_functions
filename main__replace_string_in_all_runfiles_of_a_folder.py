from past.utils import old_div

from ANSFAB__Utility import Utility
import numpy as np
from ANSFAB__Utility import Bladed
import os




baseline_folder = r'H:\BladedWS\BottomFixed\DLC_legacy\ExtremeDLCs_3B_ref_IAG_stall_new_DISCON\DLC14_3B_ref_ECD_IAG_stall'
out_folder = baseline_folder +  r'_new'

old_string = 'asds_mps_s1'
new_string = 'mps_s6'



search_string = '<SpectrumFilePath>'
replace_row = '        <SpectrumFilePath>H:\BladedWS\FOWTs\environmental_conditions\wave_calm_sea.SEA</SpectrumFilePath>\n'
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

search_string = 'OPSTP'
replace_row = 'OPSTP	 .04\n'

search_string = 'ENDT	 '
replace_row = 'ENDT	 250\n'




#search_string = 'P14: use2B_upscaled='
#replace_row = 'P14: use2B_upscaled=0; // 1 if 2B upscaled versions with same absolut power \nP15: use2B_teetering=0; // 1 if 2B teetering, 4 if LIPC else 0\n'

Include_Childfolder = False

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

if False:
    search_string = []
    replace_row = []
    old_string = []
    new_string = []
    for wspeed in range(5,26,2):
        for oldseed, newseed_idx in zip([121, 264, 473, 551, 627, 961], range(1,7)):
            search_string.append(r'WINDF	H:\BladedWS\BottomFixed\DLC_legacy\DLC12windFileNew2_from5to25\NTM_%s_s%s.wnd' %(wspeed, oldseed))
            replace_row.append(  r'WINDF	H:\BladedWS\windfiles_kaimal_5to25mps\ntm_kaimal_%smps_s%s%s.wnd' %(str(wspeed).zfill(2), newseed_idx, str(wspeed).zfill(2))+'\n')

            old_string.append('_%smps_s%s' % (str(wspeed).zfill(2), oldseed))
            new_string.append('_%smps_s%s%s' %(str(wspeed).zfill(2), newseed_idx, str(wspeed).zfill(2)))

    if True:
        old_string.append('_y00_')
        old_string.append('_yn8_')
        old_string.append('_yp8_')
        new_string.append('_00y_')
        new_string.append('_n8y_')
        new_string.append('_p8y_')

        old_string.append('DLC21_')
        new_string.append('DLC22_')

if True:
    search_string = []
    replace_row = []
    search_string.append('Params	""')
    replace_row.append('Params	""\nMEND\n\nMSTART YAWCON\nYMODEL	2\nYAWTYPE	0\nKYAW	 0\nVOLUME	 0\nPRESSURE	 0\nPUMPRATE	 0\nTRQRATE	 0\nGAMMA	 0\nCYAW	 0\nVTOL	 0\nQCOUL	 0\nQSTICK	 0\nDYAW2	 0\nDYAW2DB	 0\nYRATE	 0\n')

    search_string.append('0WINDV')
    replace_row.append('0WINDV\n0YAWCON\n')

    search_string.append('DISCRETE_Y	')
    replace_row.append('DISCRETE_Y	2\n')

    search_string.append('OPTIONS	137655')
    replace_row.append('OPTIONS	154039\n')

    search_string.append('ENDT	 ')
    #replace_row.append('ENDT	 450\n')
    replace_row.append('ENDT	 250\n')

#search_string = 'P10: factor_GenT_latTowDamper='
#replace_row = 'P10: factor_GenT_latTowDamper=0; // // 0=not used, default is [2:0.1,5:0.1,7:0.05,9:0.05,11:0.1,13:0,15:0,17:0.05,19:0.05,21:0.05,23:0.05,25:0.05]\n'


#search_string = 'max_force_N=1.5e7;'
#replace_row = 'max_force_N=2e7;\n'


if isinstance(old_string, str):
    old_string = [old_string]
    new_string = [new_string]
if isinstance(search_string, str):
    search_string = [search_string]
    replace_row = [replace_row]

Utility().createFolderIfNotExcisting(out_folder)

infiles = []
outfiles = []
if Include_Childfolder:
    subfolders = [folder[0] for folder in os.walk(baseline_folder)]
    print('found folders ---> ', subfolders)

    for subfolder in subfolders:
        childfiles = Utility().return_run_files_in_folder(subfolder)
        if childfiles:
            print('found in folder ---> ', subfolder, ' the files --->', childfiles)
            new_sub_outfolder = os.path.join(out_folder, subfolder.split('\\')[-1])
            print('creating folder ---> ', new_sub_outfolder)
            Utility().createFolderIfNotExcisting(new_sub_outfolder)

            infiles.extend(childfiles)
            outfiles.extend(os.path.join(new_sub_outfolder, path.split('\\')[-1]) for path in childfiles)
            #outfiles.extend(os.path.join(new_sub_outfolder, path.split('\\')[-1].replace(old_string, new_string)) for path in childfiles)

else:
    #run_files = [path.split('\\')[-1] for path in Utility().return_run_files_in_folder(baseline_folder)]
    infiles.extend(Utility().return_run_files_in_folder(baseline_folder))
    outfiles.extend(os.path.join(out_folder, path.split('\\')[-1]) for path in infiles)
    #outfiles.extend(os.path.join(out_folder, path.split('\\')[-1].replace(old_string, new_string)) for path in infiles)


#for idx_file, run_file in enumerate(run_files):
#    infile = open(os.path.join(baseline_folder, run_file), "r")
#    outfileName = run_file.replace(old_string, new_string)
#    outfile = open(os.path.join(out_folder, outfileName), "w")
awareness_files = []
for infile, outfile in zip(infiles, outfiles):
    changed = False
    print('adapting: ', infile)
    run_file = infile.split('\\')[-1].split('.')[0]
    outfileName = outfile.split('\\')[-1].split('.')[0]
    for old_string_i, new_string_i in zip(old_string, new_string):
        if old_string_i in outfileName:
            new_outfileName = outfileName.replace(old_string_i, new_string_i)
            outfile = outfile.replace(outfileName, new_outfileName)
            outfileName = new_outfileName

    infile = open(infile, "r")
    outfile = open(outfile, "w")
    for row in infile:
        if row.find(run_file) != -1:
            row = '  <Name>' + outfileName + '</Name>\n'
            changed = True
        for old_string_i, new_string_i in zip(old_string, new_string):
            if row.find(old_string_i) != -1:
                row = row.replace(old_string_i, new_string_i)
                changed = True
        # if isinstance(search_string, str):
        #     if row.find(search_string) != -1:
        #             print('replacing', row, 'by', replace_row)
        #             row = replace_row
        #             changed = True
        # else:
        for search_string_i, replace_row_i in zip(search_string, replace_row):
            if row.find(search_string_i) != -1:
                print('replacing', row, 'by', replace_row_i)
                row = replace_row_i
                changed = True
        outfile.write(row)

    outfile.close()
    infile.close()

    if not changed:
        awareness_files.append(run_file)

if awareness_files:
    print('\n\nNote that these files have not been subjected to changes:', *awareness_files, sep='\n')
else:
    print('Note that all files have been changed.')






























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
