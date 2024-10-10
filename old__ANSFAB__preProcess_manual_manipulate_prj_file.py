import numpy as np
import glob
import os
import csv
from datetime import datetime
import shutil
from shutil import copyfile
#from ANSFAB___Customize_GA import PrintDetails, fileEnd, MainPathToBladedRuns, searchWords, \
#    ListOfBaselineFiles, baselineFolder, addToRunFileNames, nSeeds, nParams, nPopulation


ListOfBaselineOldFiles = [r"2B101yawCon13mps121.$PJ", r"2B101yawCon13mps264.$PJ", r"2B101yawCon13mps473.$PJ", r"2B101yawCon13mps551.$PJ", r"2B101yawCon13mps627.$PJ", r"2B101yawCon13mps961.$PJ"]
ListOfBaselineNewFiles = [r"2B101yawCon11mps121.$PJ", r"2B101yawCon11mps264.$PJ", r"2B101yawCon11mps473.$PJ", r"2B101yawCon11mps551.$PJ", r"2B101yawCon11mps627.$PJ", r"2B101yawCon11mps961.$PJ"]

ListOfBaselineOldFiles = [r"2B101v17_yawContr_noDamp_11mps_s121.$PJ", r"2B101v17_yawContr_noDamp_11mps_s264.$PJ", r"2B101v17_yawContr_noDamp_11mps_s473.$PJ", r"2B101v17_yawContr_noDamp_11mps_s551.$PJ", r"2B101v17_yawContr_noDamp_11mps_s627.$PJ", r"2B101v17_yawContr_noDamp_11mps_s961.$PJ"]
ListOfBaselineNewFiles = [r"2B101v20_yawContr_noDamp_11mps_s121.$PJ", r"2B101v20_yawContr_noDamp_11mps_s264.$PJ", r"2B101v20_yawContr_noDamp_11mps_s473.$PJ", r"2B101v20_yawContr_noDamp_11mps_s551.$PJ", r"2B101v20_yawContr_noDamp_11mps_s627.$PJ", r"2B101v20_yawContr_noDamp_11mps_s961.$PJ"]

ListOfBaselineFiles = [r'2B20Volt_v009_1_15mps.$PJ']

ChangeDicts = []
# ChangeDicts.append({'WORD': 'INIMD', 'EXCHANGE': 'INIMD	 0.0'}) # .85'})
# ChangeDicts.append({'WORD': 'ENDT	 ', 'EXCHANGE': 'ENDT	 320'})

ChangeDicts.append({'WORD': r'P11: factor_Pitch_FATowDamper=', 'EXCHANGE': r'P11: factor_Pitch_FATowDamper='}) # .85'})
ChangeDicts.append({'WORD': r'P24: GA_Parameter11=', 'EXCHANGE': r'P24: GA_Parameter11='}) # .85'})

ChangeValues = [i/100 for i in range(0, 11, 1)]
ChangeValues


folder = r'D:\GeneticAlgorithm_Bladed_tuning\baselineFiles_temp_run_folder_save\\'
folder = r'G:\DLC12_runs\2B101_v20_DD_OF_yaw_controlled_noPitch_noDamp_DLC1_2\\'
folder = r'H:\BladedWS\FOWTs\iterTowerDamp\\'


fileEnd = '.$PJ'  # '.prj'



# print('# -------- copying ' + ListOfBaselineOldFiles + '-files ---------- #')
# for idx, oldfile in enumerate(ListOfBaselineOldFiles):
#     shutil.copyfile(os.path.join(folder, oldfile), os.path.join(folder, ListOfBaselineNewFiles[idx]))

print('# -------- starting to manipulate ' + str(ListOfBaselineFiles[:]) + '-files ---------- #')

