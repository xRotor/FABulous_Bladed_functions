""" ====================================================================================================================

                                           Collection of Utility functions
                         ------------------------------------------------------------------

     Basic functions mostly necessary for Bladed workflow
     Also GA (Genetic algorithm) functions are stored here: reproduction, crossover, mutation, bit_string_to_parameter

==================================================================================================================== """
# import random
import numpy.random as random
import numpy as np
from copy import copy
import sys
import os
import csv
import math
import rainflow
import glob
import copy
import clr
import matplotlib.pyplot as plt
from matplotlib import cm
from datetime import datetime

# import config parameters
from config import nBlades, nSectors, runFileEnd, towerFileEnd, hubFileEnd, PrintDetails, addToRunFileNames, \
                   eps, Referenz_Frequency, k_steel, var_nbins, DEL_keys, TowerNodePosition, ListOfBaselineFiles, \
                   baselineFolder, searchWords, CostShares, max_rotation_speed, MainPathToBladedRuns


Nreff = -1e20   # has to be positive and will later on re-assigned

# ----------------------------------------------------------------------------------------------------------------
class Utility:
    def collectTimeSeriesFromBladedFiles(self, RunFolder, BladedJob, VariableName):
        # search through files to catch right time series (make this a function later on!)
        InfoFiles = glob.glob(RunFolder + '\\' + BladedJob.split('.')[0] + '.%*')
        if PrintDetails:
            print('Found: ', InfoFiles)

        # foundIt = False
        counter = 0
        for InfoFile in InfoFiles:
            csv_data = csv.reader(open(InfoFile), delimiter='\t')
            for row in csv_data:
                if row[0] == 'DIMENS':  # need to be stored before, because it is marked in the lines above VARIAB
                    DIMENS = row[1:]
                if row[0] == 'VARIAB':  # old alternative: if row[0].find('VARIAB') != -1:
                    for idx, Parameter in enumerate(row[1].split('\' ')):
                        if Parameter.replace('\'', '') == VariableName:
                            fileEnd = '.$' + InfoFile.split('.%')[-1]
                            if PrintDetails and counter == 0:
                                print('found (', Parameter.replace('\'', ''), ') at index ', idx,
                                      ' in file with ending: ', fileEnd, ' and dimensions: ', DIMENS)
                            counter += 1
                            # DEL_dict['VARIAB_IDX'] = idx
                            # DEL_dict['DIMENS'] = DIMENS
                            # DEL_dict['fileEnd'] = fileEnd
                            ## foundIt = True
                # if foundIt:
                #    break
        # if PrintDetails and counter > 1:
        #     print('WARNING: There might be a false friend in the data. There is more then one variable with the same name!!!')
        return [fileEnd, idx, DIMENS]

    def calcTotalTimeAndDeltat(self, RunFolder, BladedJob):
        [fileEnd, idx, DIMENS] = self.collectTimeSeriesFromBladedFiles(RunFolder, BladedJob, 'Time from start of simulation')
        TimeFileEnd = fileEnd  # '.$07'  # alternative: '.$04'
        file = os.path.join(RunFolder, BladedJob.split('.')[0] + TimeFileEnd)
        try:
            csv_data = csv.reader(open(file), delimiter=' ')
            TimeTimeSeries = []  # Time series of the time in s
            for row in csv_data:
                row = list(filter(None, row))
                TimeTimeSeries.append(float(row[0]))
            globals()['time_total'] = time_total = TimeTimeSeries[-1] - TimeTimeSeries[0]
            globals()['deltat'] = deltat = round(TimeTimeSeries[1] - TimeTimeSeries[0], 3)
            globals()['Nreff'] = Nreff = time_total * Referenz_Frequency
        except OSError:
            print('cannot find time file: ', file, '. Will use default values.')

        if PrintDetails:
            print('simulation length is ', time_total, 's with a time step length of ', deltat, 's')
            print('Sector width = ' + str(180 / nSectors) + 'deg')
            print('MOST IMPORTANT DEL PARAMETER: Woehler Exp: ', k_steel, ', ref frequency: ', Referenz_Frequency,
                  ', ref cycles: ', Nreff, ' and numbers of bins is: ', var_nbins)

        return [time_total, deltat]

    def readTimeSeriesData(self, RunFolder, BladedJob, fileEnd, idx, DIMENS):
        # search through the desired time series
        file = RunFolder + '\\' + BladedJob.split('.')[0] + fileEnd
        try:
            csv_data = csv.reader(open(file), delimiter=' ')
        except OSError:
            print('cannot find ', file, '. Will skip and set value to 0.')

        TimeSeries = []
        if len(DIMENS) == 3:  # otherwise the third dimension is missing in the 2D csv data file
            dimenTwo = float(DIMENS[1])
            pos_of_note = TowerNodePosition  # some members have two notes; all notes of a single time step are
        else:
            dimenTwo = 1
            if PrintDetails and TowerNodePosition > 1:
                print('file with ending ', fileEnd,
                      ' should not have multiple stacked nodes! Will set node position to 1')
            pos_of_note = 1

        line_count = 0
        load_count = 0
        # nheader = 0
        for row in csv_data:
            # if load_count < int(time_total / deltat) + 1:  # nheader:
            if line_count == load_count * dimenTwo + pos_of_note - 1:
                row = list(filter(None, row))
                # time[line_count-nheader] = row[0]
                TimeSeries.append(float(row[idx]))
                load_count = load_count + 1
            # else: print('overshooting lines')
            line_count = line_count + 1

    def calcDELfromTimeSeries(self, timeSeries, k):
        DEL = 0.0
        if timeSeries:  # just to be sure that its not emtpy
            RFC = copy.copy(rainflow.count_cycles(timeSeries, nbins=var_nbins))
            for bin in range(var_nbins):
                DEL += copy.copy(RFC[bin][1] * (math.pow(RFC[bin][0], k)))
            DEL = copy.copy(math.pow(DEL / Nreff, 1 / k))
        return DEL

    def calcWorstDELsector(self, Mx_timeSeries, My_timeSeries, nSectors, MainResults, file):
        # sum moment vectors in fixed directions
        My_timeSeries_Sector = [[] for n in range(nSectors)]  # np.empty([nSectors, int(time_total / deltat + 10)])
        DEL_Sector = [0 for kk in range(nSectors)]  # np.empty(nSectors)
        DEL_max = 0
        n_max = 0
        for n in range(nSectors):
            for timeStep in range(len(Mx_timeSeries)):
                if abs(float(My_timeSeries[timeStep])) > 0:
                    alpha = copy.copy(math.atan(float(Mx_timeSeries[timeStep]) / float(My_timeSeries[timeStep])))
                else:
                    alpha = copy.copy(math.atan(float(Mx_timeSeries[timeStep]) / eps))
                    print('if this is never triggered, this expression is useless...')
                My_timeSeries_Sector[n].append(
                    math.sqrt(math.pow(Mx_timeSeries[timeStep], 2) + math.pow(My_timeSeries[timeStep], 2)) \
                    * math.cos(math.pi / nSectors * n - alpha) * math.copysign(1, My_timeSeries[timeStep]))

            DEL_Sector[n] = self.calcDELfromTimeSeries(My_timeSeries_Sector[n][:], k_steel)
            if DEL_Sector[n] > DEL_max:
                DEL_max = copy.copy(DEL_Sector[n])
                n_max = n

        # Further evalutations:
        Mxy_timeSeries = [math.sqrt(math.pow(Mx_timeSeries[kk], 2) + math.pow(My_timeSeries[kk], 2)) for kk in
                          range(len(Mx_timeSeries))]
        DELx = self.calcDELfromTimeSeries(Mx_timeSeries, k_steel)
        DELy = self.calcDELfromTimeSeries(My_timeSeries, k_steel)
        DEL_ref = self.calcDELfromTimeSeries(Mxy_timeSeries, k_steel)

        if PrintDetails:
            print('Reference DEL:', DEL_ref, '; -> maximum DEL', DEL_Sector[n_max], ' found in Sector', n_max,
                  'with a delta of', round((DEL_Sector[n_max] - DEL_ref) / DEL_ref * 100, 2),
                  '% to the baseline. DEL_Mx is ',
                  DELx, ' and DEL_My ', DELy)

        eps2 = 100
        if DEL_Sector[n_max] - DELy < -eps2 or DEL_Sector[n_max] - DELx < -eps2:
            print('WARNING: Worst DEL ', DEL_Sector[n_max], ' MUST NOT be smaller than My_DEL ', DELy, ' or Mx_DEL ',
                  DELx, '!!!')
            DEL_Sector[n_max] = max(DELy, DELx)

        # keys = ['runName', 'DEL_Mx', 'DEL_My', 'ref_DEL_Mxy', 'new_max_DEL_Mxy', 'sector', 'rel_difference']
        # MainResults.append(dict(zip(keys, [file, str(DELx), str(DELy), str(DEL_ref), str(DEL_Sector[n_max]), str(n_max), str(round((DEL_Sector[n_max]-DEL_ref)/DEL_ref * 100, 2))])))

        return DEL_Sector[n_max]  # , MainResults


    def createFolderIfNotExcisting(self, newfolder):
        try:
            os.mkdir(newfolder)
        except OSError:
            print("Creation of the directory %s failed. Might already exist" % newfolder)
        else:
            print("Successfully created the directory %s " % newfolder)

    def writeListDictToCSV(self, ListDict, fileNamePath):
        #print('writing output in ', fileNamePath)
        if len(ListDict) == 0:
            print('List dictionary is empty. No output file ', fileNamePath, ' is generated.')
            return
        # with open(fileNamePath, 'w', newline='') as output_file:
        ''' # Works only with Python 3
        with open(fileNamePath, 'w') as output_file:
            dict_writer = csv.DictWriter(output_file, ListDict[0].keys())
            dict_writer.writeheader()
            dict_writer.writerows(ListDict)'''
        try:
            if sys.version_info[0] < 3:
                # Works only with Python 2
                output_file = open(fileNamePath, 'wb')
                dict_writer = csv.DictWriter(output_file, ListDict[0].keys())
                dict_writer.writeheader()
                dict_writer.writerows(ListDict)
                output_file.close()
            else:  # Works only with Python 3
                with open(fileNamePath, 'w', newline='') as output_file:
                    dict_writer = csv.DictWriter(output_file, ListDict[0].keys())
                    dict_writer.writeheader()
                    dict_writer.writerows(ListDict)
        except OSError:
            print('could not write output. File might be open')
        else:
            print('writing output in ' + fileNamePath)

    def readListDictFromCSV(self, fileNamePath):
        # with open(fileNamePath, 'w', newline='') as output_file:
        ''' # Works only with Python 3
        with open(fileNamePath, 'w') as output_file:
            dict_writer = csv.DictWriter(output_file, ListDict[0].keys())
            dict_writer.writeheader()
            dict_writer.writerows(ListDict)'''
        try:
            if sys.version_info[0] < 3:
                # Works only with Python 2
                print('Python 2 is currently not supported.')
            else:  # Works only with Python 3
                with open(fileNamePath, 'r', newline='') as input_file:
                    file_dict = csv.DictReader(input_file)
                    list_dict = []
                    for row in file_dict:
                        list_dict.append(row)
        except OSError:
            print('could not write output. File might be open')
        else:
            print('reading in ' + fileNamePath)
        return list_dict

    def calcMeanValuesForSeeds(self, ListOfDicts, nSeeds = -1):
        if nSeeds < 0:
            nSeeds = int(len(ListOfDicts))
            nPopulation = 1
        else:  # nPopulation is a relict of genetic algorithms and used, when multiple runs with nSeeds are performed.
            nPopulation = int(len(ListOfDicts)/nSeeds)
        Keys = ListOfDicts[0].keys()
        New_ListOfDicts = [dict(zip(Keys, range(len(Keys)))) for _ in range(nPopulation)]
        for key in Keys:
            for nPopu in range(nPopulation):
                MeanValue = 0.0
                for nSeed in range(nSeeds):
                    MeanValue += ListOfDicts[nPopu + nPopulation * nSeed].get(key)
                MeanValue = MeanValue/nSeeds
                New_ListOfDicts[nPopu][key] = copy(MeanValue)
        return New_ListOfDicts

    def calcCCC(self, Statistics_n_DELs, ref_Statistics_n_DELs):
        if not Statistics_n_DELs.get(DEL_keys[0]):
            print('Error while evaluating the CCC! Will set CCC to 20!')
            CCC = 20  # This is necessary if bladed run did not work properly. This CCC will be "ignored"
        if Statistics_n_DELs.get('RotationSpeed_max') > max_rotation_speed:
            print('Maximum rotation speed exceeds the limit! Will set CCC to 20!')
            CCC = 20  # To avoid over speed
        else:
            CCC = 1
            CCC += ((Statistics_n_DELs.get('Blade_My_DEL') / ref_Statistics_n_DELs.get('Blade_My_DEL')   - 1))          * CostShares.get('Blade_costs')
                  # +  Statistics_n_DELs.get('Blade_My_max')  / ref_Statistics_n_DELs.get('Blade_My_max')) / 2 - 1)     * CostShares.get('Blade_costs') \
            CCC += (Statistics_n_DELs.get('Hub_Mx_DEL') / ref_Statistics_n_DELs.get('Hub_Mx_DEL') - 1)                  * CostShares.get('DriveTrain_costs')
            CCC += (Statistics_n_DELs.get('Tower_My_sector_max_DEL') / ref_Statistics_n_DELs.get('Tower_My_sector_max_DEL') - 1) * CostShares.get('Tower_costs')
            CCC -= (Statistics_n_DELs.get('Power_mean') / ref_Statistics_n_DELs.get('Power_mean') - 1)                  * CostShares.get('CoE_CAPEX_ratio')
            # might be better if any derivation of the power from mean gets punished:       + abs(Statistics_n_DELs.get('Power_mean') / ref_Statistics_n_DELs.get('Power_mean') - 1)
            #    + (Statistics_n_DELs.get('Pitch_LDC') / ref_Statistics_n_DELs.get('Pitch_LDC') - 1)
            #        * CostShares.get('PitchSys_costs'))  # might be over estimated (better use energy consumption or leave away)
        return CCC

    def manipulatePRJfiles(self, Params, Iteration_integer = '',  searchWords_local = searchWords,
               ListOfBaselineFiles_local = ListOfBaselineFiles, infolder= baselineFolder, outfolder='', ChangeDicts=[]):
        # this function should manipulate bladed project files. Most variables are defined in config.py
        # if a specific line should be changed (that is not external controller typical) use the ChangeDict option, e.g.
        # ChangeDicts.append({'WORD': 'ENDT	 ', 'EXCHANGE': 'ENDT	 320'}), will be ignored if empty (analogue to Params)

        try:
            Params[1][0]
        except:
            if ChangeDicts:
                if len(ChangeDicts) == 1:
                    MultipleRuns = True
            elif len(searchWords_local) == 1:
                MultipleRuns = True
            MultipleRuns = False
        else:
            MultipleRuns = True  # if Params is 2-dimensional than its clearly for two runs

        if MultipleRuns:
            nRuns = len(Params)
            nValues = len(Params[0])
        else:
            nRuns = 1
            nValues = len(Params)

        if not outfolder:
            from datetime import datetime
            outfolder = MainPathToBladedRuns # os.path.join(infolder, datetime.today().strftime('%Y_%m_%d__') + addToRunFileNames[0] + '\\')
        self.createFolderIfNotExcisting(outfolder)

        if Iteration_integer:
            addIterationString = '_g' + str(Iteration_integer) + '_'
        else:
            addIterationString = ''


        outfileNames = []
        for idx_baselinefile, fileName in enumerate(ListOfBaselineFiles_local):
           # for value in Params:
            for idx_run in range(nRuns):

                addToRunFileNamesValues = ''
                addForMoreValues = ''
                for idx_value in range(nValues):
                    try:
                        Value = Params[idx_run][idx_value]
                    except:
                        Value = Params[idx_value]
                    #addToRunFileNamesValues += addForMoreValues + str('%.02f' % Value).replace('.', '_')
                    addToRunFileNamesValues += addToRunFileNames[idx_value] + str('%.02f' % Value).replace('.', '_')
                    addForMoreValues = '__'

                NameAdd = addIterationString + addToRunFileNamesValues  # '.prj'

                # infileName = ListOfBaselineOldFiles[idx].replace(fileEnd, '')
                # outfileName = fileName.replace(fileEnd, '')
                infileName = fileName.replace(runFileEnd, '')
                outfileName = fileName.replace(runFileEnd, '') + NameAdd
                if len(outfileName) > 52:
                    print('outfile name ' + outfileName + ' is too long for Bladed (>52). Thus shortened to ' + outfileName[0:51])
                    outfileName = outfileName[0:41]
                outfileNames.append(outfileName + runFileEnd)

                if PrintDetails:
                    print('new filename is: ' + outfileName + ' with length ' + str(len(outfileName)))

                infile = open((os.path.join(infolder, infileName) + '.$PJ'), "r")
                outfile = open((os.path.join(outfolder, outfileName) + '.$PJ'), "w")

                for row in infile:
                    if row.find(infileName) != -1:
                        row = '  <Name>' + outfileName + '</Name>\n'

                    if ChangeDicts:
                        for idx_value, Dict in enumerate(ChangeDicts):
                            if row.find(Dict.get('WORD')) != -1:
                                print('was: ' + row)
                                row = Dict.get('EXCHANGE') + '\n'  # + str(value) + ';' + '\n'
                                print('is now: ' + row)
                    else:
                        for idx_value, Word in enumerate(searchWords_local):
                            if row.find(Word) != -1:
                                if PrintDetails:
                                    print('was: ' + row)
                                try:
                                    row = row.split(Word)[0] + Word + '=' + str(Params[idx_run][idx_value]) + ';' + '\n'
                                except:
                                    row = row.split(Word)[0] + Word + '=' + str(Params[idx_value]) + ';' + '\n'
                                if PrintDetails:
                                    print('is now: ' + row)
                    outfile.write(row)

                outfile.close()
                infile.close()

        return outfileNames, outfolder

    # evaluates folder with bladed runs by collecting all job names, parsing files through evaluation functions
    # and wrtiting to a CSV file
    def evaluateFolder(self, folderPlusFirstSnip):
        ListOfBladedJobs = []
        for run_file in glob.glob(folderPlusFirstSnip + '*.$PJ'):
            # ListOfBladedJobs.append(dict(zip(['run_name'], [''.join(run_file)])))
            ListOfBladedJobs.append(run_file.split('\\')[-1])  # .split('.')[0])

        print('job names are: ', ListOfBladedJobs)

        RunFolder = os.path.dirname(folderPlusFirstSnip)
        RunFolderName = RunFolder.split('\\')[-1]

        print('# ----------- starting with run evaluation ------------- #')
        Statistics = Bladed().extractStatisticalBladedResultsData(RunFolder, ListOfBladedJobs)
        DEL_dicts = Bladed().extractDEL_towerHubBlade(RunFolder, ListOfBladedJobs)

        EvaluationDicts = [{'BladedJobName': RunName} for RunName in ListOfBladedJobs]
        [EvaluationDicts[i].update(DEL_dicts[i]) for i in range(len(DEL_dicts))]
        [EvaluationDicts[i].update(Statistics[i]) for i in range(len(DEL_dicts))]

        # Keys that are saved to file in this specific order
        Docu_keys = ['BladedJobName', 'Blade_Mx_DEL', 'Blade_My_DEL', 'Blade_Mz_DEL', 'Blade_Fz_DEL',  # 'Blade_My_max',
                     'Tower_Mx_DEL', 'Tower_My_DEL', 'Tower_My_sector_max_DEL', 'Tower_Mz_DEL',
                     'Hub_Mx_DEL', 'Hub_My_DEL', 'Hub_Mz_DEL', 'Hub_Myz_sector_max_DEL',
                     'Power_mean', 'Pitch_LDC', 'mean_Thrust_Hub_Fx', 'mean_Platform_Pitch', 'max_Platform_Pitch',
                     'max_mooring_tension', 'max_Nacelle_FA_accel']

        Documentation = [{Key: Dict[Key] for Key in Docu_keys} for Dict in EvaluationDicts]
        # print(Documentation)

        outfileName = os.path.join(RunFolder, RunFolderName + '_' + datetime.today().strftime('%Y_%m_%d__') + '_DEL_evaluation.csv')
        Utility().writeListDictToCSV(Documentation, outfileName)

    def searchForEqualStringSequencesInRunNames(self, RunNames):
        # searching for the first sequence of chars that is equal for all run names
        RunNameRef = RunNames[0] # list_dict[0].get(keys[0])
        EqualChars_idx = 1
        for RunName in RunNames:
            for idx in range(len(RunName)):
                if RunName[:-EqualChars_idx] == RunNameRef[:-EqualChars_idx]:
                    if RunName[-EqualChars_idx - 1] == '_' or RunName[-EqualChars_idx - 1].isnumeric():
                        EqualChars_idx += 1
                    break
                else:
                    EqualChars_idx += 1
        FirstSplittingSequences = RunNameRef[:-EqualChars_idx]
        # searching for the second sequence of chars that is equal for all run names
        # first filter out the first numerical content (the start of SecondSplittingSequences)
        for idx, Char in enumerate(RunNameRef[-EqualChars_idx:]):
            if Char.isalpha() and Char != '_':
                if RunNameRef[-EqualChars_idx + idx - 1] == '_':
                    idx = idx - 1
                break
        # than search for the next numerical content (the end of SecondSplittingSequences)
        SecondSplittingSequences = RunNameRef[-EqualChars_idx + idx:]
        for idx, Char in enumerate(SecondSplittingSequences):
            if Char.isnumeric():
                break
        SecondSplittingSequences = SecondSplittingSequences[:idx]
        return FirstSplittingSequences, SecondSplittingSequences

    # this function reads in the dictionary data from a csv file and loads it into a 3-D surface plot
    def readAndPlotThreeDimensionalDataFromCSVfile(self, filePath, EvaluationKeys = ['all'], WritePlotData = True, Plot = True):
        # loading data from file
        list_dict = self.readListDictFromCSV(filePath)

        keys = list(list_dict[0].keys())
        if PrintDetails:
            print('dict keys are: ', keys)

        # searching for the first sequence of chars that is equal for all run names
        RunNames = [Dict.get(keys[0]) for Dict in list_dict]
        FirstSplittingSequences, SecondSplittingSequences = self.searchForEqualStringSequencesInRunNames(RunNames)

        if EvaluationKeys[0] == 'all':
            EvaluationKeys = keys[1:]

        for key_idx, EvaluationKey in enumerate(EvaluationKeys):
            # restoring data in two-dimensional field
            X = []
            Y = []
            Z = []
            for idx, Dict in enumerate(list_dict):
                RunName = Dict.get(keys[0])
                X.append(float(RunName.split(FirstSplittingSequences)[1].split(SecondSplittingSequences)[0].replace('_', '.')))
                Y.append(float(RunName.split(FirstSplittingSequences)[1].split(SecondSplittingSequences)[1].split('.')[0].replace('_', '.')))
                Z.append(float(Dict.get(EvaluationKey)))

            save_x = X[0]
            for idx, x in enumerate(X):
                if save_x != x:
                    xdimension = idx
                    # print('X-Dimension is', xdimension)
                    break

            X = np.array(X)
            Y = np.array(Y)
            Z = np.array(Z)

            X = np.reshape(X, (-1, xdimension))
            Y = np.reshape(Y, (-1, xdimension))
            Z = np.reshape(Z, (-1, xdimension))



            if Plot:
                fig, ax = plt.subplots(subplot_kw={"projection": "3d"})
                # Plot the surface.
                surf = ax.plot_surface(X, Y, Z,  cmap=cm.coolwarm,
                                       linewidth=0, antialiased=False, vmin=Z.min(), vmax=min(Z.min()*1.5, Z.max()))

                # Customize the z axis.
                # ax.set_zlim(Z.min(), min(Z.min()*1.5, Z.max()))
                # use to set fixed number of axis values
                # from matplotlib.ticker import LinearLocator
                # ax.zaxis.set_major_locator(LinearLocator(10))
                # A StrMethodFormatter is used automatically
                # ax.zaxis.set_major_formatter('{x:.02f}')

                # Add a color bar which maps values to colors.
                useColorBar = False
                if useColorBar:
                    fig.colorbar(surf, shrink=0.5, aspect=20)

                # Add a legend
                ax.set_xlabel(FirstSplittingSequences.split('_')[-1])
                ax.set_ylabel(SecondSplittingSequences.split('_')[-1])
                ax.set_title(EvaluationKey)

                plt.draw()
        if Plot:
            plt.show()

        return X, Y, Z


