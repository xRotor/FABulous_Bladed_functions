from ANSFAB__Utility import Bladed

################################################### READ ME ############################################################
#   This script is supposed to use a Bladed baseline file ("slavefile"), where all turbine parameters are as desired,  #
#   and copy all mstarts, the wave-*.SEA-file etc., which specify the operation status, environmental and fault        #
#   conditions, of all files of a baseline folder ("childmainfolder") into a new Bladed project file in the "out_folder"
#   If needed, the run names of the childmainfolder can be adapted a "change_snip" and exchanged by the "new_snip".    #
#   This function should also work with sub-folders.                                                                   #
#         :param masterfile:      Bladed run files from which the simulated environment and conditions are taken       #
#         :param childmainfolder: (main) folder, that contains the masterfiles                                         #
#         :param slavefile:       Bladed run file, that possesses the desired turbine and control parameters           #
#         :param outmainfolder:   (main) folder in which the combined Bladed run files are stored                      #
#         :param change_snip:     String that is a part of the masterfile which should be changed                      #
#         :param new_snip:        String that should be replaced by change_snip                                        #
#         :param mstart_names:  Contains all "mstart" sections that should be copied from the masterfile in the new file
#         :return:                outfiles                                                                             #
########################################################################################################################



slavefile = r'H:\BladedWS\CheckTeeterAngleScaling\temp_DAT_test\Cart2_powerpro_init.$PJ'
childmainfolder= r'H:\BladedWS\BottomFixed\DLC_legacy\ExtremeDLCs_2B101teeter'
out_folder = r'H:\BladedWS\CheckTeeterAngleScaling\ULS_comp\CART2_ULS_v2'

slavefile = r'H:\BladedWS\BottomFixed\DLC_legacy\ExtremeDLCs_2B101v18teeter__baseline\2B101v18teeter_ex5xtremDamp__noTeeter_100idle_IAG.$PJ'
childmainfolder= r'H:\BladedWS\BottomFixed\DLC_legacy\ExtremeDLCs_2B101v15_ref\DLC61_2B101v15'
out_folder = r'H:\BladedWS\BottomFixed\DLC_legacy\ExtremeDLCs_2B101v18noTeeter_DLC61\DLC61_2B101v18noTeeter_100idle_IAG'

slavefile = r'H:\BladedWS\BottomFixed\DLC_legacy\ExtremeDLCs_2B101v18teeter__baseline\2B101v18teeter_ex5xtremDamp__00y_05mps__teeterBrake4rpm__IAG_stall__no_pitch_imbal.$PJ'
childmainfolder= r'H:\BladedWS\BottomFixed\DLC_legacy\DLC12\DLC12_2B101v15_ref__exZone5_flexDampers_6seeds_Kaimal'
out_folder = r'H:\BladedWS\BottomFixed\DLC_legacy\DLC12\DLC12_2B101v18teeter_ex5xtremDamp_6seeds_Kaimal__teeterBrake4rpm__IAG_noImbal'

slavefile = r'H:\BladedWS\CheckTeeterAngleScaling\temp_DAT_test\Cart2_powerpro_init.$PJ'
childmainfolder= r'H:\BladedWS\BottomFixed\DLC_legacy\ExtremeDLCs_2B101v15_ref'
out_folder = r'H:\BladedWS\CheckTeeterAngleScaling\ULS_comp\CART2_ULS_v3'

slavefile = r'H:\BladedWS\FOWTs\DLC_ULS\3B20Volt_v008_baseline\DLC6X__3B20Volt_v008_baseline\3B20Volt_v008_baseline_DLC63__40mps_p20y.$PJ'
childmainfolder= r'H:\BladedWS\FOWTs\DLC_ULS\3B20Volt_v008_baseline_IAG_stall_v2\DLC6X__3B20Volt_v008_baseline_IAG_stall'
out_folder = r'H:\BladedWS\FOWTs\DLC_ULS\3B20Volt_v008_baseline\DLC6X__3B20Volt_v008_baseline__82deg'

slavefile = r'H:\BladedWS\BottomFixed\DLC_legacy\2B101_v19_LIPC123P_bode_v1_exZone5_flexGains__light_teeter_blades_DLC1_2.$PJ'
childmainfolder= r'H:\BladedWS\BottomFixed\DLC_legacy\ExtremeDLCs_2B101v15_ref_IAG_stall'
out_folder = r'H:\BladedWS\BottomFixed\DLC_legacy\ExtremeDLCs_2B101v19_LIPC_light_blades'

