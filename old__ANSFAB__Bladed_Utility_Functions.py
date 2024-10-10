""" ====================================================================================================================

                                This script is imported by the other Python script
                         ------------------------------------------------------------------

            This script is not intended to be executable. It stores the file paths that are required to by the other
            scripts, and provides some functions which are handy for often used tasks:
            - Summing um list dictionaries (for 6 seed tasks) to provide mean seed deltas
            - creating file outputs
            - creating the folder infrastructure
            - calc DELs


==================================================================================================================== """

# Note: This file can only be imported if it exists within a directory listed in "sys.path"

if __name__ == '__main__':
    raise Exception('This script is only meant to be imported by other usage examples')

#import sys       # This provides Python system tools
import os        # This provides operating system (os) tools
import csv
import glob
import copy
import rainflow
import math
# from ANSFAB__Main_Control import MainFolder

### new and need parameter ###




# potentially obsolete:
##################################################################
# Main folder of the desired bladed runs ------------------------
MainFolder = r'3B_tow0_FA_damper_itr_inc_1P_Hz_filt'
##################################################################

nSeeds     = int(6)
nWindBins  = int(8) # 11  # is 11 for 5 to 25 with 2 m/s bins
nYawDrctns = range(1) #3
sum_relative_values = False

# time_total = 600  #time series length in s
# deltat = 0.02       # time step length in s
# nSectors = 12 # 24


nBlades = 2  # number of blades
rotor_weight_in_kg = 611273
if '3B' in MainFolder:
    nBlades = 3
    rotor_weight_in_kg = 636152  # in kg (default values: 3B ref ^= 636152 kg;)
else:
    nBlades = 2
    # in kg (default values: 2B101 ref ^= new:611273, old:589544 kg; 2B teeter ^= new:559097, old:578476)
    # rotor_weight_in_kg = 559097
    rotor_weight_in_kg = 611273

# main shaft bending loads at bearing
lever_length_in_m = 4.644    # in meter
gravitation = 9.81           # in m/s^2
calculate_drivetrain_bending = True


Desired_DEL_keys_and_order = ['Blade 1 My (Root axes)', 'Blade 1 Mx (Root axes)','Stationary hub Mx',
                              'Rotating hub Myz', 'Tower Mx ', 'Tower My ', 'Tower Mz ', 'Tower Myz'] # This was the old List ]

Desired_DEL_keys_and_order = ['Blade 1 My (Root axes)', 'Blade 1 Mx (Root axes)', 'Blade 1 Mz (Root axes)', 'Blade 1 Fz (Root axes)',
                              'Tower Mx ', 'Tower My ', 'Tower Mz ', 'Tower Myz',
                              'Rotating hub Mx ', 'Rotating hub My ', 'Rotating hub Mz ', 'Rotating hub Myz',
                              'Rotating hub Fx ', 'Stationary hub My ', 'Stationary hub Mz ',
                              'Yaw bearing Mx ', 'Yaw bearing My ', 'Yaw bearing Mz ', 'Yaw bearing Mxy',
                              'Yaw bearing Fx ', 'Yaw bearing Fy ', 'Yaw bearing Fz ']


MainFolderIsRunfolder = True

# PathMainFolder = os.path.join(os.getcwd(), 'DLC12_runs\\')+ '\\' + MainFolder
PathMainFolder = os.path.join(r'H:\BladedWS\FOWTs\\') + MainFolder
#PathMainRunFolder = os.path.join(r'F:\\', MainRunFolder)
#PathMainRunFolder = os.path.join(r'E:\itrWS\3D_PI', MainRunFolder)

print('Path to evaluated folder is ', PathMainFolder)
# ---------------------------------------------------------------

# Sub-folders --------------------------------------------------
PostProResultsFolder = os.path.join(PathMainFolder, 'PostPro')
PathMainRunFolder = os.path.join(PathMainFolder, 'runs')
if MainFolderIsRunfolder: PathMainRunFolder = PathMainFolder
TempSubFolder = os.path.join(PathMainRunFolder, 'temp')
SaveFolder = os.path.join(PathMainRunFolder, 'save_org_data')
# ---------------------------------------------------------------

# Checking inputs -----------------------------------------------
assert os.path.exists(PathMainRunFolder),\
    "Could not find main folder of the desired bladed runs. Please change the hard-coded value in the ANSFAB_Utility_fncts.py file."
