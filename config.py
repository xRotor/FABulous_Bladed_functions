""" ====================================================================================================================

                                              configuration file
                         ------------------------------------------------------------------

                        All parameters that need to be adapted from the user are stored here.

==================================================================================================================== """
# Number of Blades
nBlades = 2
if nBlades == 2:
    max_rotation_speed_bound = 0.785863055 * 1.2  # * 1.08  # 2B101 rated in rad/s is 0.785863055 and in rpm is 7.504439388
else:
    max_rotation_speed_bound = 0.714279490 * 1.2  # * 1.08  # 3B90  rated in rad/s is 0.714279490 and in rpm is 6.820866669

# Choose Flags
PrintDetails = False
FOWTs = False


# Folders and Job names
#MainFolder = r'H:\BladedWS\FOWTs\BruteOptimize_3B20Volt_v009'
MainFolder = r'H:\BladedWS\FOWTs\BruteOptimize_2B20Volt_v009'
MainFolder = r'H:\BladedWS\BottomFixed\towerHzItr\bruteForceOpt'
MainFolder = r'H:\BladedWS\FOWTs\STASuperTwistingControl_tuning'
#MainFolder = r'H:\BladedWS\FOWTs\BruteOptimize_3B20Volt_v008'
baselineFolder = MainFolder + r'\baselinefile_FA_damp_all_windspeeds'
baselineFolder = MainFolder + r'\baselinefiles'
#baselineFolder = MainFolder + r'\baselinefile_tow_itr'
#baselineFolder = MainFolder + r'\baselinefile_FA_damp'
MainPathToBladedRuns = MainFolder + r'\bruteForce'
MainPathToBladedRuns = MainFolder + r'\bruteForce_tower_itr'
MainPathToBladedRuns = MainFolder + r'\bruteForce_FA_damp_all_windspeeds'
MainPathToBladedRuns = MainFolder + r'\2B_IPC_bruteForce_v2_FA_n_StS_damp_for_Monopile_Hz_itr'
MainPathToBladedRuns = MainFolder + r'\BruteForce_opt_2B_ASTR_v02__alpha0_0001'
#MainPathToBladedRuns = MainFolder + r'\3B_bruteForce_FA_n_StS_damp_for_Monopile_Hz_itr'
#MainPathToBladedRuns = MainFolder + r'\bruteForce_FA_damp_itr'
DocString = "_default"
#DocString = "_bruteForce__controller_PI_gains__3B20Volt_v008"
#DocString = "_bruteForce__FA_dampers_gain_n_Hz__2B20Volt_v009_1__lower_I_gains"
#DocString = "_bruteForce__platform_pitch_damper_gain_n_Hz__2B20Volt_v009_1"
# DocString = "_fmin_search__FOWT_PI_gains__2B20Volt_v009_1"



ListOfBaselineFiles =[r"2B20Volt_v009_1_15mps.$PJ"]
#ListOfBaselineFiles =[]

# optimization parameter:
searchWords = ['factor_Pitch_FATowDamper', 'GA_Parameter11']  # initial values: [0.1, 0.05]
searchWords = ['GA_Parameter11', 'GA_Parameter12']  # initial values: [[0, 10], [0, 0.15]]
#searchWords = []  # initial values: [[0, 10], [0, 0.15]]
#searchWords = ['pitchPGain', 'pitchIGain']  # initial values: [0.43404, 0.03006]   [0.57695,0.01998]
addToRunFileNames = ['_ppitch_G', '_Hz']
#addToRunFileNames = []
#addToRunFileNames = ['_itr_P', '_I']


# set Bladed Batch directory (for server computing it has to be a shared drive)
bladed_batch_directory = r'C:\DNV\Batch\DefaultBatchDirectory'
bladed_batch_directory = r'H:\BladedWS\SharedBladed4_14BatchDirectory'









# Parameters to calculate DELs (damage equivalent loads)
Referenz_Frequency = 1.0  # Hz
k_steel = 4.0     # Woehler exponent for steel
k_composite = 10  # Woehler exponent for composite fibers
print('Woehler exponent of composite is chosen to be 10 instead of 12!!!!')
# time_total = 3600.0  # time series length in s
# deltat = 0.1         # time step length in s
# Nreff = time_total * Referenz_Frequency # calculated in the functions
nSectors = 12    # 24
eps = 0.001      # accuracy of factor to not divide by zero
var_nbins = 100  # bins for rain-flow count

# parameters for bearing load calculation
p_bearing = 3   # exponent p = 3 for ball bearings and 10/3 for roller bearings (https://www.nrel.gov/docs/fy10osti/42362.pdf)
p_yaw_bearing = 10/3   # roller bearing assumed; same for main bearing
bearing_DEL_nbins = 30
yaw_bearing_diameter = 7.7782  # simply the diameter of the last tower section
pitch_bearing_diameter__two_bladed = 7.882776
pitch_bearing_diameter__three_bladed = 6.504958

# fileEnds
runFileEnd = '.$PJ'  # had been 'fileEnd' earlier
towerFileEnd = '.$25'
hubFileEnd = '.$22'




# Control cost criterion (CCC) infromation:
# CostShares = {'Blade_costs': 0.18, 'Tower_costs': 0.3483, 'DriveTrain_costs': 0.075, 'PitchSys_costs': 0.044, 'Generator_costs': 0.153, 'CoE_CAPEX_ratio': 3.7037}
CostShares = {'Blade_costs': 0.15, 'Tower_costs': 0.3483, 'DriveTrain_costs': 0.050, 'PitchSys_costs': 0.044, 'Generator_costs': 0.250, 'CoE_CAPEX_ratio': 3.7037}

if FOWTs:
    # might work to leave this unchanged for other variables, because it might only be needed for the tower nodes anyhow
    TowerNodePosition = [3]  # some variables are loads have members and two notes each; all nodes of a single time step
    # are staggered in one column, thus: pos 1 is first node of first member; 2 is second node of member 1; 3 is first node of member 2 ..
