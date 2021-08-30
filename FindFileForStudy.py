import itertools
import re

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pomegranate import *

from supportFunctions import flattenList, splitProtocol, QuartToMeanSd
from translationLists import *


def interventionRosterScrape(directory, existingList, n1=0, n2=-1):
    listNames = existingList
    dir_path = os.listdir(directory)

    fn = [file for file in dir_path if re.search("Protocol", file)]
    stillToAdd = []

    if len(fn) < 1:
        print("Error: director not protocol")

        ## Need to ask about corresponding break in mathematica
        exit()
    else:
        for i in range(n1, len(fn)):
            with open(os.path.join(directory, fn[i]), "r") as f:
                data = f.read()
                f.close()

            roster = splitProtocol(data)[2]
            roster = re.split("\n", roster)

            int = listNames.intersection(roster)
            newElts = [x for x in roster not in int]

            # Combines lists and removes duplicates
            stillToAdd = list(dict.fromkeys(stillToAdd + newElts))


def findProtocolsByKey(directory, files, keys, section):
    sectionIndices = {"metadata": 0,
                      "conditions": 1,
                      "interventions": 2,
                      "measurements": 3
                      }

    sectionIndex = sectionIndices.get(section)

    fileList = []
    keyList = []
    for i in range(0, len(files)):
        with open(os.path.join(directory, files[i]), "r") as f:
            data = f.read()
            f.close()

        sOI = splitProtocol(data)[sectionIndex]

        key_matches = [item for x in keys for item in sOI if re.search(str(x), item)]

        # If there are key matches
        if key_matches:
            fileList.append(files[i])
            keyList.append(sOI)

    return fileList, keyList


def getInterventionsFromList(directory, files):
    interventionList = []
    for i in range(0, len(files)):
        with open(os.path.join(directory, files[i]), "r") as f:
            data = f.read()
            f.close()

        interventions = splitProtocol(data)[2]
        interventionList.append(interventions)

    return interventionList


def collectVariables(protocol, baseDir):
    dir_path = os.path.join(baseDir, "Data\\Data_" + protocol)

    header = []
    data = []
    fnRaw = os.listdir(dir_path)
    header = [re.search('Protocol_(.+?).xlsx', x).group(1) for x in fnRaw]

    for i in range(0, len(fnRaw)):
        if fnRaw[i].split(".")[1] == "xlsx":
            local = pd.read_excel(os.path.join(dir_path, fnRaw[i]), sheet_name=None, header=None, names=None)
            cleanLocal = reduceData(local)

        else:
            cleanLocal = pd.read_excel(os.path.join(dir_path, fnRaw[i]))

        ## Convert quartiles into mean and sd
        lengths = [len(j) for i in cleanLocal for j in i]
        lengths = list(set(lengths))
        if len(lengths) == 1:
            lengths = lengths[0]
            if lengths == 3:
                cleanLocal = QuartToMeanSd(cleanLocal, lengths)
        else:
            print("Error: Different lengths")

        data.append(cleanLocal)

    head = flattenList(header)
    dat = [item for sublist in data for item in sublist]
    datLengths = [len(x) for x in dat]
    if len(list(set(datLengths))) == 1:
        ## https://stackoverflow.com/questions/6473679/transpose-list-of-lists
        outputDat = list(map(list, itertools.zip_longest(*dat, fillvalue=None)))

    else:
        print("RAGGED DATA ARRAY IN PROTOCOL " + protocol)
        outputDat = []

    return list(map(list, itertools.zip_longest(*([head] + outputDat), fillvalue=None)))


def collectNumber(expDir, filename):
    with open(os.path.join(expDir, "Protocol_" + filename + ".txt")) as f:
        protocol = f.read()
        f.close()

    # Extract metadata portion
    rawMet = splitProtocol(protocol)[0]

    # Search list of metadata for element that contains 'Subjects'
    snippet = [x for x in rawMet if re.search('Subjects', x, flags=re.IGNORECASE)]
    if not snippet:
        print("Either no subjects listed or invalid entry/spelling of 'Subjects'. Check number in " + str(filename))
        return 0
    else:
        snippet = snippet[0]

    # Extract the number of participants from string
    snippet = [int(x) for x in re.findall(r'\d+', snippet)]
    if not snippet:
        print("No valid number of subjects. Check number in " + str(filename))
        return 0
    else:
        snippet = snippet[0]

    return snippet


def reduceData(data):
    data = [[sublist for sublist in x.values.tolist()] for x in list(data.values())]
    fData = [flattenList(x) for x in data]
    fullPos = [i for i in range(len(fData)) if len(fData[i])]
    return [data[i] for i in fullPos]


def harvestMeasures():
    print("Need to work on this.")


