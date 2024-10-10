from ANSFAB__Utility import Utility
from ANSFAB__Utility import Bladed
import os
from config import TowerNodePosition, FOWTs


folder = r'H:\BladedWS\BottomFixed\towerHzItr\Tower_Decay_Test_in_y__2B101_Monopile_towerHzItr_new'
folder = r'H:\BladedWS\BottomFixed\towerHzItr\Tower_Decay_Test_in_x__3B_Monopile_towerHzItr_05mps'
folder = r'H:\BladedWS\BottomFixed\DLC_legacy\2B101_all_IAE_Monopiles_DLC12_evalu\DecayTests'

#baseline_file = r'2B20Volt_v009_1__tow_Hz_decay_baseline'
# baseline_file = r'2B20Volt_v009_1__tow_Hz_decay_baseline2'
#baseline_file = r'3B20Volt_v009_tow_Hz_decay__calmsea'
#baseline_file = r'2B20Volt_v009_1_15mps_full_TS'
baseline_file = r'3B90_Monopile_noDamp_15mps'
baseline_file = r'2B101v15_Monopile_noDamp_optImbal_15mps'
baseline_file = r'2B20Volt_v009_chirp_test_WESC'
baseline_file = r'2B20Volt_v009_chirp_long_FA'
baseline_file = r'3B90_Monopile_noDamp_optImbal_KAIMAL15mps'
baseline_file = r'2B20Volt_v009_1_kaimal 23mps'
baseline_file = r'DLC12_3B_MonoSGRE_ExZ0_126_flexDamp_DLC12_Kaimal_00y_05mps_s105'
baseline_file = r'3B_MonoPile__const15mps_tower_Hz_from_decay_test_in_y_new2'
baseline_file = r'3B_MonoPile__const15mps_towerDecay_in_x'
baseline_file = r'3B_MonoPile__const05mps_tower_Hz_from_decay_test_in_y_byDisplacement_without_Bezier'
baseline_file = r'2B101_MonoPile__tower_Hz_from_decay_test_in_x'
#baseline_file = r'3B_MonoPiles_tower_Hz_from_decay_test_FA'
#baseline_file = r'3B20Volt_v009_15mps_full_TS'

#out_folder = os.path.join(folder, '3B_itr_incl_low_Hz_full_timeSeries')
#out_folder = os.path.join(folder, '3B_Monopile_flexDampers_towerHzItr_15mps')
#out_folder = os.path.join(folder, '2B101v15_Monopile_noDamp_optImbalances_towerHzItr_15mps')
#out_folder = os.path.join(folder, '2B20Volt_v009_chirp_test_WESC')
out_folder = folder

#out_folder = os.path.join(folder, '2B101v15_Teeter_Monopile_towerHzItr__15mps')
#out_folder = os.path.join(folder, 'DecayTest__2B101v15_Monopile_towerFrequencyItr2')
baseline_file_path = os.path.join(folder, baseline_file)

#change_dict_csv_file_name = r'H:\BladedWS\BottomFixed\towerHzItr\bruteForceOpt\2023_08_11___bruteForce__FA_damper_tuning_for_tower_itr__2B101v15_Monopile_with_IPC_v2_changeDict.csv'
change_dict_csv_file_name = []

Evaluation_Parameter = 'Nacelle side-side acceleration'
Evaluation_Parameter = 'Nacelle fore-aft acceleration'
Evaluation_Parameter = 'Nacelle side-side displacement'
Evaluation_Parameter = 'Nacelle fore-aft displacement'

if False:
    # E_multipliers = [i/10 for i in range(10, 52, 2)]
    # E_multipliers = [i/100 for i in range(100, 300, 2)]
    # [E_multipliers.append(i / 100) for i in range(300, 3000, 20)]
    # E_multipliers = [i / 10 for i in range(12, 52, 2)]
    # E_multipliers = [1 * pow(1.04, i) for i in range(36)]
    # E_multipliers = [0.4 * pow(1.06, i) for i in range(48)]
    if FOWTs:
        E_multipliers = [1 * pow(1.06, i-30) for i in range(66)]   # WESC FOWT
    else:
        E_multipliers = [1 * pow(1.06, i-30) for i in range(120)]  # Bottom-fixed
    #E_multipliers = [1 * pow(1.02, i) for i in range(50)]
    print('will iterate the youngs modulus (of E+11) by 2.1x ', E_multipliers)
    outfileNames = []
    for multiplier in E_multipliers:
        # multiplier = 2.5/2

        ChangeNameDicts = [{'WORD': 'baseline2', 'EXCHANGE': ('_E%.3fE11' % (2*multiplier)).replace('.', '_')}]
        if FOWTs:
            ChangeNameDicts = [{'WORD': '_cannotfindtoprintatend', 'EXCHANGE': ('_E%.3fE11' % (2*multiplier)).replace('.', '_')}]
            n_tower_sections = 9
        else:
            ChangeNameDicts = [{'WORD': '_cannotfindtoprintatend', 'EXCHANGE': ('_E%.3fE11' % (2.1*multiplier)).replace('.', '_')}]
            n_tower_sections = 14
        #ChangeDicts = Bladed().change_dict_for_tower_steel_youngs_modulus(multiplier, FOWT)
        ChangeDicts = Bladed().change_dict_for_tower_steel_youngs_modulus__v2(multiplier, baseline_file_path, n_tower_sections=n_tower_sections)  # =9 for FOWTs  # =14 for the monopiles

        if change_dict_csv_file_name:
            from ANSFAB_csv_change_dict_reader import change_dict_from_csv_reader
            Additional_ChangeDicts = change_dict_from_csv_reader(change_dict_csv_file_name, multiplier)
            if Additional_ChangeDicts:
                ChangeDicts += Additional_ChangeDicts

        outfileName, out_folder = Utility().manipulatePRJfiles(ListOfBaselineFiles_local=[baseline_file], infolder=folder,
                                        outfolder=out_folder, ChangeDicts=ChangeDicts, ChangeNameDicts=ChangeNameDicts)
        outfileNames.append(outfileName[0])

    print('prepared runs: ', outfileNames)
    Bladed().AutoRunBatch(out_folder, outfileNames)