slavefile = r'H:\BladedWS\FOWTs\DLC_ULS\2B20v18Volt_v009_baseline_IAG_stall__teeter_v4__teeterStopAt4rpm\2B20v18_fixed_hub_Volt_v009_DLC61__50mps_00y_IAG_stall2.$PJ'
childmainfolder= r'H:\BladedWS\FOWTs\DLC_ULS\2B20Volt_v009_baseline_IAG_stall_v2\DLC6X__2B20Volt_v009_baseline_IAG_stall__old__pitch88deg'
out_folder = r'H:\BladedWS\FOWTs\DLC_ULS\2B20v18Volt_v009_baseline_IAG_stall__teeter_v4__teeterStopAt4rpm\DLC6X__2B20v18_fixed_hub_20Volt_v009_baseline_IAG_stall__old__pitch88deg'


#slavefile = r'H:\BladedWS\BottomFixed\towerHzItr\2B101v15_Monopile_noDamp_optImbal_15mps.$PJ'
slavefile = r'H:\BladedWS\BottomFixed\towerHzItr\3B90_Monopile_noDamp_optImbal_15mps.$PJ'
#childmainfolder= r'H:\BladedWS\BottomFixed\DLC_legacy\ExtremeDLCs_2B101v15_ref_IAG_stall'
childmainfolder= r'H:\BladedWS\BottomFixed\DLC_legacy\ExtremeDLCs_3B_ref_IAG_stall'
#out_folder = r'H:\BladedWS\BottomFixed\DLC_legacy\ExtremeDLCs_2B101v15__Monopile_noDamp_or_Imbal'
out_folder = r'H:\BladedWS\BottomFixed\DLC_legacy\ExtremeDLCs_3B_Monopile_noDamp_optImbal_IAG_stall'




slavefile = r'H:\BladedWS\BottomFixed\DLC_legacy\2B101_all_IAE_Monopiles_DLC12_evalu\2B101v15_MonoIEA9m_ex0122_flexDamp_DLC12_Kaimal_00y_05mps_s105.$PJ'
childmainfolder= r'H:\BladedWS\BottomFixed\DLC_legacy\ExtremeDLCs_2B101v15_ref_IAG_stall'
out_folder = r'H:\BladedWS\BottomFixed\DLC_legacy\ExtremeDLCs_2B101v15_IEA9m_Monopile_DLCs'

slavefile = r'H:\BladedWS\BottomFixed\DLC_legacy\ExtremeDLCs_3B_Monopile_DLC12\DLC12_3B_MonoIEA9m_ex012_flexDamp_DLC12_Kaimal_00y_05mps_s105.$PJ'
childmainfolder= r'H:\BladedWS\BottomFixed\DLC_legacy\ExtremeDLCs_3B_ref_IAG_stall'
out_folder = r'H:\BladedWS\BottomFixed\DLC_legacy\ExtremeDLCs_3B_IEA9m_Monopile_DLCs'

slavefile = r'H:\BladedWS\BottomFixed\DLC_legacy\2B101_all_IAE_Monopiles_DLC12_evalu\2B101v15_MonoIEA9m_7modes_ex0122_flexFAnoStS_DLC12_Kaimal_00y_05mps_s105.$PJ'
#slavefile = r'H:\BladedWS\BottomFixed\DLC_legacy\2B101_all_IAE_Monopiles_DLC12_evalu\DLC12_3B_MonoIEA9m_ex012_flexFA_noStS_Damp_DLC12_Kaimal_00y_05mps_s105.$PJ'
childmainfolder= r'H:\BladedWS\BottomFixed\DLC_legacy\ExtremeDLCs_2B101v15_ref_IAG_stall\DLC12_2B101v15_exZ5_flexDamp__new_kaimal'
#childmainfolder= r'H:\BladedWS\BottomFixed\DLC_legacy\ExtremeDLCs_3B_ref_IAG_stall\DLC12_3B_ref_legacy_ex5_flexDamp__new_Kaimal'
#childmainfolder= r'H:\BladedWS\BottomFixed\DLC_legacy\DLC12\DLC12_3B90_EERA_ref_exZone5_flexDampers_6seeds'
#childmainfolder= r'H:\BladedWS\BottomFixed\DLC_legacy\DLC12\DLC12_2B101v15_ref__exZone5_flexDampers_6seeds'
out_folder = r'H:\BladedWS\BottomFixed\DLC_legacy\2B101_all_IAE_Monopiles_DLC12_evalu\DLC12_2B101v15_MonoIEA9m_7modes_ex0122_flexFAnoStS__kaimal'
#out_folder = r'H:\BladedWS\BottomFixed\DLC_legacy\ExtremeDLCs_3B_Monopile_DLC12\DLC12_3B_MonoIAE9m_ex012_flexFA_noStS__new_Kaimal'
# main script:


slavefile = r'H:\BladedWS\BottomFixed\DLC_legacy\temptemptemp_test_ListParams\2B101v19_LIPC_lightBlades_DLC12_Kaimal_00y_13mps_s113_ref_test3.$PJ'
childmainfolder= r'H:\BladedWS\BottomFixed\DLC_legacy\ExtremeDLCs_2B101v19_LIPC_bode_v1_light_blades__IAG_stall\DLC12_2B101v19_LIPC_lightBlades_6seeds__new_Kaimal2'
out_folder = r'H:\BladedWS\BottomFixed\DLC_legacy\ExtremeDLCs_2B101v19_LIPC_bode_v1_light_blades__IAG_stall\DLC12_2B101v19_LIPC123_new_DISCON_6seeds__new_Kaimal'

slavefile = r'H:\BladedWS\BottomFixed\DLC_legacy\2B101ref_IAE_Monopiles\baseline_file2\2B101v15_MonoIEA9m_7mod_ex0122_flexDamp_DLC12_Kaimal_00y_13mps_s513.$PJ'
childmainfolder= r'H:\BladedWS\BottomFixed\DLC_legacy\ExtremeDLCs_2B101v15_ref_IAG_stall\DLC13_2B101v15_ref_Kaimal_short_time_series_IAG_stall'
out_folder = r'H:\BladedWS\BottomFixed\DLC_legacy\2B101ref_IAE_Monopiles\DLC13_2B101v15ref_MonoIEA_Kaimal_IAG_stall'

slavefile = r'H:\BladedWS\BottomFixed\DLC_legacy\ExtremeDLCs_2B101v15_ref_IAG_stall\DLC12_2B101v15_exZ5_LookUpTableDamp__new_kaimal\2B101v15_ref_ex5_LookUpTableDamp_DLC12_Kaimal_00y_19mps_s119_newInitPitch.$PJ'
childmainfolder= r'H:\BladedWS\BottomFixed\DLC_legacy\ExtremeDLCs_2B101v15_ref_IAG_stall\DLC12_2B101v15_exZ5_flexDamp__new_kaimal'
out_folder = r'H:\BladedWS\BottomFixed\DLC_legacy\ExtremeDLCs_2B101v15_ref_IAG_stall\DLC12_2B101v15_exZ5_UserLookUpTableDamp__new_kaimal_new_initPitch'

slavefile = r'H:\BladedWS\BottomFixed\DLC_legacy\ExtremeDLCs_3B_ref_IAG_stall\powprod.$PJ'
childmainfolder= r'H:\BladedWS\BottomFixed\DLC_legacy\3Bref_IEA_Monopile\DLC62_3B_MonoIEA_parkedI91d_Edgewise2xDamped_Kaimal_IAG_stall'
out_folder = r'H:\BladedWS\BottomFixed\DLC_legacy\ExtremeDLCs_2B101v15_ref_IAG_stall_new_DISCON\DLC62_3B_ref_parkedI91d_Edgewise2xDamped_Kaimal_IAG_stall2'

outfiles = Bladed().automized_bulk_mstarts_in_files_changer(masterfile='', childmainfolder=childmainfolder, slavefile=slavefile,
                                      outmainfolder=out_folder, change_snip='3B_MonoIEA_', new_snip='3B_ref_')
                                      #outmainfolder=out_folder, change_snip='_LIPC_lightBlades_', new_snip='_LIPC123_new_DISCON_')
                                      #outmainfolder=out_folder, change_snip='ref_ex5_flexDamp', new_snip='MonoIEA9m_7mod_ex012_noDamp')
                                      #outmainfolder=out_folder, change_snip='_ref_legacy_', new_snip='_MonoIEA9m_')
                                      #outmainfolder=out_folder, change_snip='v15_ref_ex5_flexDamp', new_snip='v15_MonoSGREwTP_noEx_noDamp')

                                      #outmainfolder=out_folder, change_snip='_ref_', new_snip='_MonopSGRE_')
                                      # outmainfolder=out_folder, change_snip='_ref_legacy_', new_snip='_MonopSGRE_')
                                      # outmainfolder=out_folder, change_snip='_ref_noExZ5_noDamp_', new_snip='_Monop11m_noExZ5_flexDamp_')
                                      #outmainfolder=out_folder, change_snip='2B101v15_ref', new_snip='2B101v15_Monop_noDampImbal')
                                      #outmainfolder=out_folder, change_snip='2B101v15_ref_ex5_flexDamp', new_snip='2B101v18teeter_ex5x_brk4rpm_IAG_noImbal')
                                      #outmainfolder=out_folder, change_snip='2B101v15_ref_82idle', new_snip='2B101v18noTeeter_100idle_IAG')
                                      #outmainfolder=out_folder, change_snip='3B90_exZ5_flexGains', new_snip='2B101v15_exZ5_flexG')
                                      #outmainfolder=out_folder, change_snip='EERA_ref', new_snip='bladeSpanLoads')
                                      #outmainfolder=out_folder, change_snip='2B101v15', new_snip='2B101teeter')