# for idx, fileName in enumerate(ListOfBaselineNewFiles):
for idx, fileName in enumerate(ListOfBaselineFiles):
    for value in ChangeValues:
        NameAdd = '_itr_FA_G' + str('%.02f' % value).replace('.', '_')  # '.prj'

        # infileName = ListOfBaselineOldFiles[idx].replace(fileEnd, '')
        # outfileName = fileName.replace(fileEnd, '')
        infileName = fileName.replace(fileEnd, '')
        outfileName = fileName.replace(fileEnd, '') + NameAdd

        print('new filename is: ' + outfileName + ' with length ' + str(len(outfileName)))

        infile  = open((folder + infileName + '.$PJ'), "r")
        outfile = open((folder + outfileName+ '.$PJ'), "w")

        for row in infile:
            if row.find(infileName) != -1:
                row = '  <Name>' + outfileName + '</Name>\n'
                # print('FOUND RUN NAME!!!')
            # elif newWindSpeed > 0:
            #     if row.find(baselinewindpath) != -1:
            #         row = baselinewindpath + str(newWindSpeed) + row[len(baselinewindpath) + 2:-1] + '\n'
            #     elif row.find('UBAR	 ') != -1:
            #         row = 'UBAR	 ' + str(newWindSpeed) + '\n'

            for idx2, Dict in enumerate(ChangeDicts):
                if row.find(Dict.get('WORD')) != -1:
                    print('was: ' + row)
                    row = Dict.get('EXCHANGE') + str(value) + ';' + '\n'
                    print('is now: ' + row)
            outfile.write(row)


        outfile.close()
        infile.close()

            # shutil.copy(outfolder + outfileName, folder + outfileName)  # Just for documentary









# newWindSpeed = 0  # m/s of new files (for turbulence index); USE 0 TO NOT CHANGE IT
#
#
# baselinewindpath = r'WINDF	f:\dlc12windfilenew2_from5to25\ntm_'
# if newWindSpeed == 11:
#     ChangeDicts.append({'WORD': 'TI	 ', 'EXCHANGE': 'TI	 .1510909'})
#     ChangeDicts.append({'WORD': 'TI_V	 ', 'EXCHANGE': 'TI_V	 .1208727'})
#     ChangeDicts.append({'WORD': 'TI_W	 ', 'EXCHANGE': 'TI_W	 7.554545E-02'})
# elif newWindSpeed == 13:
#     ChangeDicts.append({'WORD': 'TI	 ', 'EXCHANGE': 'TI	 .1416923'})
#     ChangeDicts.append({'WORD': 'TI_V	 ', 'EXCHANGE': 'TI_V	 .1133538'})
#     ChangeDicts.append({'WORD': 'TI_W	 ', 'EXCHANGE': 'TI_W	 7.084616E-02'})
# elif newWindSpeed == 15:
#     ChangeDicts.append({'WORD': 'TI	 ', 'EXCHANGE': 'TI	 .1348'})
#     ChangeDicts.append({'WORD': 'TI_V	 ', 'EXCHANGE': 'TI_V	 .10784'})
#     ChangeDicts.append({'WORD': 'TI_W	 ', 'EXCHANGE': 'TI_W	 .0674'})
# elif newWindSpeed == 17:
#     ChangeDicts.append({'WORD': 'TI	 ', 'EXCHANGE': 'TI	 .1295294'})
#     ChangeDicts.append({'WORD': 'TI_V	 ', 'EXCHANGE': 'TI_V	 .1036235'})
#     ChangeDicts.append({'WORD': 'TI_W	 ', 'EXCHANGE': 'TI_W	 6.476471E-02'})
#
#
# autochange_hole_folder = r'G:\DLC12_runs\2B101_v20_DD_OF_yaw_controlled_noPitch_StS_Damp_by_genT_DLC1_2\\'
# outfolder = r'G:\DLC12_runs\\'
# if autochange_hole_folder:
#     fileList = glob.glob(autochange_hole_folder + '*' + fileEnd)  # + '*.$PJ')
#
#     for file in fileList:
#         if file.find('13mps') != -1:
#             ChangeValue = '0.6'
#         elif file.find('15mps') != -1:
#             ChangeValue = '0.85'
#         elif file.find('17mps') != -1:
#             ChangeValue = '1.0'
#         elif file.find('19mps') != -1:
#             ChangeValue = '1.09'
#         elif file.find('21mps') != -1:
#             ChangeValue = '1.15'
#         elif file.find('23mps') != -1:
#             ChangeValue = '1.2'
#         elif file.find('25mps') != -1:
#             ChangeValue = '1.22'
#         else:
#             ChangeValue = '0'
#
#         ChangeDicts = [{'WORD': 'INIMD', 'EXCHANGE': 'INIMD	 ' + ChangeValue}]
#
#         outfile = '\\'.join(file.split('\\')[:-2])+'\\'+file.split('\\')[-1]  # only gets rid of the first parent folder
#
#         infile  = open(file, "r")
#         outfile = open(outfile, "w")
#
#         for row in infile:
#             for idx2, Dict in enumerate(ChangeDicts):
#                 if row.find(Dict.get('WORD')) != -1:
#                     print('was: ' + row)
#                     row = Dict.get('EXCHANGE') + '\n'
#                     print('is now: ' + row)
#             outfile.write(row)
#
#         outfile.close()
#         infile.close()
#
# else:














