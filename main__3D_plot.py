from ANSFAB__Utility import Utility


EvaluationKeys = ['Tower_My_sector_max_DEL']
EvaluationKeys = ['Blade_My_DEL']
EvaluationKeys = ['CCC']

filePath = r'C:\xBladed\FOWTs\PythonScripts\CheckPI_gains_2023_04_20___DEL_evaluation.csv'
filePath = r'H:\BladedWS\FOWTs\Optimize_FA_Damper_2B20Volt_v009\bruteForce\2023_04_26___bruteForce__FA_dampers_gain_n_Hz__2B20Volt_v009_1_Documentary.csv'
#filePath = r'C:\xBladed\FOWTs\PythonScripts\iterTowerDamp2_2023_04_20___DEL_evaluation.csv'

X, Y, Z, plt = Utility().readAndPlotThreeDimensionalDataFromCSVfile(filePath)#, EvaluationKeys)

plt.show()




































if False:
    import numpy as np
    import matplotlib.pyplot as plt
    from matplotlib import cm
    import math

    filePath = r'C:\xBladed\FOWTs\PythonScripts\iterTowerDamp2_2023_04_20___DEL_evaluation.csv'
    FirstSplittingSequences = '2B20Volt_v009_1_15mps_itr_FA_G'
    SecondSplittingSequences = '_Hz'

    filePath = r'C:\xBladed\FOWTs\PythonScripts\CheckPI_gains_2023_04_20___DEL_evaluation.csv'
    FirstSplittingSequences = '2B20Volt_v009_1_15mps_gain_P'
    SecondSplittingSequences = '_I'





    # loading data from file
    list_dict = Utility().readListDictFromCSV(filePath)

    keys = list(list_dict[0].keys())
    print('dict keys are: ', keys)

    # searching for the first sequence of chars that is equal for all run names
    RunNameRef = list_dict[0].get(keys[0])
    EqualChars_idx = 1
    for Dict in list_dict:
        RunName = Dict.get(keys[0])
        for idx in range(len(RunName)):
            if RunName[:-EqualChars_idx] == RunNameRef[:-EqualChars_idx]:
                if RunName[-EqualChars_idx-1] == '_' or RunName[-EqualChars_idx-1].isnumeric():
                    EqualChars_idx += 1
                break
            else:
                EqualChars_idx += 1
    FirstSplittingSequences = RunNameRef[:-EqualChars_idx]

    # searching for the second sequence of chars that is equal for all run names
    # first filter out the first numerical content (the start of SecondSplittingSequences)
    for idx, Char in enumerate(RunNameRef[-EqualChars_idx:]):
        if Char.isalpha() and Char != '_':
            if RunNameRef[-EqualChars_idx+idx-1] == '_':
                idx = idx - 1
            break
    # than search for the next numerical content (the end of SecondSplittingSequences)
    SecondSplittingSequences = RunNameRef[-EqualChars_idx+idx:]
    for idx, Char in enumerate(SecondSplittingSequences):
        if Char.isnumeric():
            break
    SecondSplittingSequences = SecondSplittingSequences[:idx]

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
    plt.show()
