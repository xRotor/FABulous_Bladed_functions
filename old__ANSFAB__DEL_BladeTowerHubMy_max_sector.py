import csv
import math
import rainflow
import glob
import copy
import os
from ANSFAB__Utility import Utility
from config import nBlades, nSectors, runFileEnd, towerFileEnd, hubFileEnd, PrintDetails, \
                   eps, Referenz_Frequency, k_steel, var_nbins, DEL_keys, TowerNodePosition

# PrintDetails = True
# runFileEnd = '.$PJ'  # had been 'fileEnd' before
# towerFileEnd = '.$25'
# hubFileEnd = '.$22'


# Parameters to calculate DELs (damage equivalent loads)
# time_total = 1 # 3600.0  #time series length in s
# deltat = 1 # 0.1       # time step length in s
# nSectors = 12  # 24
# eps = 0.001  # accuracy of factor to not divide by zero

# Referenz_Frequency = 1  # Hz
# Nreff = time_total * Referenz_Frequency  # 600 #
# k_steel = 4.0  # Woehler exponent for steel extremely important that this is a float
# var_nbins = 100


# DEL_keys = ['Blade_My_DEL', 'Blade_Mx_DEL', 'Hub_Mx_DEL', 'Tower_My_sector_max_DEL', 'Pitch_LDC']
print('DEL_keys are -> ' + ', '.join(DEL_keys))



########################################################################################################################
########################################################################################################################
################################################## MAIN PART ###########################################################
########################################################################################################################
########################################################################################################################

def extractDEL_towerHubBlade(RunFolder, ListOfBladedJobs):
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
