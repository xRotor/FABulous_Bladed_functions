print('hello world')

import csv
import math
import time as timing
import rainflow
import matplotlib.pyplot as plt
import glob
import copy
import os
import shutil
from ANSFAB__Utility_fncts import PathMainRunFolder, PostProResultsFolder, TempSubFolder, SaveFolder, time_total,\
    deltat, nSectors, lever_length_in_m, rotor_weight_in_kg, gravitation, calculate_drivetrain_bending

# lever_length_in_m = 4.644    # in meter
# rotor_weight_in_kg = 589544  # in kg
# gravitation = 9.81           # in m/s^2
# calculate_drivetrain_bending = True

# search for filenames
# MainRunFolder = '2020_09_03__3B_DD_23mps_powerErr\\'
# TempSubFolder = MainRunFolder + 'temp\\'
# SaveFolder = MainRunFolder + 'save_org_data\\'
# PostProResultsFolder = MainRunFolder + 'PostPro\\'

# time_total = 600  #time series length in s
# deltat = 0.02       # time step length in s
# nSectors = 12 # 24
eps = 0.001  # accuracy of factor to not divide by zero

print('Sector width = ' + str(180/nSectors) + 'deg')
# Bladed Output Properties
# nmbr_load_member = 2
# nmbr_loads_per_note = 6
pos_of_note = 1 # every member has two notes; all notes of a single time step are staggered in one column

print(int(time_total/deltat))

Referenz_Frequency = 1 # Hz
Nreff= time_total * Referenz_Frequency # 600 #
k = 4
var_nbins = 100
print('MOST IMPORTANT DEL PARAMETER: Woehler Exp: ', k, ', ref frequency: ', Referenz_Frequency,
          ', ref cycles: ', Nreff, ' and numbers of bins is: ', var_nbins)

'''
try:
    os.mkdir(TempSubFolder)
except OSError:
    print("Creation of the directory %s failed. Might already exist" % TempSubFolder)
else:
    print("Successfully created the directory %s " % TempSubFolder)
try:
    os.mkdir(SaveFolder)
except OSError:
    pass
try:
    os.mkdir(PostProResultsFolder)
except OSError:
    pass
'''

# open bladed PJ file
fileList = glob.glob(PathMainRunFolder + '\\*.$22')
infileList = []
counting = 0
for file in fileList:
    infileList.append(file.replace(PathMainRunFolder,'',).replace('.$22',''))
    print(str(counting)+ ' is ' + file)
    counting = counting + 1
print('found files', infileList)
print('file list:', fileList)


MainResults = []
keys = ['runName','DEL_Mx','DEL_My', 'ref_DEL_Mxy','new_max_DEL_Mxy','sector','rel_difference']
counting = 0
loopTime = 0
cnt_warnings = 0
startTime = timing.time()
lastTime = timing.time()

