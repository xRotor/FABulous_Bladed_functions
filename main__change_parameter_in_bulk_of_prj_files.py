from ANSFAB__Utility import Utility
import numpy as np
from ANSFAB__Utility import Bladed


baseline_folder = r'H:\BladedWS\BottomFixed\exZoneTuning\2B101v15_exZone5_hz_itr_basefiles'
baseline_folder = r'H:\BladedWS\BottomFixed\DLC_legacy\NTM_windfiles_5to25mps'
baseline_folder = r'H:\BladedWS\FOWTs\DLC_ULS\DLC6X_idling_pitch_iteration\DLC6X__2B20Volt_v009_idling_pitch_itr_basefolder'
baseline_folder = r'H:\BladedWS\BottomFixed\DLC_legacy\DLC61__idling_pitch_iteration\3B_ref_IAG_stall__DLC61_idling_pitch_itr_baseline'
baseline_folder = r'H:\BladedWS\BottomFixed\DLC_legacy\ExtremeDLCs_3B_ref_IAG_stall\DLC62_3B_ref_legacy_parkedI91d_Edgewise2xDamped_Kaimal_IAG_stall'
baseline_folder = r'H:\BladedWS\CheckTeeterAngleScaling\decay_tests\PTC_decay\AzimuthIterations\CART2_PTC1_decay_10mps_p20mps_shear__itr'
baseline_folder = r'H:\BladedWS\CheckTeeterAngleScaling\DLC15\CART2_no_imbal_tilt_gravity__v3_EWS_for_2B6__PTC_PTVC_tuning'
baseline_folder = r'H:\BladedWS\CheckTeeterAngleScaling\DLC15\2B101v17_no_imbal_tilt_gravity_v3_EWS_for_2B6__but66s__PTC_PTVC_tuning'
baseline_folder = r'H:\BladedWS\BottomFixed\DLC_legacy\ExtremeDLCs_2B101v15__Monopile_DLC12\DLC12_2B101v19_MonoSGRE_LIPC_FA_damper_gain_iteration'
baseline_folder = r'H:\BladedWS\BottomFixed\DLC_legacy\2B101_all_IEA_Monopiles_DLC12_evalu\new\zz_DLC12_3B_MonoIEA9m_7modes_FA_damp_itr'
# out_folder = r'H:\BladedWS\BottomFixed\exZoneTuning\2B101v15_exZone5_hz_itr'
# out_folder = r'H:\BladedWS\FOWTs\DLC_ULS\3B20Volt_v008_baseline_IAG_stall_v2\DLC62__3B20Volt_v008_parkedI_blade4xDamped_IAG_stall_Kaimal'
baselinefiles_folder = baseline_folder + r'\baselinefiles'
out_folder = baseline_folder + r'\itrFA_6seeds'

baseline_files = [path.split('\\')[-1] for path in Utility().return_run_files_in_folder(baselinefiles_folder)]
# baseline_files = [r'2B101v17_noImbal_or_gravity_DLC15_2BE_66s_25mps_PTVC1_0']