else:
    TowerNodePosition = [1]
    print('CHECK IF (Bottom-Fixed) TOWER NODE POSITION 1 for Jackets and new IEA Monopile IS CORRECT in config.py!!')
    #TowerNodePosition = [3]
    #print('CHECK IF (Bottom-Fixed) TOWER NODE POSITION 3 for older Monopiles IS CORRECT in config.py!!')


DEL_keys = ['Blade_My_DEL', 'Blade_Mx_DEL', 'Hub_Mx_DEL', 'Tower_My_sector_max_DEL', 'Pitch_LDC']
if PrintDetails:
    print('DEL_keys are -> ' + ', '.join(DEL_keys))






nBits = 4

nSeeds = len(ListOfBaselineFiles)
nParams = len(searchWords)

from datetime import datetime
documentation_path = MainPathToBladedRuns + '\\' + datetime.today().strftime('%Y_%m_%d__') + DocString + '_Documentary.csv'
#documentation_path = r'H:\BladedWS\FOWTs\Optimize_FA_Damper_2B20Volt_v009\bruteForce\2023_04_26___bruteForce__FA_dampers_gain_n_Hz__2B20Volt_v009_1_Documentary.csv'
#documentation_path = r'H:\BladedWS\FOWTs\Optimize_PI_gains_2B20Volt_v009\bruteForce\2023_04_27___bruteForce__controller_PI_gains__2B20Volt_v009_1_Documentary.csv'










param_key = 'Params'
max_rotor_speed_key = 'RotationSpeed_max'

Statistics_Searching = []
Statistics_Searching.append({'VARIAB': 'Electrical power', 'FileEnd': '.%06', 'Desired': 'MEAN'})
Statistics_Searching.append({'VARIAB': 'Blade 1 My (Root axes)', 'FileEnd': '.%41', 'Desired': 'MAX'})
Statistics_Searching.append({'VARIAB': 'Rotor speed', 'FileEnd': '.%05', 'Desired': 'MAX'})
Statistics_Searching.append({'VARIAB': 'Stationary hub Fx', 'FileEnd': '.%23', 'Desired': 'MEAN'})
Statistics_Searching.append({'VARIAB': 'Nacelle fore-aft acceleration', 'FileEnd': '.%26', 'Desired': 'MAX'})
if FOWTs:
    Statistics_Searching.append({'VARIAB': 'Support Structure global orientation about y', 'FileEnd': '.%65', 'Desired': 'MEAN'})
    Statistics_Searching.append({'VARIAB': 'Support Structure global orientation about y', 'FileEnd': '.%65', 'Desired': 'MAX'})
    Statistics_Searching.append({'VARIAB': 'Mooring line tension', 'FileEnd': '.%77', 'Desired': 'MAX'})
# {'VARIAB': 'pitch_actuator_duty_cycle', 'FileEnd': '.%29', 'Desired': 'MAXMIN_Delta'},  # 'DIMENS[1]': 0, 'GENLAB': 'External Controller'

Statistics_keys = ['Power_mean', 'Blade_My_max', 'RotationSpeed_max', 'mean_Thrust_Hub_Fx', 'max_Nacelle_FA_accel']
if FOWTs:
    Statistics_keys += ['mean_Platform_Pitch', 'max_Platform_Pitch', 'max_mooring_tension']