for file in fileList: # [-1:]:
    #break
    print(file)
    filename = (file.replace(PathMainRunFolder + '\\', '', ))


    # selecting rotor azimuth to calculate drive train bending moment
    DriveTrainGravityBendingMy = [] # the gravity based rotor weight bending moment of the rotating drive train at the
    DriveTrainGravityBendingMz = [] # first main bearing in Nm (=> My = G_rotor * lever * cos(rotor_azimuth))
                                    # GL-Rotating Hub coordinate system at azimuth  0°: z-pointing up, y to the side
                                    # GL-Rotating Hub coordinate system at azimuth 90°: y-pointing up, z to the side
    azimuthfile = file.replace('.$22','.$05')
    with open(azimuthfile) as csv_file:
        csv_data = csv.reader(csv_file, delimiter=' ')
        for row in csv_data:
            row = list(filter(None, row))
            azimuth = float(row[1])
            DriveTrainGravityBendingMy.append(- math.cos(azimuth) * lever_length_in_m * rotor_weight_in_kg * gravitation)
            DriveTrainGravityBendingMz.append(+ math.sin(azimuth) * lever_length_in_m * rotor_weight_in_kg * gravitation)


    HubMy = []
    HubMz = []
    HubMy_original = []
    HubMz_original = []
    HubMyz = [] # old: HubMy_Sector = np.empty([nSectors, int(time_total / deltat + 10)])
    HubMy_Sector = [[] for n in range(nSectors)] #np.empty([nSectors, int(time_total / deltat + 10)])

    with open(file) as csv_file:
        csv_data = csv.reader(csv_file, delimiter=' ')

        for timeStep, row in enumerate(csv_data):
            row = list(filter(None, row))
            HelpMy = float(row[1])
            HelpMz = float(row[2])
            HubMy_original.append(copy.copy(HelpMy))
            HubMz_original.append(copy.copy(HelpMz))
            if calculate_drivetrain_bending:
                HelpMy += DriveTrainGravityBendingMy[timeStep]
                HelpMz += DriveTrainGravityBendingMz[timeStep]
            HubMy.append(HelpMy)
            HubMz.append(HelpMz)
            HubMyz.append(math.sqrt( pow(HelpMy, 2) + pow(HelpMz, 2)))
            # Check if everything is alright:
            #if abs( 1- float(row[3])/ math.sqrt( pow(float(row[1]), 2) + pow(float(row[2]), 2))) > 0.0001:
                #print("calculation/sorting of HubMyz might be a foolish: should be ",  float(row[3]), " is ", math.sqrt( pow(float(row[1]), 2) + pow(float(row[2]), 2)) )
                #print("row 1: ",  float(row[0]),", row 2: ",  float(row[1]), ", row 3: ",  float(row[2]), ", row 4: ",  float(row[3]), ", row 5: ",  float(row[4]) )

    time = range(int(time_total/deltat))

    RFC = copy.copy(rainflow.count_cycles(HubMyz, nbins = var_nbins))
    RFXz = copy.copy(rainflow.count_cycles(HubMz, nbins=var_nbins))
    RFCy = copy.copy(rainflow.count_cycles(HubMy, nbins=var_nbins))
    RFXz_original = copy.copy(rainflow.count_cycles(HubMz_original, nbins=var_nbins))
    RFCy_original = copy.copy(rainflow.count_cycles(HubMy_original, nbins=var_nbins))

    # DELs = [0 for n in range(var_nbins)] # old: DELs = np.empty(var_nbins)
    DEL = 0
    DELz = 0
    DELy = 0
    DELz_original = 0
    DELy_original = 0
    for bin in range(var_nbins):
        # DELs[bin] = RFC[bin][1]*(pow(RFC[bin][0], k))
        # DEL = DEL + DELs[bin]
        DEL  += RFC[bin][1]  * (pow(RFC[bin][0],  k))
        DELz += RFXz[bin][1] * (pow(RFXz[bin][0], k))
        DELz_original += RFXz_original[bin][1] * (pow(RFXz_original[bin][0], k))
        if not RFCy:
            DELy = 0
        else:
            DELy += RFCy[bin][1] * (pow(RFCy[bin][0], k))
            DELy_original += RFCy_original[bin][1] * (pow(RFCy_original[bin][0], k))

    DEL_ref = pow(DEL/Nreff, 1/k)
    DELz = pow(DELz / Nreff, 1 / k)
    DELy = pow(DELy / Nreff, 1 / k)
    DELz_original = pow(DELz_original / Nreff, 1 / k)
    DELy_original = pow(DELy_original / Nreff, 1 / k)
    #print('Reference DEL:', DEL_ref)


    # sum moment vectors in fixed directions
    DEL_Sector = [0 for n in range(nSectors)] # np.empty(nSectors)
    DEL_max = 0
    n_max = 0
    for n in range(nSectors):
        for timeStep in range(len(HubMz)):
            if abs(float(HubMy[timeStep])) > 0:
                alpha = copy.copy(math.atan(float(HubMz[timeStep]) / float(HubMy[timeStep])))
            else:
                alpha = copy.copy(math.atan(float(HubMz[timeStep]) / eps))
                print('if this is never triggered, this expression is useless...')
            HubMy_Sector[n].append(math.sqrt(pow(HubMz[timeStep], 2) + pow(HubMy[timeStep], 2))\
                                        * math.cos(math.pi / nSectors * n - alpha) * math.copysign(1, HubMy[timeStep]))# * math.copysign(1, HubMy[timeStep]))
            #HubMy_Sector[n].append(copy.copy(math.sqrt(pow(HubMz[timeStep], 2) + pow(HubMy[timeStep], 2)) \
            #            * math.cos( math.pi / nSectors * n - alpha)))  # * math.cos(2 * math.pi / nSectors * n - alpha))
            #HubMz_Sector[n].append(float(math.sqrt(pow(float(HubMz[timeStep]), 2)+pow(float(HubMy[timeStep]), 2))
            #                                   * math.sin(2 * math.pi / nSectors * n - alpha)))

        RFC2 = rainflow.count_cycles(HubMy_Sector[n][:], nbins=var_nbins)
        DELs = [0 for n in range(var_nbins)] # np.empty(var_nbins)
        DEL2 = 0
        for bin in range(var_nbins):
            DELs[bin] = copy.copy(RFC2[bin][1] * (pow(RFC2[bin][0], k)))
            DEL2 = copy.copy(DEL2 + DELs[bin])
        DEL_Sector[n] = copy.copy(pow(DEL2 / Nreff, 1 / k))

        if DEL_Sector[n] > DEL_max:
            DEL_max = copy.copy(DEL_Sector[n])
            n_max = n

    print( '      Reference DEL:', DEL_ref, '; -> maximum DEL', DEL_Sector[n_max], ' found in Sector', n_max, 'with a delta of',
          round((DEL_Sector[n_max]-DEL_ref)/DEL_ref * 100, 2), '% to the baseline. DEL_Mz is ', DELz, ' and DEL_My ', DELy)
    if calculate_drivetrain_bending:
        print('      -> Original Hub My DEL is:', DELy_original, 'and Mz DEL is: ', DELz_original, ' without rotor gravity taken into account')

    MainResults.append(dict(zip(keys, [file, str(DELz), str(DELy), str(DEL_ref), str(DEL_Sector[n_max]), str(n_max), str(round((DEL_Sector[n_max]-DEL_ref)/DEL_ref * 100, 2))])))
    # keys = ['runName','DEL_Mx','DEL_My' 'ref_DEL_Mxy','new_max_DEL_Mxy','sector','rel_difference']
    eps = 100
    if DEL_Sector[n_max]-DELy < -eps or DEL_Sector[n_max]-DELz < -eps:
        print('WARNING: Worst DEL ', DEL_Sector[n_max], ' must not be smaller than My_DEL ', DELy, ' or Mx_DEL ', DELz, '!!!')
        cnt_warnings += 1


    with open(os.path.join(TempSubFolder, filename), 'w', newline='') as csvfile:
        fixed_output_file = csv.writer(csvfile, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)

        #line_count = 0
        load_count = 0

        with open(file) as csv_file:
            csv_data = csv.reader(csv_file, delimiter=' ')

            for row in csv_data:
                #if load_count < int(time_total/deltat)+1: #nheader:
                    #if line_count == load_count * nmbr_load_member * 2:
                row = list(filter(None, row))
                row[3] = "{:.7e}".format(HubMy_Sector[n_max][load_count])
                load_count = load_count + 1
                        #print('load_count:',load_count,'Line number:',line_count)
                # else:
                #     print('overshooting lines')
                #line_count = line_count + 1
                fixed_output_file.writerow(row)


    loopTime = timing.time() - lastTime
    lastTime = timing.time()
    print('-> finished with run ' + str(counting) + ' from ' + str(len(fileList)) + ' in ' + str(int(loopTime)) + 's; ~' \
        + str(int(loopTime*(len(fileList)-counting)))+'s or ~'+str(int(loopTime*(len(fileList)-counting)/60)) + 'min left')
    counting = counting + 1
    #break

    shutil.move(file, file.replace(PathMainRunFolder,SaveFolder))
    shutil.move(file.replace(PathMainRunFolder, TempSubFolder), file)

