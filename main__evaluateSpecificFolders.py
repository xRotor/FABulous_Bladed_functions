import ANSFAB__evaluateSpecificFolders
import ANSFAB__evaluateSpecificFolders_for_ULS
import ANSFAB__evaluateSpecificFolders_for_FLS
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





folderPlusFirstSnips = [r'H:\BladedWS\BottomFixed\DLC_legacy\2B101ref_IEA_Monopile_new_v2_10min_TS\DLC12_2B101v15MonoIEA_exZ5_flexDamp__new_kaimal_10min_TS_v2\\']

for folderPlusFirstSnip in folderPlusFirstSnips:
    print('\n \n \n evaluating ', folderPlusFirstSnip, '\n \n \n')
    #Documentation, Docu_keys, ListOfBladedJobs, documentation_path = ANSFAB__evaluateSpecificFolders.evaluateFolder(folderPlusFirstSnip, use_hub_fixed_blade_coordinate_system=True)
    #Documentation, ListOfBladedJobs, documentation_path = ANSFAB__evaluateSpecificFolders_for_ULS.evaluateFolder_for_ULS(folderPlusFirstSnip)
    Documentation, ListOfBladedJobs, documentation_path = ANSFAB__evaluateSpecificFolders_for_FLS.evaluateFolder_for_ULS_or_FLS(folderPlusFirstSnip, search_kind='FLS', prefilter_ULS_folders=False)  # search_kinds: FLS or ULS
    #Documentation, Docu_keys, ListOfBladedJobs, documentation_path = ANSFAB__evaluateSpecificFolders_for_DEL_along_blades.evaluateFolder_for_DEL_along_blades(folderPlusFirstSnip, calc_out_and_inplane_blade_DELs=True)  # check minus from pitch angle!!

