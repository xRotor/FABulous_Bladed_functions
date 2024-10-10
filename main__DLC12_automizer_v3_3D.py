from ANSFAB__Utility import Utility
from ANSFAB__Utility import Bladed


folder = r'H:\BladedWS\FOWTs\Best_of_BruteForce_full_time_series'
out_folder = r'H:\BladedWS\FOWTs\DLC12\2B20Volt_v009_FA_damper_v0'
baseline_file = '2b20volt_v009_1_15mps_g0_FA_damper_full_TS'
change_string = '_1_15mps_g0_FA_damper_full_TS'

folder = r'H:\BladedWS\FOWTs\BruteOptimize_3B20Volt_v008'
out_folder = r'H:\BladedWS\FOWTs\BruteOptimize_3B20Volt_v008\baselinefile_FA_damp__multiple_windspeeds'
baseline_file = '3B20Volt_v008_15mps_FA'
change_string = '_15mps_FA'

folder = r'H:\BladedWS\FOWTs\DLC12'
out_folder = r'H:\BladedWS\FOWTs\DLC12\3B20Volt_v008__TI_iter'
out_folder = r'H:\BladedWS\FOWTs\DLC12\2B20Volt_v009_1__TI_iter'
baseline_file = '3B20Volt_v008_15mps_full_TS'
baseline_file = '2B20Volt_v009_1_15mps_full_TS'
change_string = '1_15mps_full_TS'

folder = r'H:\BladedWS\BottomFixed\towerHzItr'
out_folder = r'H:\BladedWS\BottomFixed\towerHzItr\3B_SE_DLC12__wind_shear_iter'
#out_folder = r'H:\BladedWS\BottomFixed\towerHzItr\2B101v15_SE_DLC12__wind_shear_iter'
baseline_file = '3B_ref_ex5_flexDamp_15mps'
#baseline_file = '2B101v15_ex5_flexDamp_15mps'
change_string = '_15mps'

folder = r'H:\BladedWS\BottomFixed\shear_and_TI_ref_iterations'
out_folder = r'H:\BladedWS\BottomFixed\shear_and_TI_ref_iterations\3B_SE_DLC12__TI_ref_and_wind_shear_iter'
out_folder = r'H:\BladedWS\BottomFixed\shear_and_TI_ref_iterations\2B101v15_SE_DLC12__TI_ref_and_wind_shear_iter'
baseline_file = '3B_ref_ex5_fG_optImbal_15mps'
baseline_file = '2B101v15_ref_ex5_fG_optImbal_15mps'
#baseline_file = '2B101v15_ex5_flexDamp_15mps'
change_string = '_15mps'

#baseline_file = '3B20Volt_v008_15mps'
#change_string = '_15mps'

# main script:
for turb_iter_variable in range(2, 19, 2):  # range(2, 13, 2):
    for shear_iter_variable in range(0, 21, 2):
        ListOfChangeDicts = Bladed().change_dict_for_DLC12_iterations(wind_shear=turb_iter_variable / 100, ref_turbulence_intensity=shear_iter_variable/100, change_wave_files=False)
        Utility().createFolderIfNotExcisting(out_folder)
        outfileNames = []
        for idx, ChangeDicts in enumerate(ListOfChangeDicts):
            #ChangeNameDicts = [{'WORD': change_string, 'EXCHANGE': '__TI%02i' % iter_varaible + '_%02d' % int(5+idx*2) + 'mps'}]
            #ChangeNameDicts = [{'WORD': change_string, 'EXCHANGE': '__shear0_%02i' % iter_varaible + '__%02d' % int(5+idx*2) + 'mps'}]
            ChangeNameDicts = [{'WORD': change_string, 'EXCHANGE': '__TI0_%02i' % turb_iter_variable + '_shear0_%02i' % shear_iter_variable + '__%02d' % int(5+idx*2) + 'mps'}]
            outfileName, out_folder = Utility().manipulatePRJfiles(ListOfBaselineFiles_local=[baseline_file], infolder=folder,
                                                outfolder=out_folder, ChangeDicts=ChangeDicts, ChangeNameDicts=ChangeNameDicts)
            outfileNames.append(outfileName[0])

        print('prepared runs: ', outfileNames)
#Bladed().AutoRunBatch(out_folder, outfileNames)