# for itr_variable in np.linspace(0.16,0.175,16):
# for itr_variable in range(80, 101, 1):
#for itr_variable in range(60, 102, 4):
#for itr_variable in np.linspace(0.20, 0.25, 10):
#for itr_variable in np.linspace(1.05, 1.35, 30):
#for itr_variable in np.linspace(0.0, 0.2, 21):
# for itr_variable in np.linspace(0, 0.1, 41):
for itr_variable in np.linspace(0, 0.4, 21):
#for itr_variable in range(0, 190, 10):
    ChangeDicts = []
    #ChangeDicts.append({'WORD': r'P12: towerFrequencyToAvoid=', 'EXCHANGE': r'P12: towerFrequencyToAvoid=%.3f' % itr_variable})
    #ChangeDicts.append({'WORD': r'IDLEPITCH	 ', 'EXCHANGE': r'IDLEPITCH	 %.14f' % (itr_variable*np.pi/180)})
    #ChangeDicts.append({'WORD': r'INIMD	 0', 'EXCHANGE': r'INIMD	 %.14f' % (itr_variable*np.pi/180)})
    #ChangeDicts.append({'WORD': r'INAZI	 0', 'EXCHANGE': r'INAZI	 %.14f' % (itr_variable*np.pi/180)})
    #ChangeDicts.append({'WORD': r'P2: pitchTeeterVeloCouplGain=0.18116;', 'EXCHANGE': r'P2: pitchTeeterVeloCouplGain=%.6f;' % (itr_variable)})
    # ChangeDicts.append({'WORD': r'P2: pitchTeeterVeloCouplGain=1;', 'EXCHANGE': r'P2: pitchTeeterVeloCouplGain=%.6f;' % (itr_variable)})
    #ChangeDicts.append({'WORD': r'P11: factor_Pitch_FATowDamper=', 'EXCHANGE': r'P11: factor_Pitch_FATowDamper=0;'})
    #ChangeDicts.append({'WORD': r'factor_GenT_latTowDamper=', 'EXCHANGE': r'factor_GenT_latTowDamper=%.6f;' % (itr_variable)})
    ChangeDicts.append({'WORD': r'P11: factor_Pitch_FATowDamper=', 'EXCHANGE': r'P11: factor_Pitch_FATowDamper=%.6f;' % (itr_variable)})

    #ChangeNameDicts = [{'WORD': 'itr', 'EXCHANGE': 'itr_Hz' + ('%.3f' % itr_variable).replace('.','_') + '_'}]
    #ChangeNameDicts = [{'WORD': 'itr', 'EXCHANGE': 'idl_pit' + ('%.0f' % itr_variable).replace('.','_')+'d'}]
    #ChangeNameDicts = [{'WORD': '_Kaimal_50mps_00y_IAG_stall', 'EXCHANGE': '_50mps_y' + ('%03.0f' % itr_variable).replace('.','_')+'d'}]
    #ChangeNameDicts = [{'WORD': '_itr', 'EXCHANGE': '_yaw' + ('%03.0f' % itr_variable).replace('.','_')+'d'}]
    #ChangeNameDicts = [{'WORD': '_itr', 'EXCHANGE': '_azi' + ('%03.0f' % itr_variable).replace('.', '_')+'d'}]
    #ChangeNameDicts = [{'WORD': '_itr', 'EXCHANGE': '_PTVC' + ('%0.4f' % itr_variable).replace('.', '_')}]
    ChangeNameDicts = [{'WORD': '_FA_gain', 'EXCHANGE': '_FA_gain' + ('%0.4f' % itr_variable).replace('.', '_')}]
    # ChangeDicts.append({'WORD': '', 'EXCHANGE': ''})

    print(ChangeDicts[0]['EXCHANGE'])
    print(ChangeNameDicts[0]['EXCHANGE'])

    for baseline_file in baseline_files:

        outfileName, out_folder = Utility().manipulatePRJfiles(ListOfBaselineFiles_local=[baseline_file], infolder=baselinefiles_folder,
                                            outfolder=out_folder, ChangeDicts=ChangeDicts, ChangeNameDicts=ChangeNameDicts)
        print(outfileName)




