# ---------------------------------------------------------------

def createFolderIfNotExcisting(newfolder):
    try:
        os.mkdir(newfolder)
    except OSError:
        print("Creation of the directory %s failed. Might already exist" % newfolder)
    else:
        print("Successfully created the directory %s " % newfolder)

#createFolderIfNotExcisting(PostProResultsFolder)
#createFolderIfNotExcisting(TempSubFolder)
#createFolderIfNotExcisting(SaveFolder)

def listRunNamesInFolder(RunFolder):
    # simply outputs a list of all bladed run files in the RunFolder (which all end on .$PJ)
    fileEnd = ".$PJ"
    if os.path.exists(RunFolder):
        RunPaths = glob.glob(RunFolder + '\*' + fileEnd)
        RunNames = []
        for Path in RunPaths:
            RunNames.append(Path.split('\\')[-1].split('.')[0])
        return RunNames
    else:
        print('ERROR: Run folder does not exist')

def searchForBladedOutputParams(RunFolder, RunNames, Params, StructureIsStatic = True):
    # The task is to read through the list of Params and add changing parameters as
    # bladed output dimension, file extension, index of output variable etc.

    for idx_Param, Param in enumerate(Params):
        for RunName in RunNames:
            DescriptionFiles = glob.glob(RunFolder + '\\' + RunName + '.%*')  # collecting all description files of one run
            for DescriptionFile in DescriptionFiles:
                csv_data = csv.reader(open(DescriptionFile), delimiter=' ')

                for row in csv_data:
                    row_joined = ' '.join(row)

                    if row_joined.find('DIMENS') != -1:  # search and store outfile dimensions
                        DIMENS = row[0].split('\t')[1:]

                    if row_joined.find('GENLAB') != -1:  # search for general identifier
                        if row_joined.find(Param.get('GENLAB')) != -1:  # search for specific identifier
                            print('found: ' + Param.get('GENLAB'))
                            Params[idx_Param]['FILENUMBER'] = DescriptionFile.split('.%')[-1]
                            Params[idx_Param]['DIMENS'] = DIMENS
                        else:
                            break  # to avoid wrong storing of parameters

                    if row_joined.find('VARIAB') != -1:  # search for index of identifier
                        Variables = row_joined.split('\'')[1::2]  # list of output variables
                        for idx_Variable, Variable in enumerate(Variables):
                            #if Variable.find(Param.get('VARIAB')) != -1:
                            if Variable == Param.get('VARIAB'):
                                # print('found:' + Variable)
                                Params[idx_Param]['VARIAB_IDX'] = idx_Variable

                    if row_joined.find('STEP') != -1:  # search for time step length
                        TimeStep = float(row_joined.split('\t')[-1])
                        Params[idx_Param]['STEP'] = TimeStep

            if StructureIsStatic:  # should be used, if, e.g., different output parameters are present
                break
    return Params

def readTimeSeries(RunFolder, RunNames, Params):
    # reads in the time series of every variable in Params and stores those in Params
    for idx_Param, Param in enumerate(Params):
        list_of_time_series = []
        for RunName in RunNames:
            time_series = []
            file = os.path.join(RunFolder, RunName) + '.$' + str(Param.get('FILENUMBER'))
            csv_data = csv.reader(open(file), delimiter=' ')

            line_count = 0
            load_count = 0

            Dimensions = [int(i) for i in Param.get('DIMENS')]
            if len(Dimensions)>2:
                StaggeringIndex = Dimensions[1] # end 2 of last member.
            else:
                StaggeringIndex = 1

            Steps = Dimensions[-1]
            for row in csv_data:
                if load_count < Steps:
                    if line_count == StaggeringIndex - 1 + load_count * StaggeringIndex:  # currently only chooses end 2 of last member.
                        row = list(filter(None, row))
                        time_series.append(float(row[Param.get('VARIAB_IDX')]))
                        load_count = load_count + 1
                line_count = line_count + 1
            list_of_time_series.append(time_series)
        Params[idx_Param]['TIMESERIES'] = list_of_time_series
    return Params



