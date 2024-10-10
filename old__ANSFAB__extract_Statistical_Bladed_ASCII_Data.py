import os  # This provides operating system (os) tools, such as copy file
import glob
import csv

PrintDetails = True
fileEnd = '.$PJ'
#from ANSFAB__Utility_fncts import MainFolder, PathMainRunFolder, PostProResultsFolder, nSeeds, writeListDictToCSV, sumSeedsOfIterations, sumAndNormSeedsOfIterations

# MainRunFolder = r'2020_08_31__3B_DD_15mps_powerErr__gen_mass_really_in_front'
# PostProResultsFolder = os.path.join(os.getcwd(), MainRunFolder, 'PostPro')
# PathMainRunFolder = os.path.join(os.getcwd(), MainRunFolder)

# print('file(s) in dir: ' + str(os.listdir(PathMainRunFolder)))
def extractStatisticalBladedResultsData(RunFolder, ListOfBladedJobs):

    #fileEnd = '.$PJ'

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
    Searching = [{'VARIAB': 'Electrical power', 'FileEnd': '.%06', 'Desired': 'MEAN'},  # 'DIMENS[1]': 0, 'GENLAB': 'Generator variables'
        {'VARIAB': 'Blade 1 My (Root axes)', 'FileEnd': '.%41', 'Desired': 'MAX'}, # 'GENLAB': 'Blade 1 Loads: Root axes'
        #{'VARIAB': 'pitch_actuator_duty_cycle', 'FileEnd': '.%29', 'Desired': 'MAXMIN_Delta'},  # 'DIMENS[1]': 0, 'GENLAB': 'External Controller'
        {'VARIAB': 'Rotor speed', 'FileEnd': '.%05', 'Desired': 'MAX'}, # 'DIMENS[1]': 0, 'GENLAB': 'Drive train variables'
        {'VARIAB': 'Stationary hub Fx', 'FileEnd': '.%23', 'Desired': 'MEAN'},
        {'VARIAB': 'Support Structure global orientation about y', 'FileEnd': '.%65', 'Desired': 'MEAN'},
        {'VARIAB': 'Support Structure global orientation about y', 'FileEnd': '.%65', 'Desired': 'MAX'},
        {'VARIAB': 'Mooring line tension', 'FileEnd': '.%77', 'Desired': 'MAX'},
        {'VARIAB': 'Nacelle fore-aft acceleration', 'FileEnd': '.%26', 'Desired': 'MAX'}]

    Statistics_keys = ['Power_mean', 'Blade_My_max', 'RotationSpeed_max', 'mean_Thrust_Hub_Fx', 'mean_Platform_Pitch',
                       'max_Platform_Pitch', 'max_mooring_tension', 'max_Nacelle_FA_accel']
    Statistics = [dict(zip(Statistics_keys, [0 for _ in range(len(Statistics_keys))]))
                  for _ in range(len(ListOfBladedJobs))]

    #RefFile = fileList[0].replace(PathMainRunFolder + '\\', '').replace('.$PJ','')


    # Filter additional parameters from a reference run
    for Search in Searching:
        DidWork = False
        for JobName in ListOfBladedJobs:
            filename = os.path.join(RunFolder, JobName.replace(fileEnd, '')) + Search.get('FileEnd')
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
                            #Search['FileEnd'] = PrcntFileType
                        pstn = pstn + 1
        else:
            print('None of the runs did work.... Hopefully next generation is better.')
            return Statistics

    # Search through all relevant files for all desired components
    Statistics_old = []  # Values in 'Searching' List will be overwritten in every sub loop
    keys_old = [Search.get('VARIAB')+'_'+Search.get('Desired') for Search in Searching]
    if PrintDetails:
        print('Statistics keys are: ', keys_old)
    HelpList = [0 for key in keys_old]
    for file_idx, file in enumerate(ListOfBladedJobs):
        for search_idx, Search in enumerate(Searching):
            filename = os.path.join(RunFolder, file.replace(fileEnd, Search.get('FileEnd')))

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
                    if ScrollingULOADS < 2*Search.get('PSTNs'):
                        # print('ScollingULAODS ', ScollingULOADS, ' is smaller than ', 2*Searching[Search_idx].get('PSTNs'))
                        if ScrollingULOADS == Search.get('PSTN')*2:
                            Search['MAX'] = float(row[Search.get('PSTN') + (ScrollingULOADS == 0)]) # +1 if first row to scip string
                            # print('MAX in ', row[Search.get('PSTN') + (ScrollingULOADS == 0)])
                        if ScrollingULOADS == Search.get('PSTN')*2+1:
                            Search['MIN'] = float(row[Search.get('PSTN')])
                            # print('MIN in ', row[Search.get('PSTN')])

                    ScrollingULOADS = ScrollingULOADS + 1

                if row[0] == 'MEAN' and not FoundMean: # isinstance(Search.get('MEAN'), float) == 0:
                    Search['MEAN'] = float(row[Search.get('PSTN')+1])
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

    '''
    Statistics_summed, Statistics_Alarms = sumAndNormSeedsOfIterations(Statistics, nSeeds, 'Rotor speed')
    Statistics_summed_absolute = sumSeedsOfIterations(Statistics, nSeeds)

    writeListDictToCSV(Statistics,        os.path.join(PostProResultsFolder, MainFolder + '_Statistics_all.csv'))
    writeListDictToCSV(Statistics_summed_absolute, os.path.join(PostProResultsFolder, MainFolder + '_Statistics_summed_absolute_values.csv'))
    if bool(Statistics_summed[0]):
        writeListDictToCSV(Statistics_summed, os.path.join(PostProResultsFolder, MainFolder + '_Statistics_summed_relative.csv'))
        writeListDictToCSV(Statistics_Alarms, os.path.join(PostProResultsFolder, MainFolder + '_Statistics_alarms.csv'))
    '''
    # print('Note, that only the first MAX, MIN and MEAN in the $-Files will be extracted')




























    '''
    output_file_name = os.path.join(PostProResultsFolder, MainRunFolder + '_Main_Statistics.csv')
    print('outfile is in dir: ' + output_file_name)
    with open(output_file_name, mode='w', newline='') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(Statistics)
    
    
    
    runs_info_file = glob.glob(os.path.join(MainRunFolder, 'base_prj_files') + '\*.csv')[0]
    print('Opening runs info file ', runs_info_file)
    file_data = csv.reader(open(runs_info_file), delimiter=',')
    
    runs_info = []
    info_keys = []
    cnt = 0
    for row in file_data:
        if not info_keys:
            info_keys = row
            print('info_keys are ', info_keys)
        else:
            runs_info.append(dict(zip(info_keys, row)))
            if float(runs_info[cnt].get(info_keys[1])) == 1 and float(runs_info[cnt].get(info_keys[2])) == 1:
                PosOfReference = cnt
                print('entirely unsure about the position of gain factors 1 and 1! Here position ', PosOfReference)
            cnt += 1
    
    
    print(Statistics[0].keys())
    nSeeds = int(6)
    iterationCases = int(len(Statistics)/nSeeds)
    Statistics_summed = [dict(zip(Statistics[0].keys(), range(len(Statistics[0].keys())))) for cnt in range(iterationCases)]
    for cnt in range(iterationCases):
        for key in Statistics[0].keys():
            Sum = 0
            for nSeed in range(nSeeds):
                Value = float(Statistics[cnt + iterationCases * nSeed].get(key))
                Value_ref = float(Statistics[PosOfReference + iterationCases * nSeed].get(key))
                Sum += Value / Value_ref
            Statistics_summed[cnt][key] = Sum / nSeeds
    '''