def ScrapeFilesForStudies(fileDir="", baseDir="", interventionKeys=[], metaKeys=[], conditionKeys=[]):
    if not fileDir:
        print("ScrapeFilesForStudies: Path to directory containing protocol files not passed to function.")
        print("Please recheck 1st argument value. Exiting now...")
        exit(1)
    elif not isinstance(fileDir, str):  # not a string
        print("ScrapeFilesForStudies: Argument passed for directory path to protocol files not a string.")
        print("Please recheck 1st argument value. Exiting now...")
        exit(1)
    elif not os.path.isdir(fileDir):  # path does not exist
        print("ScrapeFilesForStudies: Path provided to protocol files does not exist.")
        print("Please recheck 1st argument value. Exiting now...")
        exit(1)

    if not baseDir:
        print("ScrapeFilesForStudies: Path to base directory not passed to function.")
        print("Please recheck 2nd argument value. Exiting now...")
        exit(1)
    elif not isinstance(fileDir, str):  # not a string
        print("ScrapeFilesForStudies: Argument passed for base directory path not a string.")
        print("Please recheck 2nd argument value. Exiting now...")
        exit(1)
    elif not os.path.isdir(fileDir):  # path does not exist
        print("ScrapeFilesForStudies: Path to base directory does not exist.")
        print("Please recheck 2nd argument value. Exiting now...")
        exit(1)

    """
    Step 1
    Identify keys of interest
    Point to fill location and discover available files
    """

    dir_path = os.listdir(fileDir)
    fn = [file for file in dir_path if re.search("Protocol", file)]

    """
    Step 2
    Identify which files have the appropriate metadata and
    intervention keys from the keys described in step 1
    """

    fileList, metadataList = findProtocolsByKey(fileDir, fn, metaKeys, "metadata")
    print("Number of experiments matching metaKeys = " + str(len(fileList)))

    fileList, rawInterventionList = findProtocolsByKey(fileDir, fileList, interventionKeys, "interventions")
    print("Number of experiments matching interventionKeys = " + str(len(fileList)))

    """
    Step 3
    Construct the closure of the protocols, identifying all
    papers that include a protocol in "fileList"
    This step is optional
    """

    fileListExperiments = [re.split("_", file)[1] for file in fileList]

    matchingExperimentFiles = [x for x in fn for y in fileListExperiments if y in x]
    matchingExperimentFiles_Temp = []
    [matchingExperimentFiles_Temp.append(x) for x in matchingExperimentFiles if x not in matchingExperimentFiles_Temp]
    matchingExperimentFiles = matchingExperimentFiles_Temp

    matchingExperiments = [re.split("Protocol_|.txt", file)[1] for file in matchingExperimentFiles]

    print(matchingExperiments)
    print("Length of matching experiments = " + str(len(matchingExperiments)))

    interventionList = getInterventionsFromList(fileDir, matchingExperimentFiles)

    """
    Step 4
    Import the experimental data and clean extraneous content
    """

    collectedData = [collectVariables(experiment, baseDir) for experiment in matchingExperiments]

    """
    Step 5
    check data records to confirm all variables in listed
    experiments are represented as data
    """

    dataDir = baseDir + "Data\\"
    expDir = baseDir + "protocols\\"
    rosterPrep = []
    dataPrep = []
    weightList = []

    for index in range(len(matchingExperiments)):
        # for index in range(51, 60):

        """
        1: import experimental protocol and extract clean 
        form of measurements
        Construct roster list ("measures" and "measuresShort", 
        no spaces) for each experiment
        """

        number = collectNumber(expDir, matchingExperiments[index])
        weightList.append(number)
        with open(os.path.join(expDir, "protocol_" + matchingExperiments[index] + ".txt"), "r") as f:
            protocol = f.read()
            f.close()

        measures = splitProtocol(protocol)[3]

        """
        measuresShort is used to compare protocol roster with 
        filenames in the associated data directory to confirm match
        """
        measuresShort = [re.split("\(", x)[0].strip().replace(" ", "") for x in measures]

        """
        final version of measures is the list of HumMod 
        variable names; this automatically guarantees name and unit match
        """
        newMeasures = translateMeasures(sorted(measures, key=str.lower))

        if not (len(measuresShort) == len(newMeasures)):
            print(str(index) + "  " + str(matchingExperiments[index]))
            print("first measures = " + ", ".join(sorted(measures, key=str.lower)))
            print("newMeasures = " + ", ".join(newMeasures))
            print()

        """
        2: use "collectVariables" to extract the variables 
        seen in the data directories
        """
        collectedData = collectVariables(matchingExperiments[index], baseDir)
        dataPrep.append(collectedData)

        """
        3: check that the variables line up
        """

        variableCheck = (
                    sorted(measuresShort, key=str.lower) == sorted([mes[0] for mes in collectedData], key=str.lower))

        if variableCheck:
            rosterPrep.append(newMeasures)
        else:
            print(sorted(measuresShort, key=str.lower))
            print(sorted([mes[0] for mes in collectedData], key=str.lower))
            print(str(index) + ": variable mismatch in " + str(matchingExperiments[index]))

    """
    Step 6
    """
    voI = "SystemicArtys.Pressure"

    voIPositions = [[i, j] for i in range(len(rosterPrep)) for j in range(len(rosterPrep[i])) if
                    rosterPrep[i][j] == voI]

    voINames = [dataPrep[coordinates[0]][coordinates[1]][0] for coordinates in voIPositions]

    # Currently only takes first measurement for voI (ignores any subsequent ones)
    fullvoI = [dataPrep[coordinates[0]][coordinates[1]][1] for coordinates in voIPositions]

    minMu = min([x[0] for x in fullvoI])
    maxMu = max([x[0] for x in fullvoI])
    gap = 3 * max([x[1] for x in fullvoI])
    mm = minMu - gap
    MM = maxMu + gap

    if len(fullvoI) > 1:
        distributions = [NormalDistribution(fullvoI[i][0], fullvoI[i][1]) for i in range(len(fullvoI))]
        model = GeneralMixtureModel([dt for dt in distributions], weights=weightList)
        prob = model.probability([x for x in np.arange(mm, MM, 0.1)])

        plt.plot([x for x in np.arange(mm, MM, 0.1)], prob)
        plt.show()

    elif len(fullvoI) == 1:
        distributions = [NormalDistribution(fullvoI[0][0], fullvoI[0][1]),
                         NormalDistribution(fullvoI[0][0], fullvoI[0][1])]
        model = GeneralMixtureModel([dt for dt in distributions], weights=[weightList, weightList])
        prob = model.probability([x for x in np.arange(mm, MM, 0.1)])

        plt.plot([x for x in np.arange(mm, MM, 0.1)], prob)
        plt.show()