def sumAndNormSeedsOfIterations(ListDict, nSeeds=6, JustSumKey='None' ): # input: List Dictionary, number of seeds and an exception where the values should only be normed
    if not sum_relative_values:
        return [{}], [{}]
    runs_info_file = glob.glob(os.path.join(PathMainFolder, 'base_prj_files') + '\*.csv')[0]
    print('Opening runs info file ', runs_info_file)
    file_data = csv.reader(open(runs_info_file), delimiter=',')

    runs_info = []
    info_keys = []
    cnt = 0
    PosOfReference = 0
    for row in file_data:
        if not info_keys:
            info_keys = row
            # print('info_keys are ', info_keys)
        else:
            runs_info.append(dict(zip(info_keys, row)))
            if float(runs_info[cnt].get(info_keys[1])) == 1 and float(runs_info[cnt].get(info_keys[2])) == 1 and PosOfReference == 0:
            #if (float(runs_info[cnt].get(info_keys[1])) == 1 and float(runs_info[cnt].get(info_keys[2])) == 1 or float(runs_info[cnt].get(info_keys[1])) == 0) and PosOfReference == 0:
                PosOfReference = cnt
                print('If necessary check position of gain factors 1 and 1! Here position ', PosOfReference)
            cnt += 1

    print(ListDict[0].keys())

    Value_Alarms = []
    Alarm_keys = ['RunNumber', 'RunName', 'seedNumber', 'Component', 'Value', 'Value_ref', 'relativeIncrease']
    eps = 0.5  # percentage of error tolerance without an error message
    iterationCases = int(len(ListDict) / nSeeds)
    ListDict_summed = [dict(zip(ListDict[0].keys(), range(len(ListDict[0].keys())))) for cnt in
                         range(iterationCases)]
    for cnt in range(iterationCases):
        for key in ListDict[0].keys():
            Sum = 0
            for nSeed in range(nSeeds):
                Value = float(ListDict[cnt + iterationCases * nSeed].get(key))
                Value_ref = float(ListDict[PosOfReference + iterationCases * nSeed].get(key))
                if Value_ref == 0: Value_ref = 0.00000000001
                #if Value_ref == 0:
                #    Value_ref = 1
                #    Value = 1
                if JustSumKey in key:
                    Value_ref = 1
                Sum += Value / Value_ref
                if (Value - Value_ref) / Value_ref > eps:
                    #print('Run ', cnt + iterationCases * nSeed, 'of ', key, 'got a Value of ', Value,
                    #      'with a relative difference of ', (Value - Value_ref) / Value_ref, ' to ', Value_ref)
                    Value_Alarms.append(dict(zip(Alarm_keys, [cnt + iterationCases * nSeed,
                                            #runs_info[cnt].get(info_keys[0]),
                                            runs_info[cnt + iterationCases * nSeed].get(info_keys[0]),
                                            nSeed, key, Value, Value_ref, (Value-Value_ref)/Value_ref ])))

            ListDict_summed[cnt][key] = Sum / nSeeds
    return ListDict_summed, Value_Alarms

def sumSeedsOfIterations(ListDict, nSeeds=6): # input: List Dictionary, number of seeds
    print(ListDict[0].keys())

    iterationCases = int(len(ListDict) / nSeeds/ nWindBins/len(nYawDrctns))
    if len(nYawDrctns) > 1: print(iterationCases, 'iterationCase(s) should be 1 ')
    ListDict_summed = [dict(zip(ListDict[0].keys(), range(len(ListDict[0].keys())))) for cnt in
                         range(iterationCases * nWindBins * len(nYawDrctns))]
    for nYawDrctn in nYawDrctns:
        for nWindBin in range(nWindBins):  # for nWindBin in nWindBins:
            for cnt in range(iterationCases):
                for key in ListDict[0].keys():
                    Sum = 0
                    for nSeed in range(nSeeds):
                        Value = float(ListDict[cnt + iterationCases*(nSeed + nSeeds*(nWindBin + nWindBins*nYawDrctn))].get(key))
                        Sum += Value
                    ListDict_summed[cnt + iterationCases * (nWindBin + nWindBins*nYawDrctn)][key] = Sum / nSeeds
    return ListDict_summed


def writeListDictToCSV(ListDict, fileNamePath):
    print('writing output in ', fileNamePath)
    if len(ListDict) == 0:
        print('List dictionary is empty. No output file ', fileNamePath, ' is generated.')
        return
    with open(fileNamePath, 'w', newline='') as output_file:
        dict_writer = csv.DictWriter(output_file, ListDict[0].keys())
        dict_writer.writeheader()
        dict_writer.writerows(ListDict)








