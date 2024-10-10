import os
import ANSFAB__evaluateSpecificFolders_for_FLS
from ANSFAB__Utility import Utility
import ANSFAB__evaluateSpecificFolders_for_DEL_along_blades

################################################### READ ME ############################################################
#   This script starts the post-processing of Bladed run files. It searches for all executed runs in the specified
#   run folder including the sub folders "folderPlusFirstSnips". It is also possible to add a list of folders add
#   the first part of the runs in the run folder of a specific group by simply adding it to the path. The path should
#   end with a double backslash "\\" if just a folder is specified. 3 types of post-processing can be in/out commented:
#       1. An IEC conform evaluation of fatigue loads (of DLC 1.2)
#       2. An IEC conform evaluation of ULS
#       3. An evaluation of fatigue loads along the blades
########################################################################################################################

folderPlusFirstSnips = [r'H:\BladedWS\BottomFixed\DLC_legacy\temptemptemp_test_shorterNames_test\\']
mainfolder = r'H:\BladedWS\BottomFixed\DLC_legacy\\'

folderPlusFirstSnips = []

for subfolder in os.walk(mainfolder):
    if 'DLC12' in subfolder[0].split('\\')[-1]:
        if Utility().return_run_files_in_folder(subfolder[0]):
            folderPlusFirstSnips.append(subfolder[0] + '\\')

print('found specific', len(folderPlusFirstSnips) ,'folders ---> ', folderPlusFirstSnips)




for folderPlusFirstSnip in folderPlusFirstSnips:
    print('\n \n \n evaluating ', folderPlusFirstSnip, '\n \n \n')
    Documentation, ListOfBladedJobs, documentation_path = ANSFAB__evaluateSpecificFolders_for_FLS.evaluateFolder_for_ULS_or_FLS(folderPlusFirstSnip, search_kind='FLS')  # search_kinds: FLS or ULS