if False:
    print('Reading the tower eigenfrequency from a chirp excitation test')
    run_file_paths = Utility().return_run_files_in_folder(out_folder)
    ListDict = []
    for run_file_path in run_file_paths:
        BladedJob = run_file_path.split('\\')[-1]
        RunFolder = run_file_path.replace(BladedJob, '')
        [fileEnd, idx, DIMENS] = Utility().collectTimeSeriesStructureFromBladedFiles(RunFolder=RunFolder, BladedJob=BladedJob, VariableName='Tower Mz') # Node: tower Mz is My in the GL coordinate system
        tower_timeSeries = Utility().readTimeSeriesData(RunFolder=RunFolder, BladedJob=BladedJob, fileEnd=fileEnd, idx=idx, DIMENS=DIMENS, pos_of_node=TowerNodePosition[0])

        [fileEnd, idx, DIMENS] = Utility().collectTimeSeriesStructureFromBladedFiles(RunFolder=RunFolder, BladedJob=BladedJob, VariableName='chirp_frequency_in_Hz')
        chirp_frequency = Utility().readTimeSeriesData(RunFolder=RunFolder, BladedJob=BladedJob, fileEnd=fileEnd, idx=idx, DIMENS=DIMENS, pos_of_node=1)

        peak_value = float('-inf')
        # tower_eigenfrequency = 0
        for idx, moment in enumerate(tower_timeSeries):
            if peak_value < moment:
                peak_value = moment
                tower_eigenfrequency = chirp_frequency[idx]

        # Utility().easyPlotGraph(tower_timeSeries)

        print('run_file', run_file_path.split('\\')[-1], ' detected tower_eigenfrequency=', tower_eigenfrequency, 'Hz')
        ListDict.append({'run_file': run_file_path.split('\\')[-1], #'E_modulus': '42',
                         'tower_eigenfrequency': tower_eigenfrequency})

    Utility().writeListDictToCSV(ListDict, baseline_file_path + '.csv')


if True:
    run_file_paths = Utility().return_run_files_in_folder(out_folder)
    ListDict = []
    for run_file_path in run_file_paths:
        #tower_eigenfrequency = Utility().detect_tower_eigenfrequency_from_decay_test(run_file_path, plot_PSD=True, use_bezier=True)
        tower_eigenfrequency = Utility().detect_tower_eigenfrequency_from_decay_test(run_file_path, plot_PSD=False, use_bezier=True, Evaluation_Parameter=Evaluation_Parameter)
        ListDict.append({'run_file': run_file_path.split('\\')[-1], #'E_modulus': '42',
                         'tower_eigenfrequency': tower_eigenfrequency})

    Utility().writeListDictToCSV(ListDict, baseline_file_path + '.csv')


if False:
    run_file_paths = Utility().return_run_files_in_folder(out_folder)
    ListDict = []
    for run_file_path in run_file_paths:
        side_side_tower_eigenfrequency = Utility().detect_eigenfrequency_from_campbell_linearization(run_file_path,  mode_name='Tower 1st side-side mode', frequency_position=3)    # damped frequency is position 3
        side_side_tower_eigenfrequency_B = Utility().detect_eigenfrequency_from_campbell_linearization(run_file_path,  mode_name='Tower 1st side-side mode B', frequency_position=3, printDetails=False)    # damped frequency is position 3
        if float(side_side_tower_eigenfrequency) > float(side_side_tower_eigenfrequency_B) and float(side_side_tower_eigenfrequency_B) > 0:
            side_side_tower_eigenfrequency = side_side_tower_eigenfrequency_B
            print('eigenfrequency replaced by lower alternative mode extracted at ', side_side_tower_eigenfrequency, 'Hz in run', run_file_path)
        fore_aft_tower_eigenfrequency = Utility().detect_eigenfrequency_from_campbell_linearization(run_file_path,  mode_name='Tower 1st fore-aft mode', frequency_position=3)    # damped frequency is position 3
        fore_aft_tower_eigenfrequency_B = Utility().detect_eigenfrequency_from_campbell_linearization(run_file_path,  mode_name='Tower 1st fore-aft mode', frequency_position=3, printDetails=False)    # damped frequency is position 3
        if float(fore_aft_tower_eigenfrequency) > float(fore_aft_tower_eigenfrequency_B) and float(fore_aft_tower_eigenfrequency_B) > 0:
            fore_aft_tower_eigenfrequency = fore_aft_tower_eigenfrequency_B
            print('eigenfrequency replaced by lower alternative mode extracted at ', fore_aft_tower_eigenfrequency, 'Hz in run', run_file_path)
        ListDict.append({'run_file': run_file_path.split('\\')[-1], #'E_modulus': '42',
                         'side_side_tower_eigenfrequency': side_side_tower_eigenfrequency,
                         'fore_aft_tower_eigenfrequency': fore_aft_tower_eigenfrequency})

    csv_file_path = os.path.join(folder, out_folder.split('\\')[-1]) + '.csv'
    csv_file_path = os.path.join(out_folder, out_folder.split('\\')[-1]) + '.csv'
    Utility().writeListDictToCSV(ListDict, csv_file_path)


#run_file_path = r'H:\BladedWS\FOWTs\decay_test\2B20Volt_v009_1__decay_y20m'
#Utility().detect_tower_eigenfrequency_from_decay_test(run_file_path, plot_PSD=True)