FLS_Searching = []
FLS_Searching.append({'VARIAB': 'Blade 1 Mx (Root axes)', 'Desired': 'DEL', 'k_SN': k_composite, 'Key': 'Blade_1_Mx_DEL', 'NodePos': [1]})
FLS_Searching.append({'VARIAB': 'Blade 1 My (Root axes)', 'Desired': 'DEL', 'k_SN': k_composite, 'Key': 'Blade_1_My_DEL', 'NodePos': [1]})
FLS_Searching.append({'VARIAB': 'Blade 1 Mz (Root axes)', 'Desired': 'DEL', 'k_SN': k_composite, 'Key': 'Blade_1_Mz_DEL', 'NodePos': [1]})
FLS_Searching.append({'VARIAB': 'Blade 1 Fz (Root axes)', 'Desired': 'DEL', 'k_SN': k_composite, 'Key': 'Blade_1_Fz_DEL', 'NodePos': [1]})
FLS_Searching.append({'VARIAB': 'Tower My', 'Desired': 'DEL', 'k_SN': k_steel, 'Key': 'Tower_Mx_DEL', 'NodePos': TowerNodePosition})  # Note: The coordinate-system in the tower node is rotated in comparison with the GL-system, thus y^=x, z^=y, x^=z
FLS_Searching.append({'VARIAB': 'Tower Mz', 'Desired': 'DEL', 'k_SN': k_steel, 'Key': 'Tower_My_DEL', 'NodePos': TowerNodePosition})  # Note: The coordinate-system in the tower node is rotated in comparison with the GL-system, thus y^=x, z^=y, x^=z
FLS_Searching.append({'VARIAB': 'Tower My', 'Desired': 'DEL_sector', 'Orthogonal_VARIAB': 'Tower Mz', 'k_SN': k_steel, 'Key': 'Tower_Mxy_sector_DEL', 'NodePos': TowerNodePosition})  # Note: The coordinate-system in the tower node is rotated in comparison with the GL-system, thus y^=x, z^=y, x^=z
FLS_Searching.append({'VARIAB': 'Tower Mx', 'Desired': 'DEL', 'k_SN': k_steel, 'Key': 'Tower_Mz_DEL', 'NodePos': TowerNodePosition})  # Note: The coordinate-system in the tower node is rotated in comparison with the GL-system, thus y^=x, z^=y, x^=z
FLS_Searching.append({'VARIAB': 'Yaw bearing Mx', 'Desired': 'DEL', 'k_SN': k_steel, 'Key': 'Yaw_Mx_DEL', 'NodePos': [1]})
FLS_Searching.append({'VARIAB': 'Yaw bearing My', 'Desired': 'DEL', 'k_SN': k_steel, 'Key': 'Yaw_My_DEL', 'NodePos': [1]})
FLS_Searching.append({'VARIAB': 'Yaw bearing My', 'Desired': 'DEL_sector', 'Orthogonal_VARIAB': 'Yaw bearing Mx','k_SN': k_steel, 'Key': 'Yaw_Mxy_sector_DEL', 'NodePos': [-1]})
FLS_Searching.append({'VARIAB': 'Yaw bearing Mz', 'Desired': 'DEL', 'k_SN': k_steel, 'Key': 'Yaw_Mz_DEL', 'NodePos': [1]})
FLS_Searching.append({'VARIAB': 'Yaw bearing Fz', 'Desired': 'DEL', 'k_SN': k_steel, 'Key': 'Yaw_Fz_DEL', 'NodePos': [1]})
FLS_Searching.append({'VARIAB': 'Rotating hub Mx', 'Desired': 'DEL', 'k_SN': k_steel, 'Key': 'Hub_Mx_DEL', 'NodePos': [1]})
FLS_Searching.append({'VARIAB': 'Rotating hub My', 'Desired': 'DEL', 'k_SN': k_steel, 'Key': 'Hub_My_rotating_DEL', 'NodePos': [1]})
FLS_Searching.append({'VARIAB': 'Rotating hub Mz', 'Desired': 'DEL', 'k_SN': k_steel, 'Key': 'Hub_Mz_rotating_DEL', 'NodePos': [1]})
FLS_Searching.append({'VARIAB': 'Rotating hub My', 'Desired': 'DEL_sector', 'Orthogonal_VARIAB': 'Stationary hub Mz', 'k_SN': k_steel, 'Key': 'Hub_Myz_sector_DEL', 'NodePos': [-1]})
FLS_Searching.append({'VARIAB': 'Rotating hub Fx', 'Desired': 'DEL', 'k_SN': k_steel, 'Key': 'Thrust_Hub_rotating_Fx_DEL', 'NodePos': [1]})
FLS_Searching.append({'VARIAB': 'Stationary hub My', 'Desired': 'DEL', 'k_SN': k_steel, 'Key': 'Hub_My_stationary_DEL', 'NodePos': [1]})
FLS_Searching.append({'VARIAB': 'Stationary hub Mz', 'Desired': 'DEL', 'k_SN': k_steel, 'Key': 'Hub_Mz_stationary_DEL', 'NodePos': [1]})
# FLS_Searching.append({'VARIAB': 'Stationary hub Mx', 'FileEnd': '.%22', 'Desired': 'DEL', 'k_SN': k_steel, 'Key': 'Hub_Mx_rotating_DEL', 'NodePos': [-1]})
# FLS_Searching.append({'VARIAB': 'Stationary hub Fx', 'FileEnd': '.%22', 'Desired': 'DEL', 'k_SN': k_steel, 'Key': 'Thrust_Hub_rotating_Fx_DEL', 'NodePos': [-1]})
# FLS_Searching.append({'VARIAB': 'Blade 1 x-deflection (perpendicular to rotor plane)', 'FileEnd': '.%18', 'Desired': 'MAX', 'Key': 'Blade_1_Bending_MAX', 'NodePos': [-1]})
# FLS_Searching.append({'VARIAB': 'Tip to tower closest approach', 'FileEnd': '.%07', 'Desired': 'MIN', 'Key': 'Tip_to_Tower_MIN', 'NodePos': [-1]})
FLS_Searching.append({'VARIAB': 'Electrical power', 'Desired': 'MEAN', 'Key': 'Power_in_W_MEAN', 'NodePos': [1]})
FLS_Searching.append({'VARIAB': 'Electrical power', 'Desired': 'STD', 'Key': 'Power_in_W_STD', 'NodePos': [1]})
FLS_Searching.append({'VARIAB': 'Rotor speed', 'Desired': 'MEAN', 'Key': 'RotationSpeed_MEAN', 'NodePos': [1]})
FLS_Searching.append({'VARIAB': 'Rotor speed', 'Desired': 'MAX', 'Key': 'RotationSpeed_MAX', 'NodePos': [1]})
FLS_Searching.append({'VARIAB': 'pitch_actuator_duty_cycle', 'Desired': 'ADC', 'Key': 'ADC_in_deg', 'NodePos': [1]})
FLS_Searching.append({'VARIAB': 'Blade root 1 Mxy', 'Desired': 'LDC', 'Pitch_Velo_VARIAB': 'Blade 1 pitch rate', 'Key': 'LDC_in_Nm_rad', 'NodePos': [1]})
FLS_Searching.append({'VARIAB': 'Nacelle fore-aft acceleration', 'FileEnd': '.%26', 'Desired': 'STD', 'Key': 'Nacelle_FA_accel_MAX', 'NodePos': [1]})
FLS_Searching.append({'VARIAB': 'Blade root 1 Mx', 'Desired': 'DEL', 'k_SN': k_composite, 'Key': 'Blade_root_1_Mx_DEL', 'NodePos': [1]})
FLS_Searching.append({'VARIAB': 'Blade root 1 My', 'Desired': 'DEL', 'k_SN': k_composite, 'Key': 'Blade_root_1_My_DEL', 'NodePos': [1]})
FLS_Searching.append({'VARIAB': 'Blade root 1 My', 'Desired': 'DEL_sector', 'Orthogonal_VARIAB': 'Blade root 1 Mx', 'k_SN': k_composite, 'Key': 'Blade_root_1_Mxy_sector_DEL', 'NodePos': [1]})
# if FOWTs:
FLS_Searching.append({'VARIAB': 'Support Structure global orientation about y', 'FileEnd': '.%65', 'Desired': 'MEAN', 'Key': 'Platform_Pitch_MEAN', 'NodePos': [1]})  # only used for FOWTs
FLS_Searching.append({'VARIAB': 'Support Structure global orientation about y', 'FileEnd': '.%65', 'Desired': 'ULS', 'Key': 'Platform_Pitch_ULS', 'NodePos': [1]})  # only used for FOWTs
MooringLineNodePosition = ['ALL']
FLS_Searching.append({'VARIAB': 'Mooring line tension', 'FileEnd': '.%77', 'Desired': 'MAX', 'Key': 'max_mooring_tension_ULS', 'NodePos': MooringLineNodePosition})  # only used for FOWTs #
FLS_Searching.append({'VARIAB': 'Mooring line tension', 'FileEnd': '.%77', 'Desired': 'DEL', 'k_SN': k_steel, 'Key': 'mooring_tension_DEL', 'NodePos': [1]})  # only used for FOWTs #