'''
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
        
    def writeListDictToCSV(ListDict, fileNamePath):
        print('writing output in ', fileNamePath)
        if len(ListDict) == 0:
            print('List dictionary is empty. No output file ', fileNamePath, ' is generated.')
            return
        with open(fileNamePath, 'w', newline='') as output_file:
            dict_writer = csv.DictWriter(output_file, ListDict[0].keys())
            dict_writer.writeheader()
            dict_writer.writerows(ListDict)
'''





class Bladed:
    # def __init__(self): #, BASE_RESULTS_DIRECTORY, PROJECT_FILE_PATH):
    def AutoRunBatch(self, PathToBladedRuns, ListOfBladedJobs):

        if not ListOfBladedJobs:
            print('Job list is empty. No new runs performed.')
            return 42

        # Bladed installation directory here -----------------------
        BLADED_INSTALL_DIR = r"C:\DNV\Bladed 4.13"
        # ---------------------------------------------------------------
        sys.path.append(BLADED_INSTALL_DIR)  # This allows the import of the .Net dlls in the Bladed install directory
        clr.AddReference("GH.Bladed.Api.Facades")  # This loads the dll which provides the Bladed API into Python
        from GH.Bladed.Api.Facades.EntryPoint import \
            Bladed  # This imports the entry point to the Bladed API into this script

        if not PrintDetails:
            Bladed.LoggingSettings.LogToConsole = False  # Controls whether logs are output to the console
        # ---------------------------------------------------------------

        # Start batch framework, set the working directory and job list--
        print("Starting the Batch Framework...\n")
        Bladed.BatchApi.StartFramework()
        #Bladed.BatchApi.SetDirectory(r'C:\DNV\Batch\DefaultBatchDirectory')
        Bladed.BatchApi.SetJobList("optimization")
        # ---------------------------------------------------------------

        # Redirect log file output (useful for debugging purposes)
        Bladed.LoggingSettings.LogFilePath = os.path.join(PathToBladedRuns, r"Bladed_API_Log.txt")

        # Suppress warning messages and allow outputs to be overwritten
        Bladed.ProjectApi.Settings.OverwriteOutputs = True
        Bladed.ProjectApi.Settings.SuppressAllMessageBoxesByChoosingDefaultOption = True

        print('# -------- loading runs into job list ---------- #')
        # PrintList = ''
        try:
            # load job(s) into the batch queue
            for idx, JobName in enumerate(ListOfBladedJobs):
                #JobName = JobName + runFileEnd
                prj = Bladed.ProjectApi.GetProject(os.path.join(PathToBladedRuns, JobName))
                newJobName = JobName.split('.')[0]
                Bladed.ProjectApi.QueueJob(prj, PathToBladedRuns, newJobName)

                sys.stdout.write('\r' + str(idx + 1) + ' of ' + str(len(ListOfBladedJobs)) + ' Job(s) added to queue ')  #: ' + PrintList)
            print(': ' + ", ".join([JobName for JobName in ListOfBladedJobs]))

            # Starting batch and define working directory done in UsageExampleUtilities
            # Set job list name
            Bladed.BatchApi.SetJobList(r"AutoIterations")

            # Add queued jobs to batch. This will not return until the operation is complete and it clears the job queue
            Bladed.ProjectApi.AddQueuedJobsToBatch()
            # print("Queued jobs have been added to batch.")

            # Run the simulations added to batch
            print("Starting to run calculations.")
            # Blocking method to run the batched calculations and only return when it has finished running.
            Bladed.BatchApi.RunBlocking()
            if Bladed.BatchApi.HasCompleted():
                print("Batch runs have completed successfully.")
            else:
                print("Batch runs have not completed successfully.")

            # Shut down the Batch framework
            # Throws an exception if the batch framework could not be stopped due to being busy.
            # Bladed.BatchApi.StopFramework()

        except Exception:
            print("ERROR WHILE LOADING AND RUNNING BLADED BATCH!!!!")
        # finally: # Reset the API. Clear all state.
        #     Bladed.Reset()

    ####################################################################################################################
    ####################################################################################################################
    ################################################## Bladed EVALUATIONS ##############################################
    ####################################################################################################################
    ####################################################################################################################

    def extractDEL_towerHubBlade(self, RunFolder, ListOfBladedJobs):
        DEL_dicts = [dict(zip(DEL_keys, range(len(DEL_keys)))) for whatever in range(len(ListOfBladedJobs))]

        Utility().calcTotalTimeAndDeltat(RunFolder, ListOfBladedJobs[0])



        MainResults = []
        cnt_warnings = 0

        if PrintDetails:
            print('# ------------------ Extracting Tower My\' DEL from Bladed ASCII results ------------- #')
        # Bladed Output Properties
        nmbr_load_member = 2
        # nmbr_loads_per_note = 6
        pos_of_note = 3  # every member has two notes; all notes of a single time step are staggered in one column, thus:
                         # pos 1 is first node of first member; 2 is second node of member 1; 3 is first node of member 2 ..
        for idx, filename in enumerate(ListOfBladedJobs): #[11:500]:
            #break
            file = os.path.join(RunFolder, filename).replace(runFileEnd, towerFileEnd)
            if PrintDetails:
                print('current file is called: ', file)  # filename = (file.replace(RunFolder + '\\', '', ))

            TowerMx = []
            TowerMy = []
            TowerMz = []

            try:
                csv_data = csv.reader(open(file), delimiter=' ')
            except OSError:
                print('Something is rotten in the state of denmark!')
                print('cannot find ', file, '. Will skip and set value to 0.')
                DEL_dicts[idx]['Tower_My_sector_max_DEL'] = 0
                continue

            line_count = 0
            load_count = 0
            # nheader = 0
            for row in csv_data:
                # if load_count < int(time_total / deltat) + 1:  # nheader:
                if line_count == load_count * nmbr_load_member * 2 + pos_of_note - 1:
                    row = list(filter(None, row))
                    # time[line_count-nheader] = row[0]
                    TowerMz.append(float(row[0]))
                    TowerMx.append(float(row[1]))
                    TowerMy.append(float(row[2]))
                    # TowerMxy.append(float(row[3]))
                    load_count = load_count + 1
                # else: print('overshooting lines')
                line_count = line_count + 1

            '''
            with open(file) as csv_file:
                csv_data = csv.reader(csv_file, delimiter=' ')
                line_count = 0
                load_count = 0
                # nheader = 0
                for row in csv_data:
                    if load_count < int(time_total/deltat)+1: #nheader:
                        if line_count == load_count * nmbr_load_member * 2:
                            row = list(filter(None, row))
                            # time[line_count-nheader] = row[0]
                            TowerMx.append(float(row[1]))
                            TowerMy.append(float(row[2]))
                            # TowerMxy.append(float(row[3]))
                            load_count = load_count + 1
                    # else: print('overshooting lines')
                    line_count = line_count + 1
                    '''

            # sum moment vectors in fixed directions and search for worst DEL direction
            DEL_max = Utility().calcWorstDELsector(TowerMx, TowerMy, nSectors, MainResults, file)
            DEL_dicts[idx]['Tower_My_sector_max_DEL'] = DEL_max
            # DEL_dicts[idx][DEL_keys[2]] = DEL_max
            DEL_dicts[idx]['Tower_Mx_DEL'] = Utility().calcDELfromTimeSeries(TowerMx, k_steel)
            DEL_dicts[idx]['Tower_My_DEL'] = Utility().calcDELfromTimeSeries(TowerMy, k_steel)
            DEL_dicts[idx]['Tower_Mz_DEL'] = Utility().calcDELfromTimeSeries(TowerMz, k_steel)


        if PrintDetails:
            print('# ------------------ Exctracting Hub Mx DEL from Bladed ASCII results --------------- #')
        for idx, filename in enumerate(ListOfBladedJobs):  # [11:500]:
            file = os.path.join(RunFolder, filename).replace(runFileEnd, hubFileEnd)
            if PrintDetails:
                print('current file is called: ', file)  # filename = (file.replace(RunFolder + '\\', '', ))

            try:
                csv_data = csv.reader(open(file), delimiter=' ')
            except OSError:
                print('cannot find ', file, '. Will skip and set value to 0.')
                DEL_dicts[idx]['Hub_My_sector_max_DEL'] = 0
                continue

            HubMx = []
            HubMy = []
            HubMz = []
            HubFx = []
            for row in csv_data:
                row = list(filter(None, row))
                HubMx.append(float(row[0]))
                HubMy.append(float(row[1]))
                HubMz.append(float(row[2]))
                HubFx.append(float(row[4]))

            # sum moment vectors in fixed directions and search for worst DEL direction
            # Note: Hub_My is the major moment direction for a two-bladed turbine
            DEL_max = Utility().calcWorstDELsector(HubMz, HubMy, nSectors, MainResults, file)
            DEL_dicts[idx]['Hub_Myz_sector_max_DEL'] = DEL_max
            DEL_dicts[idx]['Hub_Mx_DEL'] = Utility().calcDELfromTimeSeries(HubMx, k_steel)
            DEL_dicts[idx]['Hub_My_DEL'] = Utility().calcDELfromTimeSeries(HubMy, k_steel)
            DEL_dicts[idx]['Hub_Mz_DEL'] = Utility().calcDELfromTimeSeries(HubMz, k_steel)
            DEL_dicts[idx]['Hub_Fx_DEL'] = Utility().calcDELfromTimeSeries(HubFx, k_steel)


        if PrintDetails:
            print('# -------- Exctracting Blade My DEL and Pitch LDC (load duty cycle) from Bladed ASCII results ------- #')
        for idx, filename in enumerate(ListOfBladedJobs):  # [11:500]:
            # bladeFileEnd = '.$41'
            pitchFileEnd = '.$08'
            Pitch_movement_file = os.path.join(RunFolder, filename).replace(runFileEnd, pitchFileEnd)

            Sum_Blade_Mx_DELs = 0
            Sum_Blade_My_DELs = 0
            Sum_Blade_Mz_DELs = 0
            Sum_Blade_Fz_DELs = 0
            Sum_Pitch_LDCs = 0
            for idx_blade in range(nBlades):
                bladeFileEnd = '.$4' + str(idx_blade + 1)
                Blade_load_file = os.path.join(RunFolder, filename).replace(runFileEnd, bladeFileEnd)

                try:
                    csv_data = csv.reader(open(Blade_load_file), delimiter=' ')
                except OSError:
                    print('cannot find ', file, '. Will skip and set value to 0.')
                    DEL_dicts[idx]['Pitch_LDC'] = 0
                    continue
                BladeMx = []  # blade root my moment
                BladeMy = []  # blade root my moment
                BladeMz = []  # blade root my moment
                BladeFz = []  # blade root my moment
                for row in csv_data:
                    row = list(filter(None, row))
                    BladeMx.append(float(row[0]))
                    BladeMy.append(float(row[1]))
                    BladeMz.append(float(row[3]))
                    BladeFz.append(float(row[7]))
                # DEL_dicts[idx]['Blade_My_DEL'] = calcDELfromTimeSeries(BladeMy)
                Sum_Blade_Mx_DELs += Utility().calcDELfromTimeSeries(BladeMx, 10)
                Sum_Blade_My_DELs += Utility().calcDELfromTimeSeries(BladeMy, 10)
                Sum_Blade_Mz_DELs += Utility().calcDELfromTimeSeries(BladeMz, 10)
                Sum_Blade_Fz_DELs += Utility().calcDELfromTimeSeries(BladeFz, 10)

                try:
                    csv_data = csv.reader(open(Pitch_movement_file), delimiter=' ')
                except OSError:
                    print('cannot find ', file, '. Will skip and set value to 0.')
                    DEL_dicts[idx]['Pitch_LDC'] = 0
                    continue
                PitchVelo = []  # pitch velocity
                for row in csv_data:
                    row = list(filter(None, row))
                    PitchVelo.append(float(row[nBlades]))

                Pitch_LDC = 0  # pitch load duty cycle
                for i in range(len(BladeMy) - 1):
                    # Pitch_LDC = Pitch_LDC + 1/2* abs(BladeMy[i]*PitchVelo[i] + BladeMy[i+1]*PitchVelo[i+1]) # valid for trapez-rule
                    Pitch_LDC = Pitch_LDC + abs(BladeMy[i] * PitchVelo[i])  # no real difference

                # DEL_dicts[idx]['Pitch_LDC'] = Pitch_LDC
                Sum_Pitch_LDCs += Pitch_LDC

            DEL_dicts[idx]['Blade_Mx_DEL'] = Sum_Blade_Mx_DELs / nBlades
            DEL_dicts[idx]['Blade_My_DEL'] = Sum_Blade_My_DELs / nBlades
            DEL_dicts[idx]['Blade_Mz_DEL'] = Sum_Blade_Mz_DELs / nBlades
            DEL_dicts[idx]['Blade_Fz_DEL'] = Sum_Blade_Fz_DELs / nBlades
            DEL_dicts[idx]['Pitch_LDC'] = Sum_Pitch_LDCs / nBlades

        return DEL_dicts


    def extractStatisticalBladedResultsData(self, RunFolder, ListOfBladedJobs):
        # fileEnd = '.$PJ'

        '''
        # in dict: {'VARIAB': , 'FileEnd': , 'Desired': } # not needed for now: DIMENS[1], GENLAB
        Searching =[{'VARIAB': 'Tower My', 'FileEnd': '.%25', 'Desired': 'MAX'},  # 'DIMENS[1]': 0, 'GENLAB': 'Tower member loads - local coordinates', 'FileEnd': '.%25'},
                    {'VARIAB': 'Generator torque', 'FileEnd': '.%06', 'Desired': 'MAX'},  #  , 'DIMENS[1]': 0, 'GENLAB': 'Generator variables', 'FileEnd': '.%06'},
                    {'VARIAB': 'Electrical power', 'FileEnd': '.%06', 'Desired': 'MEAN'},  # , 'DIMENS[1]': 0, 'GENLAB': 'Generator variables', 'FileEnd': '.%06'}]
                    {'VARIAB': 'Generator torque', 'FileEnd': '.%06', 'Desired': 'MAX'},  # 'DIMENS[1]': 0, 'GENLAB': 'Generator variables'
                    {'VARIAB': 'Blade 1 My (Root axes)', 'FileEnd': '.%41', 'Desired': 'MAX'}, # '%42' Blade2, '%43' Blade3 # 'GENLAB': 'Blade 1 Loads: Root axes'
                    {'VARIAB': 'Blade 1 Mx (Root axes)', 'FileEnd': '.%41', 'Desired': 'MAX'}, # '%42' Blade2, '%43' Blade3 # 'GENLAB': 'Blade 1 Loads: Root axes'
                    {'VARIAB': 'pitch_actuator_duty_cycle', 'FileEnd': '.%29', 'Desired': 'MAXMIN_Delta'},  # 'DIMENS[1]': 0, 'GENLAB': 'External Controller'
                    {'VARIAB': 'Rotor speed', 'FileEnd': '.%05', 'Desired': 'MAX'}, # 'DIMENS[1]': 0, 'GENLAB': 'Drive train variables'
                    {'VARIAB': 'Yaw bearing Mxy', 'FileEnd': '.%24', 'Desired': 'MAX'},  # 'DIMENS[1]': 0, 'GENLAB': 'Yaw bearing loads GL coordinates'
                    {'VARIAB': 'Rotating hub Mx', 'FileEnd': '.%22', 'Desired': 'MAX'},  # 'DIMENS[1]': 0, 'GENLAB': 'Hub loads: rotating GL coordinates'
                    {'VARIAB': 'Blade 1 x-deflection (perpendicular to rotor plane)', 'FileEnd': '.%18', 'Desired': 'MAXMIN_Delta'},  # 'DIMENS[1]': 0, 'GENLAB': 'Blade 1 Deflections'
                    {'VARIAB': 'Blade 1 pitch angle', 'FileEnd': '.%08', 'Desired': 'MAXMIN_Delta'}]  # 'DIMENS[1]': 0, 'GENLAB': 'Pitch system'

        '''
        Searching = [{'VARIAB': 'Electrical power', 'FileEnd': '.%06', 'Desired': 'MEAN'},
                     # 'DIMENS[1]': 0, 'GENLAB': 'Generator variables'
                     {'VARIAB': 'Blade 1 My (Root axes)', 'FileEnd': '.%41', 'Desired': 'MAX'},
                     # 'GENLAB': 'Blade 1 Loads: Root axes'
                     # {'VARIAB': 'pitch_actuator_duty_cycle', 'FileEnd': '.%29', 'Desired': 'MAXMIN_Delta'},  # 'DIMENS[1]': 0, 'GENLAB': 'External Controller'
                     {'VARIAB': 'Rotor speed', 'FileEnd': '.%05', 'Desired': 'MAX'},
                     # 'DIMENS[1]': 0, 'GENLAB': 'Drive train variables'
                     {'VARIAB': 'Stationary hub Fx', 'FileEnd': '.%23', 'Desired': 'MEAN'},
                     {'VARIAB': 'Support Structure global orientation about y', 'FileEnd': '.%65', 'Desired': 'MEAN'},
                     {'VARIAB': 'Support Structure global orientation about y', 'FileEnd': '.%65', 'Desired': 'MAX'},
                     {'VARIAB': 'Mooring line tension', 'FileEnd': '.%77', 'Desired': 'MAX'},
                     {'VARIAB': 'Nacelle fore-aft acceleration', 'FileEnd': '.%26', 'Desired': 'MAX'}]

        Statistics_keys = ['Power_mean', 'Blade_My_max', 'RotationSpeed_max', 'mean_Thrust_Hub_Fx', 'mean_Platform_Pitch',
                           'max_Platform_Pitch', 'max_mooring_tension', 'max_Nacelle_FA_accel']
        Statistics = [dict(zip(Statistics_keys, [0 for _ in range(len(Statistics_keys))]))
                      for _ in range(len(ListOfBladedJobs))]

        # RefFile = fileList[0].replace(PathMainRunFolder + '\\', '').replace('.$PJ','')

        # Filter additional parameters from a reference run
        for Search in Searching:
            DidWork = False
            for JobName in ListOfBladedJobs:
                filename = os.path.join(RunFolder, JobName.replace(runFileEnd, '')) + Search.get('FileEnd')
                try:
                    file_data = csv.reader(open(filename), delimiter='\t')
                except OSError:
                    print('could not open file ' + filename + ' for bladed file variable position will try next one')
                else:
                    DidWork = True
                    break
            if DidWork:
                for row in file_data:
                    if row[0].find('DIMENS') != -1:
                        DIMENS = row[1:]

                    if row[0].find('VARIAB') != -1:
                        if PrintDetails:
                            print('found VARIAB: ', row)
                        ASCII_content = row[1][1:-1].split('\' \'')
                        pstn = 0
                        for Content in ASCII_content:
                            if Content == Search.get('VARIAB'):
                                Search['PSTN'] = int(pstn)
                                Search['PSTNs'] = int(DIMENS[0])
                                # Search['FileEnd'] = PrcntFileType
                            pstn = pstn + 1
            else:
                print('None of the runs did work.... Hopefully next generation is better.')
                return Statistics

        # Search through all relevant files for all desired components
        Statistics_old = []  # Values in 'Searching' List will be overwritten in every sub loop
        keys_old = [Search.get('VARIAB') + '_' + Search.get('Desired') for Search in Searching]
        if PrintDetails:
            print('Statistics keys are: ', keys_old)
        HelpList = [0 for key in keys_old]
        for file_idx, file in enumerate(ListOfBladedJobs):
            for search_idx, Search in enumerate(Searching):
                filename = os.path.join(RunFolder, file.replace(runFileEnd, Search.get('FileEnd')))

                try:
                    file_data = csv.reader(open(filename), delimiter=' ')
                except OSError:
                    print('Something is rotten in the state of denmark!')
                    print('cannot find ', filename, '. Will skip and leave value as 0.')
                    break

                ScrollingULOADS = 0
                FoundMean = 0
                for row in file_data:
                    row[:] = [x for x in row if x]  # remove empty list elements

                    if row[0] == 'ULOADS' or ScrollingULOADS > 0:
                        if ScrollingULOADS < 2 * Search.get('PSTNs'):
                            # print('ScollingULAODS ', ScollingULOADS, ' is smaller than ', 2*Searching[Search_idx].get('PSTNs'))
                            if ScrollingULOADS == Search.get('PSTN') * 2:
                                Search['MAX'] = float(
                                    row[Search.get('PSTN') + (ScrollingULOADS == 0)])  # +1 if first row to scip string
                                # print('MAX in ', row[Search.get('PSTN') + (ScrollingULOADS == 0)])
                            if ScrollingULOADS == Search.get('PSTN') * 2 + 1:
                                Search['MIN'] = float(row[Search.get('PSTN')])
                                # print('MIN in ', row[Search.get('PSTN')])

                        ScrollingULOADS = ScrollingULOADS + 1

                    if row[0] == 'MEAN' and not FoundMean:  # isinstance(Search.get('MEAN'), float) == 0:
                        Search['MEAN'] = float(row[Search.get('PSTN') + 1])
                        # print('MEAN is', row[Search.get('PSTN')+1])
                        FoundMean = 1

                if not Search.get('MIN'):
                    Search['MAXMIN_Delta'] = 0
                else:
                    Search['MAXMIN_Delta'] = Search.get('MAX') - Search.get('MIN')
                # print('MAXMIN_delta is: ', Search.get('MAXMIN_Delta'))

                HelpList[search_idx] = Search.get(Search.get('Desired'))
                Statistics[file_idx][Statistics_keys[search_idx]] = Search.get(Search.get('Desired'))

            Statistics_old.append(dict(zip(keys_old, HelpList)))

        return Statistics

        # writeListDictToCSV(Statistics, os.path.join(PostProResultsFolder, MainFolder + '_Statistics_all.csv'))