################################################# DEL - Section ########################################################
def calcDELfromTimeSeries(timeSeries, time_total = 600, k = 4.0, Referenz_Frequency = 1.0, var_nbins = 100):
    # parameter for DEL calculation
    # Referenz_Frequency = 1.0  # Hz
    Nreff = time_total * Referenz_Frequency  # 600 #
    # k = 4.0  # Woehler exponent for steel extremely important that this is a float!!!!
    # var_nbins = 100

    #print('MOST IMPORTANT DEL PARAMETER: Woehler Exp: ', k, ', ref frequency: ', Referenz_Frequency,
    #      ', ref cycles: ', Nreff, ' and numbers of bins is: ', var_nbins)

    DEL = 0.0
    if timeSeries: # just to be sure that its not emtpy
        RFC = copy.copy(rainflow.count_cycles(timeSeries, nbins=var_nbins))
        for bin in range(var_nbins):
            DEL += copy.copy(RFC[bin][1] * (math.pow(RFC[bin][0], k)))
        DEL = copy.copy(math.pow(DEL / Nreff, 1/k))
    return DEL

def calcWorstDELsector(Mx_timeSeries, My_timeSeries, time_total = 600, nSectors = 12, eps = 0.001 ):
    # sum moment vectors in fixed directions of n Sectors
    # eps for accuracy of factor to not divide by zero
    My_timeSeries_Sector = [[] for n in range(nSectors)]  # np.empty([nSectors, int(time_total / deltat + 10)])
    DEL_Sector = [0 for kk in range(nSectors)] # np.empty(nSectors)
    DEL_max = 0
    n_max = 0
    for n in range(nSectors):
        for timeStep in range(len(Mx_timeSeries)):
            if abs(float(My_timeSeries[timeStep])) > 0:
                alpha = copy.copy(math.atan(float(Mx_timeSeries[timeStep]) / float(My_timeSeries[timeStep])))
            else:
                alpha = copy.copy(math.atan(float(Mx_timeSeries[timeStep]) / eps))
                print('if this is never triggered, this expression is useless...')
            My_timeSeries_Sector[n].append(math.sqrt(math.pow(Mx_timeSeries[timeStep], 2) + math.pow(My_timeSeries[timeStep], 2))\
                         * math.cos(math.pi / nSectors * n - alpha) * math.copysign(1, My_timeSeries[timeStep]))

        DEL_Sector[n] = calcDELfromTimeSeries(My_timeSeries_Sector[n][:], time_total)
        if DEL_Sector[n] > DEL_max:
            DEL_max = copy.copy(DEL_Sector[n])
            n_max = n

    # Further evalutations:
    Mxy_timeSeries = [math.sqrt(math.pow(Mx_timeSeries[kk], 2) + math.pow(My_timeSeries[kk], 2)) for kk in range(len(Mx_timeSeries))]
    DELx = calcDELfromTimeSeries(Mx_timeSeries, time_total)
    DELy = calcDELfromTimeSeries(My_timeSeries, time_total)
    DEL_ref = calcDELfromTimeSeries(Mxy_timeSeries, time_total)

    if PrintDetails:
        print('Reference DEL:', DEL_ref, '; -> maximum DEL', DEL_Sector[n_max], ' found in Sector', n_max,
              'with a delta of', round((DEL_Sector[n_max]-DEL_ref)/DEL_ref * 100, 2), '% to the baseline. DEL_Mx is ',
              DELx, ' and DEL_My ', DELy)

    eps2 = 100
    if DEL_Sector[n_max]-DELy < -eps2 or DEL_Sector[n_max]-DELx < -eps2:
        print('WARNING: Worst DEL ', DEL_Sector[n_max], ' MUST NOT be smaller than My_DEL ', DELy, ' or Mx_DEL ', DELx, '!!!')
        DEL_Sector[n_max] = max(DELy, DELx)

    # keys = ['runName', 'DEL_Mx', 'DEL_My', 'ref_DEL_Mxy', 'new_max_DEL_Mxy', 'sector', 'rel_difference']
    # MainResults.append(dict(zip(keys, [file, str(DELx), str(DELy), str(DEL_ref), str(DEL_Sector[n_max]), str(n_max), str(round((DEL_Sector[n_max]-DEL_ref)/DEL_ref * 100, 2))])))

    return DEL_Sector[n_max]