# # old:
#
# baseline_files = [r'2B101v15_MonoSGRE_Kaimal05mps_s105_FA_gain',  r'2B101v15_MonoSGRE_Kaimal07mps_s107_FA_gain',  r'2B101v15_MonoSGRE_Kaimal09mps_s109_FA_gain',  r'2B101v15_MonoSGRE_Kaimal11mps_s111_FA_gain',  r'2B101v15_MonoSGRE_Kaimal13mps_s113_FA_gain',
#                    r'2B101v15_MonoSGRE_Kaimal15mps_s115_FA_gain',  r'2B101v15_MonoSGRE_Kaimal17mps_s117_FA_gain', r'2B101v15_MonoSGRE_Kaimal19mps_s119_FA_gain',  r'2B101v15_MonoSGRE_Kaimal21mps_s121_FA_gain', r'2B101v15_MonoSGRE_Kaimal23mps_s123_FA_gain',
#                   r'2B101v15_MonoSGRE_Kaimal25mps_s125_FA_gain']
#
# baseline_files = [r'2B101v19_MonoSGRE_teeter_Kaimal05mps_s105_FA_gain',  r'2B101v19_MonoSGRE_teeter_Kaimal07mps_s107_FA_gain',  r'2B101v19_MonoSGRE_teeter_Kaimal09mps_s109_FA_gain',  r'2B101v19_MonoSGRE_teeter_Kaimal11mps_s111_FA_gain',  r'2B101v19_MonoSGRE_teeter_Kaimal13mps_s113_FA_gain',
#                    r'2B101v19_MonoSGRE_teeter_Kaimal15mps_s115_FA_gain',  r'2B101v19_MonoSGRE_teeter_Kaimal17mps_s117_FA_gain', r'2B101v19_MonoSGRE_teeter_Kaimal19mps_s119_FA_gain',  r'2B101v19_MonoSGRE_teeter_Kaimal21mps_s121_FA_gain', r'2B101v19_MonoSGRE_teeter_Kaimal23mps_s123_FA_gain',
#                   r'2B101v19_MonoSGRE_teeter_Kaimal25mps_s125_FA_gain']
#
# baseline_files = [r'2B101v19_MonoSGRE_LIPC_Kaimal05mps_s105_FA_gain',  r'2B101v19_MonoSGRE_LIPC_Kaimal07mps_s107_FA_gain',  r'2B101v19_MonoSGRE_LIPC_Kaimal09mps_s109_FA_gain',  r'2B101v19_MonoSGRE_LIPC_Kaimal11mps_s111_FA_gain',  r'2B101v19_MonoSGRE_LIPC_Kaimal13mps_s113_FA_gain',
#                    r'2B101v19_MonoSGRE_LIPC_Kaimal15mps_s115_FA_gain',  r'2B101v19_MonoSGRE_LIPC_Kaimal17mps_s117_FA_gain', r'2B101v19_MonoSGRE_LIPC_Kaimal19mps_s119_FA_gain',  r'2B101v19_MonoSGRE_LIPC_Kaimal21mps_s121_FA_gain', r'2B101v19_MonoSGRE_LIPC_Kaimal23mps_s123_FA_gain',
#                   r'2B101v19_MonoSGRE_LIPC_Kaimal25mps_s125_FA_gain']
#
# baseline_files = [r'3B_MonoSGRE_Kaimal05mps_s105_FA_gain',  r'3B_MonoSGRE_Kaimal07mps_s107_FA_gain',  r'3B_MonoSGRE_Kaimal09mps_s109_FA_gain',  r'3B_MonoSGRE_Kaimal11mps_s111_FA_gain',  r'3B_MonoSGRE_Kaimal13mps_s113_FA_gain',
#                    r'3B_MonoSGRE_Kaimal15mps_s115_FA_gain',  r'3B_MonoSGRE_Kaimal17mps_s117_FA_gain', r'3B_MonoSGRE_Kaimal19mps_s119_FA_gain',  r'3B_MonoSGRE_Kaimal21mps_s121_FA_gain', r'3B_MonoSGRE_Kaimal23mps_s123_FA_gain',
#                   r'3B_MonoSGRE_Kaimal25mps_s125_FA_gain']
#
# baseline_files = [r'2B101v15_MonoIEA9m_7modes_Kaimal05mps_s105_FA_gain',  r'2B101v15_MonoIEA9m_7modes_Kaimal07mps_s107_FA_gain',  r'2B101v15_MonoIEA9m_7modes_Kaimal09mps_s109_FA_gain',  r'2B101v15_MonoIEA9m_7modes_Kaimal11mps_s111_FA_gain',  r'2B101v15_MonoIEA9m_7modes_Kaimal13mps_s113_FA_gain',
#                    r'2B101v15_MonoIEA9m_7modes_Kaimal15mps_s115_FA_gain',  r'2B101v15_MonoIEA9m_7modes_Kaimal17mps_s117_FA_gain', r'2B101v15_MonoIEA9m_7modes_Kaimal19mps_s119_FA_gain',  r'2B101v15_MonoIEA9m_7modes_Kaimal21mps_s121_FA_gain', r'2B101v15_MonoIEA9m_7modes_Kaimal23mps_s123_FA_gain',
#                   r'2B101v15_MonoIEA9m_7modes_Kaimal25mps_s125_FA_gain']
#
# baseline_files = [r'3B_MonoIEA9m_7mod_Kaimal05mps_s105_FA_gain',  r'3B_MonoIEA9m_7mod_Kaimal07mps_s107_FA_gain',  r'3B_MonoIEA9m_7mod_Kaimal09mps_s109_FA_gain',  r'3B_MonoIEA9m_7mod_Kaimal11mps_s111_FA_gain',  r'3B_MonoIEA9m_7mod_Kaimal13mps_s113_FA_gain',
#                    r'3B_MonoIEA9m_7mod_Kaimal15mps_s115_FA_gain',  r'3B_MonoIEA9m_7mod_Kaimal17mps_s117_FA_gain', r'3B_MonoIEA9m_7mod_Kaimal19mps_s119_FA_gain',  r'3B_MonoIEA9m_7mod_Kaimal21mps_s121_FA_gain', r'3B_MonoIEA9m_7mod_Kaimal23mps_s123_FA_gain',
#                   r'3B_MonoIEA9m_7mod_Kaimal25mps_s125_FA_gain']
#
# baseline_files = [r'2B101v19_MonoIEA9m_7mod_LIPC_Kaimal05mps_s105_FA_gain',  r'2B101v19_MonoIEA9m_7mod_LIPC_Kaimal07mps_s107_FA_gain',  r'2B101v19_MonoIEA9m_7mod_LIPC_Kaimal09mps_s109_FA_gain',  r'2B101v19_MonoIEA9m_7mod_LIPC_Kaimal11mps_s111_FA_gain',  r'2B101v19_MonoIEA9m_7mod_LIPC_Kaimal13mps_s113_FA_gain',
#                   r'2B101v19_MonoIEA9m_7mod_LIPC_Kaimal15mps_s115_FA_gain',  r'2B101v19_MonoIEA9m_7mod_LIPC_Kaimal17mps_s117_FA_gain',  r'2B101v19_MonoIEA9m_7mod_LIPC_Kaimal19mps_s119_FA_gain',  r'2B101v19_MonoIEA9m_7mod_LIPC_Kaimal21mps_s121_FA_gain',  r'2B101v19_MonoIEA9m_7mod_LIPC_Kaimal23mps_s123_FA_gain',
#                   r'2B101v19_MonoIEA9m_7mod_LIPC_Kaimal25mps_s125_FA_gain']
#
# baseline_files = [r'2B101v18_MonoIEA9m_7mod_teeter_Kaimal05mps_s105_FA_gain',  r'2B101v18_MonoIEA9m_7mod_teeter_Kaimal07mps_s107_FA_gain',  r'2B101v18_MonoIEA9m_7mod_teeter_Kaimal09mps_s109_FA_gain',  r'2B101v18_MonoIEA9m_7mod_teeter_Kaimal11mps_s111_FA_gain',  r'2B101v18_MonoIEA9m_7mod_teeter_Kaimal13mps_s113_FA_gain',
#                   r'2B101v18_MonoIEA9m_7mod_teeter_Kaimal15mps_s115_FA_gain',  r'2B101v18_MonoIEA9m_7mod_teeter_Kaimal17mps_s117_FA_gain',  r'2B101v18_MonoIEA9m_7mod_teeter_Kaimal19mps_s119_FA_gain',  r'2B101v18_MonoIEA9m_7mod_teeter_Kaimal21mps_s121_FA_gain',  r'2B101v18_MonoIEA9m_7mod_teeter_Kaimal23mps_s123_FA_gain',
#                   r'2B101v18_MonoIEA9m_7mod_teeter_Kaimal25mps_s125_FA_gain']