# ----------------------------------------------------------------------------------------------------------------
# Functions mostly used for genetic algorithm optimization
# ----------------------------------------------------------------------------------------------------------------
class GA_utility:
    def calcProbabilities(self, FitnessFunctions):
        # Function should calculate probabilities vom the respective FitnessFunction values.
        # The sum of all probabilities should be 1.
        Probabilities = []
        for value in FitnessFunctions:
            Probabilities.append(value / sum(FitnessFunctions))
        return Probabilities

    def calcProbabilitiesByRank(self, FitnessFunctions):
        # Function should calculate probabilities vom the respective FitnessFunction values.
        # Fitnesses will be ranked and probability distributed for the ranking.
        # The sum of all probabilities should be 1.
        Probabilities = [0 for _ in FitnessFunctions]
        P1 = 0.3
        for cnt, idx in enumerate(np.argsort(FitnessFunctions)):
            Probabilities[idx] = np.power(1 - P1, cnt) * P1
            if cnt == (len(FitnessFunctions-1)):
                Probabilities[idx] = Probabilities[idx] / P1
        return Probabilities

    def calcProbabilityIntervals(self, Probabilities):
        # Function should order the probabilities in an order between 0 and 1.
        ProbabilityIntervalls = []
        Memory = 0
        for Probability in Probabilities:
            ProbabilityIntervalls.append([Memory, Memory + Probability])
            Memory += Probability
        return ProbabilityIntervalls

    def reproduction(self, GA_Strings, ProbabilityIntervals):
        # It mimics the random roulette principal including the respective probabilities.
        # It transfers the mating pool to the reproduction pool
        New_GA_Strings = []
        idx_List = []
        for _ in range(len(GA_Strings)):
            RandomNumber = random.uniform(0, 1)
            for idx, ProbabilityInterval in enumerate(ProbabilityIntervals):
                if ProbabilityInterval[0] <= RandomNumber and RandomNumber <= ProbabilityInterval[1]:
                    New_GA_Strings.append(GA_Strings[idx])
                    idx_List.append(idx)
        if PrintDetails:
            print(idx_List)
        return New_GA_Strings

    def reproductionWithDiversity(self, GA_Strings, ProbabilityIntervals):
        # It mimics the random roulette principal including the respective probabilities.
        # It transfers the mating pool to the reproduction pool
        New_GA_Strings = []
        idx_List = []
        for _ in range(len(GA_Strings)):
            RandomNumber = random.uniform(0, 1)
            for idx, ProbabilityInterval in enumerate(ProbabilityIntervals):
                if ProbabilityInterval[0] <= RandomNumber and RandomNumber <= ProbabilityInterval[1]:
                    New_GA_Strings.append(GA_Strings[idx])
                    idx_List.append(idx)
        if PrintDetails:
            print(idx_List)
        return New_GA_Strings

    def crossover(self, GA_Strings, p_cross, check_p_cross):
        # crossing "genes" if crossing probability (p_cross, default = 0.8) allows for it in random loops
        for idx_string in range(int(len(GA_Strings)/2)):
            if random.uniform(0, 1) <= p_cross:
                RandomPosition = int(random.uniform(1, len(GA_Strings[0]) - 1)) # starting with 1 instead of 0 to force a crossing
                Partner1 = list(GA_Strings[idx_string * 2])
                Partner2 = list(GA_Strings[idx_string * 2 + 1])
                for idx in range(RandomPosition):
                    Memory = copy(Partner1[idx])
                    Partner1[idx] = copy(Partner2[idx])
                    Partner2[idx] = copy(Memory)
                GA_Strings[idx_string * 2] = ''.join(Partner1)
                GA_Strings[idx_string * 2 + 1] = ''.join(Partner2)
                check_p_cross[1] += 1
            check_p_cross[0] += 1
        return GA_Strings, check_p_cross

    def mutation(self, GA_Strings, p_mutate, check_p_mutate):
        # mutate (1=0 or 0=1) every bit in the GA_Strings with the probability of p_mutate (default = 0.05)
        New_GA_Strings = []
        for GA_String in GA_Strings:
            GA_String_List = list(GA_String)
            for idx in range(len(GA_String_List)):
                if random.uniform(0, 1) <= p_mutate:
                    if GA_String_List[idx] == '0':
                        GA_String_List[idx] = '1'
                    elif GA_String_List[idx] == '1':
                        GA_String_List[idx] = '0'
                    else:
                        print('Something is rotten in the state of denmark')
                    check_p_mutate[1] += 1
                check_p_mutate[0] += 1
            New_GA_Strings.append(''.join(GA_String_List))
        return New_GA_Strings, check_p_mutate

    def bitStringToDezimal(self, GA_Strings, SolutionIntervals):
        # turns string of bits into parameters inside the defined intervals
        nParams = len(SolutionIntervals)
        Params = [[0 for i in range(nParams)] for ii in range(len(GA_Strings))]
        for idx, GA_String in enumerate(GA_Strings):
            nBits = int(len(GA_String) / nParams)
            for idx_Params in range(nParams):
                BitParam = int(GA_String[idx_Params * nBits: (idx_Params + 1) * nBits], 2)  # 2 for binary
                if PrintDetails:
                    print('BitParam: ', BitParam, 'Bit-String:', GA_String[idx_Params * nBits: (idx_Params + 1) * nBits], GA_String)
                Params[idx][idx_Params] = SolutionIntervals[idx_Params][0] + (SolutionIntervals[idx_Params][1]
                             - SolutionIntervals[idx_Params][0]) / (pow(2, nBits) - 1) * BitParam
        return Params

    def findeUnchangedRuns(self, GA_Strings, New_GA_Strings):  # , ListOfBladedJobs):
        # If job parameters haven't been altered than it is unnecessarily time consuming to run those jobs again
        OldIdxOfUnchangedBladedJobs = []
        NewIdxOfUnchangedBladedJobs = []
        for old_idx, GA_String in enumerate(GA_Strings):
            for new_idx, New_GA_String in enumerate(New_GA_Strings):
                if GA_String == New_GA_String:
                    if new_idx not in NewIdxOfUnchangedBladedJobs:
                        OldIdxOfUnchangedBladedJobs.append(old_idx)
                        NewIdxOfUnchangedBladedJobs.append(new_idx)
                    else:
                        if PrintDetails:
                            print('WARNING! CROSSING DUPLICATE! WILL JUMP HERE! (GA_utility().findeUnchangedRuns())')
        return OldIdxOfUnchangedBladedJobs, NewIdxOfUnchangedBladedJobs