log_file = os.path.join(PostProResultsFolder,'007_Main_Results_Hub_DEL_sector.csv')
with open(log_file, 'w', newline='') as output_file:
    dict_writer = csv.DictWriter(output_file, keys)
    dict_writer.writeheader()
    dict_writer.writerows(MainResults)


print('total time used = ' + str(int(timing.time()-startTime))+'s')
print('Stack seems not to overflow now :)')

if cnt_warnings > 0:
    print('THERE HAD BEEN ', cnt_warnings, ' WARNINGS. PLEASE CHECK ', log_file)



print('\n--------------------------- Creating post process DEL $PJ-file ----------------------------\n')
import ANSFAB_prepare_Bladed_PostPro


try:
    help = 1 # int(1/deltat)
    plotpoints = 10000
    linestyles = ['-', '--', '-.', ':', '-', '--', '-.', ':', '-', '--', '-.', ':', '-', '--', '-.', ':','-', '--', '-.', ':', '-', '--','-', '--', '-.', ':', '-', '--','-', '--', '-.', ':', '-', '--','-', '--', '-.', ':', '-', '--',]
    for n in range(nSectors):
        if n != n_max:
            plt.plot(time[1:plotpoints*help:help], HubMy_Sector[n][1:plotpoints*help:help], linestyle=linestyles[n], color='yellow', label=str(n))

    plt.plot(time[1:plotpoints*help:help], HubMy_Sector[n_max][1:plotpoints*help:help], linestyle=linestyles[n_max], color='red', label='HubMy_Sector_max')
    plt.plot(time[1:plotpoints*help:help], HubMz[1:plotpoints*help:help], color='grey', linestyle='--', label='HubMz')
    plt.plot(time[1:plotpoints*help:help], HubMyz[1:plotpoints*help:help], color='blue', linestyle='--', label='HubMyz')
    plt.plot(time[1:plotpoints*help:help], HubMy[1:plotpoints*help:help], color='green', linestyle='--', label='HubMy')
    plt.plot(time[1:plotpoints*help:help], HubMy_Sector[0][1:plotpoints*help:help], linestyle=':', color='yellow', label='HubMy_Sector0')

    plt.xlabel('time step')
    if calculate_drivetrain_bending:
        plt.ylabel('drive train rotating bending moment for different directions')
    else:
        plt.ylabel('hub rotating bending moment for different directions')
    plt.title(filename)
    plt.legend()
    plt.show()

    sectors = range(0, int(180), int(180/nSectors))
    plt.plot(sectors, DEL_Sector, color='blue', label='Sector DELs')
    plt.plot([0, int(180)], [DELz, DELz], color='yellow', label='Mz_DEL')
    plt.plot([0, int(180)], [DELy, DELy], color='green', label='My_DEL')
    plt.plot([0, int(180)], [DEL_ref, DEL_ref], color='red', label='Mxy_DEL')
    plt.xlabel('degree, 0 = y_GL_Axis')
    plt.ylabel('hub rotating bending DELs')
    plt.legend()
    plt.title(filename)

    plt.show()
except:
    print('Error while plotting. Could be mismatching time steps on x axis.')


# import ANSFAB_prepare_Bladed_PostPro