FLS_Searching.append({'VARIAB': 'Stationary hub Fy', 'Desired': 'DEL', 'k_SN': k_steel, 'Key': 'Hub_Fy_stationary_DEL', 'NodePos': [1]})
FLS_Searching.append({'VARIAB': 'Stationary hub Fz', 'Desired': 'DEL', 'k_SN': k_steel, 'Key': 'Hub_Fz_stationary_DEL', 'NodePos': [1]})
FLS_Searching.append({'VARIAB': 'Stationary hub Fx', 'Desired': 'MEAN', 'k_SN': k_steel, 'Key': 'Hub_Fx_thust_MEAN', 'NodePos': [1]})


FLS_Searching.append({'VARIAB': 'Blade 1 Mxy (Root axes)', 'Desired': 'P_ea_pitch', 'Key': 'P_ea_pitch_equivalent_bearing_load_per_diam', 'k_SN': p_bearing, 'NodePos': [1]})
FLS_Searching.append({'VARIAB': 'Yaw bearing Mxy', 'Desired': 'P_ea_yaw', 'Key': 'P_ea_yaw_bearing_load', 'k_SN': p_yaw_bearing, 'NodePos': [1]})
FLS_Searching.append({'VARIAB': 'Rotating hub My', 'Desired': 'P_ea_first_main_bearing', 'Orthogonal_VARIAB': 'Rotating hub Mz', 'k_SN': p_yaw_bearing, 'Key': 'P_ea_main_bearing_P_r_equivalent_load', 'NodePos': [1]})
FLS_Searching.append({'VARIAB': 'Rotating hub My', 'Desired': 'DEL_sector_rot_main_shaft', 'Orthogonal_VARIAB': 'Rotating hub Mz', 'k_SN': k_steel, 'Key': 'main_shaft_Myz_sector_DEL_at_first_bearing', 'NodePos': [1]})

# FLS_Searching.append({'VARIAB': 'Tower My', 'Desired': 'DEL_sector_HP_filtered', 'Orthogonal_VARIAB': 'Tower Mz', 'filter_HP_Hz': 0.11, 'k_SN': k_steel, 'Key': 'Tower_Mxy_sector_DEL_HP_filtered', 'NodePos': TowerNodePosition})

FLS_Searching.append({'VARIAB': 'Teeter angle (delta-3 direction)', 'FileEnd': '.%21', 'Desired': 'ULS', 'Key': 'Teeter_angle_AMAX', 'NodePos': [1]})  # only used for teetering turbines
FLS_Searching.append({'VARIAB': 'Teeter velocity (delta-3 direction)', 'FileEnd': '.%21', 'Desired': 'ULS', 'Key': 'Teeter_velocity_AMAX', 'NodePos': [1]})  # only used for teetering turbines






# same order as FLS
ULS_Searching = []
ULS_Searching.append({'VARIAB': 'Blade 1 Mx (Root axes)', 'FileEnd': '.%41', 'Desired': 'ULS', 'Key': 'Blade_1_Mx_ULS', 'NodePos': [1]})
ULS_Searching.append({'VARIAB': 'Blade 1 My (Root axes)', 'FileEnd': '.%41', 'Desired': 'ULS', 'Key': 'Blade_1_My_ULS', 'NodePos': [1]})
ULS_Searching.append({'VARIAB': 'Blade 1 Mz (Root axes)', 'FileEnd': '.%41', 'Desired': 'ULS', 'Key': 'Blade_1_Mz_ULS', 'NodePos': [1]})
ULS_Searching.append({'VARIAB': 'Blade 1 Fz (Root axes)', 'FileEnd': '.%41', 'Desired': 'ULS', 'Key': 'Blade_1_Fz_ULS', 'NodePos': [1]})
ULS_Searching.append({'VARIAB': 'Tower My', 'FileEnd': '.%25', 'Desired': 'ULS', 'Key': 'Tower_Mx_ULS', 'NodePos': TowerNodePosition})  # Note: The coordinate-system in the tower node is rotated in comparison with the GL-system, thus y^=x, z^=y, x^=z
ULS_Searching.append({'VARIAB': 'Tower Mz', 'FileEnd': '.%25', 'Desired': 'ULS', 'Key': 'Tower_My_ULS', 'NodePos': TowerNodePosition})  # Note: The coordinate-system in the tower node is rotated in comparison with the GL-system, thus y^=x, z^=y, x^=z
ULS_Searching.append({'VARIAB': 'Tower Myz', 'FileEnd': '.%25', 'Desired': 'ULS', 'Key': 'Tower_Mxy_ULS', 'NodePos': TowerNodePosition})  # Note: The coordinate-system in the tower node is rotated in comparison with the GL-system, thus y^=x, z^=y, x^=z
ULS_Searching.append({'VARIAB': 'Tower Mx', 'FileEnd': '.%25', 'Desired': 'ULS', 'Key': 'Tower_Mz_ULS', 'NodePos': TowerNodePosition})  # Note: The coordinate-system in the tower node is rotated in comparison with the GL-system, thus y^=x, z^=y, x^=z
ULS_Searching.append({'VARIAB': 'Yaw bearing Mx', 'FileEnd': '.%24', 'Desired': 'ULS', 'Key': 'Yaw_Mx_ULS', 'NodePos': [1]})
ULS_Searching.append({'VARIAB': 'Yaw bearing My', 'FileEnd': '.%24', 'Desired': 'ULS', 'Key': 'Yaw_My_ULS', 'NodePos': [1]})
ULS_Searching.append({'VARIAB': 'Yaw bearing Mxy', 'FileEnd': '.%24', 'Desired': 'ULS', 'Key': 'Yaw_Mxy_ULS', 'NodePos': [1]})
ULS_Searching.append({'VARIAB': 'Yaw bearing Mz', 'FileEnd': '.%24', 'Desired': 'ULS', 'Key': 'Yaw_Mz_ULS', 'NodePos': [1]})
ULS_Searching.append({'VARIAB': 'Yaw bearing Fz', 'FileEnd': '.%24', 'Desired': 'ULS', 'Key': 'Yaw_Fz_ULS', 'NodePos': [1]})

