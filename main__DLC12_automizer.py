from ANSFAB__Utility import Utility
from ANSFAB__Utility import Bladed


folder = r'H:\BladedWS\FOWTs\Best_of_BruteForce_full_time_series'
out_folder = r'H:\BladedWS\FOWTs\DLC12\2B20Volt_v009_FA_damper_v0'

baseline_file = '2b20volt_v009_1_15mps_g0_FA_damper_full_TS'
change_string = '_1_15mps_g0_FA_damper_full_TS'

folder = r'H:\BladedWS\FOWTs\DLC12\2B20Volt_v009_baseline'
folder = r'H:\BladedWS\FOWTs\DLC_ULS\3B20Volt_v008_baseline\DLC22__3B20Volt_v008_baseline_v2'
out_folder = r'H:\BladedWS\FOWTs\DLC_ULS\3B20Volt_v008_baseline\DLC22__3B20Volt_v008_baseline_v3'
baseline_file = '3B20Volt_v008_baseline_DLC22pitfail__09mps_s109'
change_string = '__09mps_s109'

#baseline_file = '3B20Volt_v008_15mps'
#change_string = '_15mps'

nSeeds = 6
# main script:
#DictOfChangeDicts = Bladed().change_dict_for_DLC12_iterations(turbulence_type='kaimal', nSeeds=nSeeds, wind_type='NTM', seastate='NSS', sim_output_time=200, sim_end_time=3800)
#DictOfChangeDicts = Bladed().change_dict_for_DLC12_iterations(turbulence_type='kaimal', nSeeds=nSeeds, wind_type='NTM', seastate='SSS')
DictOfChangeDicts = Bladed().change_dict_for_DLC12_iterations(turbulence_type='kaimal', nSeeds=nSeeds, wind_type='NTM', seastate='NSS', sim_output_time=200, sim_end_time=700)
Utility().createFolderIfNotExcisting(out_folder)
outfileNames = []
nmbrSeed = 0
windSpeeds = 0
for idx, ChangeDicts in enumerate(DictOfChangeDicts):
    ChangeNameDicts = [{'WORD': change_string, 'EXCHANGE': 'baseline_DLC16__%02d' % int(5+idx*2) + 'mps'}]
    ChangeNameDicts = [{'WORD': change_string, 'EXCHANGE': '__%02d' % int(5+windSpeeds*2) + 'mps' + '_s%01d' % int(nmbrSeed+1) + '%02d' % int(5+windSpeeds*2)}]
    nmbrSeed += 1
    if nmbrSeed >= nSeeds:
        nmbrSeed = 0
        windSpeeds += 1
    outfileName, out_folder = Utility().manipulatePRJfiles(ListOfBaselineFiles_local=[baseline_file], infolder=folder,
                                        outfolder=out_folder, ChangeDicts=ChangeDicts, ChangeNameDicts=ChangeNameDicts)
    outfileNames.append(outfileName[0])

print('prepared runs: ', outfileNames)
#Bladed().AutoRunBatch(out_folder, outfileNames)