ULS_Searching.append({'VARIAB': 'Rotating hub Mx', 'FileEnd': '.%22', 'Desired': 'ULS', 'Key': 'Hub_Mx_ULS', 'NodePos': [1]})
ULS_Searching.append({'VARIAB': 'Rotating hub My', 'FileEnd': '.%22', 'Desired': 'ULS', 'Key': 'Hub_My_rot_ULS', 'NodePos': [1]})
ULS_Searching.append({'VARIAB': 'Rotating hub Mz', 'FileEnd': '.%22', 'Desired': 'ULS', 'Key': 'Hub_Mz_rot_ULS', 'NodePos': [1]})
ULS_Searching.append({'VARIAB': 'Rotating hub Myz', 'FileEnd': '.%22', 'Desired': 'ULS', 'Key': 'Hub_Myz_ULS', 'NodePos': [1]})
ULS_Searching.append({'VARIAB': 'Rotating hub Fx', 'FileEnd': '.%22', 'Desired': 'ULS', 'Key': 'Thrust_Hub_Fx_ULS', 'NodePos': [1]})
ULS_Searching.append({'VARIAB': 'Stationary hub My', 'FileEnd': '.%22', 'Desired': 'ULS', 'Key': 'Hub_My_stat_ULS', 'NodePos': [1]})
ULS_Searching.append({'VARIAB': 'Stationary hub Mz', 'FileEnd': '.%22', 'Desired': 'ULS', 'Key': 'Hub_Mz_stat_ULS', 'NodePos': [1]})
ULS_Searching.append({'VARIAB': 'Stationary hub Fy', 'FileEnd': '.%22', 'Desired': 'ULS', 'Key': 'Hub_Fy_stat_ULS', 'NodePos': [1]})
ULS_Searching.append({'VARIAB': 'Stationary hub Fz', 'FileEnd': '.%22', 'Desired': 'ULS', 'Key': 'Hub_Fz_stat_ULS', 'NodePos': [1]})

ULS_Searching.append({'VARIAB': 'Rotor speed', 'FileEnd': '.%05', 'Desired': 'MAX', 'Key': 'RotationSpeed_MAX', 'NodePos': [1]})

ULS_Searching.append({'VARIAB': 'Blade 1 x-deflection (perpendicular to rotor plane)', 'FileEnd': '.%18', 'Desired': 'MAX', 'Key': 'Blade_1_Bending_MAX', 'NodePos': [1]})
ULS_Searching.append({'VARIAB': 'Tip to tower closest approach', 'FileEnd': '.%07', 'Desired': 'MIN', 'Key': 'Tip_to_Tower_MIN', 'NodePos': [1]})
ULS_Searching.append({'VARIAB': 'Nacelle fore-aft acceleration', 'FileEnd': '.%26', 'Desired': 'MAX', 'Key': 'Nacelle_FA_accel_MAX', 'NodePos': [1]})
# if FOWTs:
ULS_Searching.append({'VARIAB': 'Support Structure global orientation about y', 'FileEnd': '.%65', 'Desired': 'MAX', 'Key': 'Platform_Pitch_ULS', 'NodePos': [1]})  # only used for FOWTs
MooringLineNodePosition = ['ALL']
ULS_Searching.append({'VARIAB': 'Mooring line tension', 'FileEnd': '.%77', 'Desired': 'MAX', 'Key': 'max_mooring_tension_ULS', 'NodePos': MooringLineNodePosition})  # only used for FOWTs #

ULS_Searching.append({'VARIAB': 'Blade 1 Mxy (Root axes)', 'FileEnd': '.%XX', 'Desired': 'pitch_bearing_ULS', 'Key': 'pitch_bearing_Q_max_yaw_ULS', 'NodePos': [1]})
ULS_Searching.append({'VARIAB': 'Yaw bearing Mxy', 'FileEnd': '.%24', 'Desired': 'yaw_bearing_ULS', 'Key': 'yaw_bearing_Q_max_yaw_ULS', 'NodePos': [1]})
ULS_Searching.append({'VARIAB': 'Rotating hub My', 'FileEnd': '.%XX', 'Desired': 'main_bearing_ULS', 'Key': 'main_bearing_P_Or_ULS', 'NodePos': [1]})
ULS_Searching.append({'VARIAB': 'Rotating hub My', 'FileEnd': '.%XX', 'Desired': 'main_shaft_ULS', 'Key': 'main_shaft_Myz_at_bearing_ULS', 'NodePos': [1]})

ULS_Searching.append({'VARIAB': 'Teeter angle (delta-3 direction)', 'FileEnd': '.%21', 'Desired': 'ULS', 'Key': 'Teeter_angle_AMAX', 'NodePos': [1]})  # only used for teetering turbines
ULS_Searching.append({'VARIAB': 'Teeter velocity (delta-3 direction)', 'FileEnd': '.%21', 'Desired': 'ULS', 'Key': 'Teeter_velocity_AMAX', 'NodePos': [1]})  # only used for teetering turbines
# ULS_Searching.append({'VARIAB': 'Electrical power', 'FileEnd': '.%06', 'Desired': 'MAX', 'Key': 'Power_MAX'})

ULS_Searching.append({'VARIAB': 'Blade 2 Mx (Root axes)', 'FileEnd': '.%41', 'Desired': 'ULS', 'Key': 'Blade_2_Mx_ULS', 'NodePos': [1]})
ULS_Searching.append({'VARIAB': 'Blade 2 My (Root axes)', 'FileEnd': '.%41', 'Desired': 'ULS', 'Key': 'Blade_2_My_ULS', 'NodePos': [1]})
ULS_Searching.append({'VARIAB': 'Blade 2 Mz (Root axes)', 'FileEnd': '.%41', 'Desired': 'ULS', 'Key': 'Blade_2_Mz_ULS', 'NodePos': [1]})
ULS_Searching.append({'VARIAB': 'Blade 2 Fz (Root axes)', 'FileEnd': '.%41', 'Desired': 'ULS', 'Key': 'Blade_2_Fz_ULS', 'NodePos': [1]})

ULS_Searching.append({'VARIAB': 'Blade 3 Mx (Root axes)', 'FileEnd': '.%41', 'Desired': 'ULS', 'Key': 'Blade_3_Mx_ULS', 'NodePos': [1]})
ULS_Searching.append({'VARIAB': 'Blade 3 My (Root axes)', 'FileEnd': '.%41', 'Desired': 'ULS', 'Key': 'Blade_3_My_ULS', 'NodePos': [1]})
ULS_Searching.append({'VARIAB': 'Blade 3 Mz (Root axes)', 'FileEnd': '.%41', 'Desired': 'ULS', 'Key': 'Blade_3_Mz_ULS', 'NodePos': [1]})
ULS_Searching.append({'VARIAB': 'Blade 3 Fz (Root axes)', 'FileEnd': '.%41', 'Desired': 'ULS', 'Key': 'Blade_3_Fz_ULS', 'NodePos': [1]})

ULS_Searching.append({'VARIAB': 'Blade 2 x-deflection (perpendicular to rotor plane)', 'FileEnd': '.%18', 'Desired': 'MAX', 'Key': 'Blade_2_Bending_MAX', 'NodePos': [1]})
ULS_Searching.append({'VARIAB': 'Blade 3 x-deflection (perpendicular to rotor plane)', 'FileEnd': '.%18', 'Desired': 'MAX', 'Key': 'Blade_3_Bending_MAX', 'NodePos': [1]})




# Oldschool
if False:
    ULS_Searching = []
    ULS_Searching.append({'VARIAB': 'Blade 1 Mx (Root axes)', 'FileEnd': '.%41', 'Desired': 'ULS', 'Key': 'Blade_1_Mx_ULS', 'NodePos': [1]})
    ULS_Searching.append({'VARIAB': 'Blade 1 My (Root axes)', 'FileEnd': '.%41', 'Desired': 'ULS', 'Key': 'Blade_1_My_ULS', 'NodePos': [1]})
    ULS_Searching.append({'VARIAB': 'Blade 1 Mz (Root axes)', 'FileEnd': '.%41', 'Desired': 'ULS', 'Key': 'Blade_1_Mz_ULS', 'NodePos': [1]})
    ULS_Searching.append({'VARIAB': 'Blade 1 Fz (Root axes)', 'FileEnd': '.%41', 'Desired': 'ULS', 'Key': 'Blade_1_Fz_ULS', 'NodePos': [1]})
    ULS_Searching.append({'VARIAB': 'Tower My', 'FileEnd': '.%25', 'Desired': 'ULS', 'Key': 'Tower_Mx_ULS', 'NodePos': TowerNodePosition})  # Note: The coordinate-system in the tower node is rotated in comparison with the GL-system, thus y^=x, z^=y, x^=z
    ULS_Searching.append({'VARIAB': 'Tower Mz', 'FileEnd': '.%25', 'Desired': 'ULS', 'Key': 'Tower_My_ULS', 'NodePos': TowerNodePosition})  # Note: The coordinate-system in the tower node is rotated in comparison with the GL-system, thus y^=x, z^=y, x^=z
    ULS_Searching.append({'VARIAB': 'Tower Myz', 'FileEnd': '.%25', 'Desired': 'ULS', 'Key': 'Tower_Mxy_ULS', 'NodePos': TowerNodePosition})  # Note: The coordinate-system in the tower node is rotated in comparison with the GL-system, thus y^=x, z^=y, x^=z
    ULS_Searching.append({'VARIAB': 'Tower Mx', 'FileEnd': '.%25', 'Desired': 'ULS', 'Key': 'Tower_Mz_ULS', 'NodePos': TowerNodePosition})  # Note: The coordinate-system in the tower node is rotated in comparison with the GL-system, thus y^=x, z^=y, x^=z
    ULS_Searching.append({'VARIAB': 'Rotating hub Mx', 'FileEnd': '.%22', 'Desired': 'ULS', 'Key': 'Hub_Mx_ULS', 'NodePos': [1]})
    ULS_Searching.append({'VARIAB': 'Rotating hub Myz', 'FileEnd': '.%22', 'Desired': 'ULS', 'Key': 'Hub_Myz_ULS', 'NodePos': [1]})
    ULS_Searching.append({'VARIAB': 'Rotating hub Fx', 'FileEnd': '.%22', 'Desired': 'ULS', 'Key': 'Thrust_Hub_Fx_ULS', 'NodePos': [1]})
    ULS_Searching.append({'VARIAB': 'Yaw bearing Mxy', 'FileEnd': '.%24', 'Desired': 'ULS', 'Key': 'Yaw_Mxy_ULS', 'NodePos': [1]})
    ULS_Searching.append({'VARIAB': 'Yaw bearing Mz', 'FileEnd': '.%24', 'Desired': 'ULS', 'Key': 'Yaw_Mz_ULS', 'NodePos': [1]})
    ULS_Searching.append({'VARIAB': 'Blade 1 x-deflection (perpendicular to rotor plane)', 'FileEnd': '.%18', 'Desired': 'MAX', 'Key': 'Blade_1_Bending_MAX', 'NodePos': [1]})
    ULS_Searching.append({'VARIAB': 'Tip to tower closest approach', 'FileEnd': '.%07', 'Desired': 'MIN', 'Key': 'Tip_to_Tower_MIN', 'NodePos': [1]})
    ULS_Searching.append({'VARIAB': 'Rotor speed', 'FileEnd': '.%05', 'Desired': 'MAX', 'Key': 'RotationSpeed_MAX', 'NodePos': [1]})
    ULS_Searching.append({'VARIAB': 'Nacelle fore-aft acceleration', 'FileEnd': '.%26', 'Desired': 'MAX', 'Key': 'Nacelle_FA_accel_MAX', 'NodePos': [1]})
    # if FOWTs:
    ULS_Searching.append({'VARIAB': 'Support Structure global orientation about y', 'FileEnd': '.%65', 'Desired': 'MAX', 'Key': 'Platform_Pitch_ULS', 'NodePos': [1]})  # only used for FOWTs
    MooringLineNodePosition = ['ALL']
    ULS_Searching.append({'VARIAB': 'Mooring line tension', 'FileEnd': '.%77', 'Desired': 'MAX', 'Key': 'max_mooring_tension_ULS', 'NodePos': MooringLineNodePosition})  # only used for FOWTs #

    ULS_Searching.append({'VARIAB': 'Blade 1 Mxy (Root axes)', 'FileEnd': '.%XX', 'Desired': 'pitch_bearing_ULS', 'Key': 'pitch_bearing_Q_max_yaw_ULS', 'NodePos': [1]})
    ULS_Searching.append({'VARIAB': 'Yaw bearing Mxy', 'FileEnd': '.%24', 'Desired': 'yaw_bearing_ULS', 'Key': 'yaw_bearing_Q_max_yaw_ULS', 'NodePos': [1]})
    ULS_Searching.append( {'VARIAB': 'Rotating hub My', 'FileEnd': '.%XX', 'Desired': 'main_bearing_ULS', 'Key': 'main_bearing_P_Or_ULS', 'NodePos': [1]})
    ULS_Searching.append({'VARIAB': 'Rotating hub My', 'FileEnd': '.%XX', 'Desired': 'main_shaft_ULS', 'Key': 'main_shaft_Myz_at_bearing_ULS', 'NodePos': [1]})

    ULS_Searching.append({'VARIAB': 'Teeter angle (delta-3 direction)', 'FileEnd': '.%21', 'Desired': 'ULS', 'Key': 'Teeter_angle_AMAX', 'NodePos': [1]})  # only used for teetering turbines
    ULS_Searching.append({'VARIAB': 'Teeter velocity (delta-3 direction)', 'FileEnd': '.%21', 'Desired': 'ULS', 'Key': 'Teeter_velocity_AMAX', 'NodePos': [1]})  # only used for teetering turbines
    # ULS_Searching.append({'VARIAB': 'Electrical power', 'FileEnd': '.%06', 'Desired': 'MAX', 'Key': 'Power_MAX'})


    ULS_Searching.append({'VARIAB': 'Stationary hub Fy', 'FileEnd': '.%22', 'Desired': 'ULS', 'Key': 'Hub_Stat_Fy_ULS', 'NodePos': [1]})
    ULS_Searching.append({'VARIAB': 'Stationary hub Fz', 'FileEnd': '.%22', 'Desired': 'ULS', 'Key': 'Hub_Stat_Fz_ULS', 'NodePos': [1]})

    ULS_Searching.append({'VARIAB': 'Blade 2 Mx (Root axes)', 'FileEnd': '.%41', 'Desired': 'ULS', 'Key': 'Blade_2_Mx_ULS', 'NodePos': [1]})
    ULS_Searching.append({'VARIAB': 'Blade 2 My (Root axes)', 'FileEnd': '.%41', 'Desired': 'ULS', 'Key': 'Blade_2_My_ULS', 'NodePos': [1]})
    ULS_Searching.append({'VARIAB': 'Blade 2 Mz (Root axes)', 'FileEnd': '.%41', 'Desired': 'ULS', 'Key': 'Blade_2_Mz_ULS', 'NodePos': [1]})
    ULS_Searching.append({'VARIAB': 'Blade 2 Fz (Root axes)', 'FileEnd': '.%41', 'Desired': 'ULS', 'Key': 'Blade_2_Fz_ULS', 'NodePos': [1]})


    ULS_Searching.append({'VARIAB': 'Blade 3 Mx (Root axes)', 'FileEnd': '.%41', 'Desired': 'ULS', 'Key': 'Blade_3_Mx_ULS', 'NodePos': [1]})
    ULS_Searching.append({'VARIAB': 'Blade 3 My (Root axes)', 'FileEnd': '.%41', 'Desired': 'ULS', 'Key': 'Blade_3_My_ULS', 'NodePos': [1]})
    ULS_Searching.append({'VARIAB': 'Blade 3 Mz (Root axes)', 'FileEnd': '.%41', 'Desired': 'ULS', 'Key': 'Blade_3_Mz_ULS', 'NodePos': [1]})
    ULS_Searching.append({'VARIAB': 'Blade 3 Fz (Root axes)', 'FileEnd': '.%41', 'Desired': 'ULS', 'Key': 'Blade_3_Fz_ULS', 'NodePos': [1]})

    ULS_Searching.append({'VARIAB': 'Blade 2 x-deflection (perpendicular to rotor plane)', 'FileEnd': '.%18', 'Desired': 'MAX', 'Key': 'Blade_2_Bending_MAX', 'NodePos': [1]})
    ULS_Searching.append({'VARIAB': 'Blade 3 x-deflection (perpendicular to rotor plane)', 'FileEnd': '.%18', 'Desired': 'MAX', 'Key': 'Blade_3_Bending_MAX', 'NodePos': [1]})



'''
FLS_Searching.append({'VARIAB': 'Blade 2 Mx (Root axes)', 'FileEnd': '.%41', 'Desired': 'DEL', 'Key': 'Blade_2_Mx_ULS', 'NodePos': [-1]})
FLS_Searching.append({'VARIAB': 'Blade 2 My (Root axes)', 'FileEnd': '.%41', 'Desired': 'DEL', 'Key': 'Blade_2_My_ULS', 'NodePos': [-1]})
FLS_Searching.append({'VARIAB': 'Blade 2 Mz (Root axes)', 'FileEnd': '.%41', 'Desired': 'DEL', 'Key': 'Blade_2_Mz_ULS', 'NodePos': [-1]})
FLS_Searching.append({'VARIAB': 'Blade 2 Fz (Root axes)', 'FileEnd': '.%41', 'Desired': 'DEL', 'Key': 'Blade_2_Fz_ULS', 'NodePos': [-1]})


FLS_Searching.append({'VARIAB': 'Blade 3 Mx (Root axes)', 'FileEnd': '.%41', 'Desired': 'DEL', 'Key': 'Blade_3_Mx_ULS', 'NodePos': [-1]})
FLS_Searching.append({'VARIAB': 'Blade 3 My (Root axes)', 'FileEnd': '.%41', 'Desired': 'DEL', 'Key': 'Blade_3_My_ULS', 'NodePos': [-1]})
FLS_Searching.append({'VARIAB': 'Blade 3 Mz (Root axes)', 'FileEnd': '.%41', 'Desired': 'DEL', 'Key': 'Blade_3_Mz_ULS', 'NodePos': [-1]})
FLS_Searching.append({'VARIAB': 'Blade 3 Fz (Root axes)', 'FileEnd': '.%41', 'Desired': 'DEL', 'Key': 'Blade_3_Fz_ULS', 'NodePos': [-1]})

FLS_Searching.append({'VARIAB': 'Blade 2 x-deflection (perpendicular to rotor plane)', 'FileEnd': '.%18', 'Desired': 'MAX', 'Key': 'Blade_2_Bending_MAX', 'NodePos': [-1]})
FLS_Searching.append({'VARIAB': 'Blade 3 x-deflection (perpendicular to rotor plane)', 'FileEnd': '.%18', 'Desired': 'MAX', 'Key': 'Blade_3_Bending_MAX', 'NodePos': [-1]})
'''


'''
ULS_Searching = []
ULS_Searching.append({'VARIAB': 'Blade 1 Mx (Root axes)', 'FileEnd': '.%41', 'Desired': 'ULS'})
ULS_Searching.append({'VARIAB': 'Blade 1 My (Root axes)', 'FileEnd': '.%41', 'Desired': 'ULS'})
ULS_Searching.append({'VARIAB': 'Blade 1 Mz (Root axes)', 'FileEnd': '.%41', 'Desired': 'ULS'})
ULS_Searching.append({'VARIAB': 'Blade 1 Fz (Root axes)', 'FileEnd': '.%41', 'Desired': 'ULS'})
ULS_Searching.append({'VARIAB': 'Tower My', 'FileEnd': '.%25', 'Desired': 'ULS'})
ULS_Searching.append({'VARIAB': 'Tower Mz', 'FileEnd': '.%25', 'Desired': 'ULS'})
ULS_Searching.append({'VARIAB': 'Tower Myz', 'FileEnd': '.%25', 'Desired': 'ULS'})
ULS_Searching.append({'VARIAB': 'Tower Mx', 'FileEnd': '.%25', 'Desired': 'ULS'})
ULS_Searching.append({'VARIAB': 'Rotating hub Mx', 'FileEnd': '.%22', 'Desired': 'ULS'})
ULS_Searching.append({'VARIAB': 'Rotating hub Myz', 'FileEnd': '.%22', 'Desired': 'ULS'})
ULS_Searching.append({'VARIAB': 'Rotating hub Fx', 'FileEnd': '.%22', 'Desired': 'ULS'})
ULS_Searching.append({'VARIAB': 'Yaw bearing Mxy', 'FileEnd': '.%24', 'Desired': 'ULS'})
ULS_Searching.append({'VARIAB': 'Yaw bearing Mz', 'FileEnd': '.%24', 'Desired': 'ULS'})
ULS_Searching.append({'VARIAB': 'Blade 1 x-deflection (perpendicular to rotor plane)', 'FileEnd': '.%18', 'Desired': 'MAX'})
ULS_Searching.append({'VARIAB': 'Tip to tower closest approach', 'FileEnd': '.%07', 'Desired': 'MIN'})
# ULS_Searching.append({'VARIAB': 'Electrical power', 'FileEnd': '.%06', 'Desired': 'MAX'})
ULS_Searching.append({'VARIAB': 'Rotor speed', 'FileEnd': '.%05', 'Desired': 'MAX'})
ULS_Searching.append({'VARIAB': 'Nacelle fore-aft acceleration', 'FileEnd': '.%26', 'Desired': 'MAX'})
if FOWTs:
    ULS_Searching.append({'VARIAB': 'Support Structure global orientation about y', 'FileEnd': '.%65', 'Desired': 'MAX'})
    ULS_Searching.append({'VARIAB': 'Mooring line tension', 'FileEnd': '.%77', 'Desired': 'MAX'})

ULS_Searching.append({'VARIAB': 'Teeter angle (delta-3 direction)', 'FileEnd': '.%21', 'Desired': 'MAX'})

ULS_Searching_keys = ['Blade_Mx_ULS', 'Blade_My_ULS', 'Blade_Mz_ULS', 'Blade_Fz_ULS', 'Tower_Mx_ULS', 'Tower_My_ULS',
                 'Tower_My_sector_max_ULS', 'Tower_Mz_ULS', 'Hub_Mx_ULS', 'Hub_Myz_sector_max_ULS', 'Thrust_Hub_Fx_ULS', #'Power_ULS',
                 'Yaw_Mxy_ULS', 'Yaw_Mz_ULS', 'Blade_Bending_MAX', 'Tip_to_Tower_MIN', 'RotationSpeed_MAX', 'Nacelle_FA_accel_MAX']
if FOWTs:
    ULS_Searching_keys += ['Platform_Pitch_ULS', 'max_mooring_tension_ULS']

ULS_Searching_keys += ['Teeter_angle_MAX']
'''