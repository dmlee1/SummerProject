import numpy as np
import os, re
from itertools import chain, zip_longest
from globalVariables import hummodPath


# reads protocol file and read contents to string
def readFile(folder, fn):
    with open(os.path.join(folder, fn), "r") as f:
        data = f.read()
        f.close()
    return data


# To flatten list that are more than 2 levels deep
def flattenList(init_list):
    list_types = [True if type(t) == list else False for t in init_list]
    while any(list_types):
        init_list = [item for sublist in init_list for item in sublist]
        list_types = [True if type(t) == list else False for t in init_list]
    return init_list


def splitProtocol(protocol):
    """
    Splits protocol file into 4 parts:
    0th element = metadata
    1st element = conditions
    2nd element = interventions
    3rd element = measurements
    """
    protocol = protocol.replace(" \n", "\n")
    splitInfo = re.split("Metadata|^Conditions$|Interventions|Measurements", protocol, flags=re.MULTILINE)
    splitInfo = list(filter(None, splitInfo))
    splitInfo = [x.strip('\n') for x in splitInfo]

    # Remove beginning and ending parentheses in metadata section
    splitInfo[0] = splitInfo[0].replace("(", "").replace(")", "")

    # Split the list elements by comma if metadata section and by \n in the others
    splitInfo = [splitInfo[i].split(",") if i == 0 else splitInfo[i].split("\n") for i in range(len(splitInfo))]

    # Strip any leading or trailing whitespaces in any individual element in each nested list
    splitInfo = [[y.strip() for y in x] for x in splitInfo]

    return splitInfo


def QuartToMeanSd(data, lengths):
    for i in range(len(data[0])):
        tempx = data[0][i]
        mu = sum(tempx) / lengths
        Q25 = tempx[1]
        Q75 = tempx[2]
        sd = (Q75 - Q25) / 1.34898
        data[0][i] = [mu, sd]
    return data


def drawNSamples(number, ranges):
    samples = []
    for i in range(number):
        nums = []
        for a_range in ranges:
            nums.append(np.random.uniform(a_range[0], a_range[1]))
        samples.append(nums)
    return samples


def extractLine(ICS, pp):
    spList1 = []
    spList2 = []

    for match in re.finditer(re.escape('<name> ' + pp + ' '), ICS):
        spList1.append([match.start(), match.end()])

    sp1 = spList1[0][0]
    str1 = ICS[sp1:(sp1 + 500)]
    for match in re.finditer(re.escape('</var>'), str1):
        spList2.append([match.start(), match.end()])

    sp2 = sp1 + spList2[0][-1]
    return [sp1 - 6, sp2]


def cutDeck(ics, spl, svl, Ranges):
    spots = [extractLine(ics, x) for x in spl]

    sortSpots = [list(a) for a in zip(spots, spl, svl, Ranges)]
    sortSpots = sorted(sortSpots, key=lambda x: (x[0]))

    # Extract each of the list elements after sorting
    sRanges = [x[3] for x in sortSpots]
    sSvl = [x[2] for x in sortSpots]
    sSpl = [x[1] for x in sortSpots]
    sSpots = [x[0] for x in sortSpots]

    # Flatten sSpots into 1D list & then prepend 0 and append -1
    dummy = [item for sublist in sSpots for item in sublist]
    dummy.insert(0, 0)
    dummy.append(-1)

    # Renest list into a 2D list of lists of size 2
    regs = [dummy[i:i + 2] for i in range(0, len(dummy), 2)]

    # Extract ics lines that do not contain any of the extracted parameters and values
    keeps = [ics[x[0]:x[1]] for x in regs]

    return sSpl, sSvl, sRanges, keeps


def icsvarFill(p, v):
    return "\n<var><name> " + p + " </name><val> " + str(v) + " </val></var>"


def makeServerICS(destination, name, samples, sspl, keeps, whichCallingFunction=""):

    trans = checkPath(os.path.join(destination, "ICS_Files"))
    for j in range(len(samples)):
        if whichCallingFunction == "Existing":
            tempName = name
        elif whichCallingFunction == "Nonexisting":
            tempName = name + "_" + str(j+1)
        table = []
        for i in range(len(sspl)):
            table.append(icsvarFill(sspl[i], samples[j][i]))
        newics = [x for x in chain.from_iterable(zip_longest(keeps, table)) if x is not None]
        newics = ''.join(newics)

        with open(os.path.join(trans, tempName + ".ICS"), "w") as f:
            f.write(newics)
            f.close()


def MakeDesktopICS(destination, name, samples, sspl, keeps):
    Samples = [float(x) for x in samples]
    trans = checkPath(destination)
    for j in range(len(Samples)):
        tempName = name + str(j)
        table = []
        for i in range(len(sspl)):
            table.append(icsvarFill(sspl[i], Samples[j][i]))
        newics = [val for pair in zip(keeps, table) for val in pair]
        with open(trans + tempName + ".ICS", "w") as f:
            f.write(newics)
            f.close()


def checkPath(destination):
    if not os.path.exists(destination):
        os.makedirs(destination)
    return destination


def getParmsAndRanges(structDir, eps=0.05):
    dir_path = os.path.join(structDir, "Structure\\")
    fullParameterList = []
    fullValList = []
    fnParticular = []
    for root, dirs, files in os.walk(dir_path):
        for file in files:
            if file.endswith(".DES"):
                fnParticular.append(os.path.join(root, file))

    for j in range(len(fnParticular)):
        with open(fnParticular[j], "r") as f:
            data = f.read()
            f.close()
        parmList, valList = parmSearch(data)
        fullParameterList = fullParameterList + parmList
        fullValList = fullValList + valList
    rawList = [list(a) for a in zip(fullParameterList, fullValList)]
    finalList = [x for x in rawList if not (clearTest(x[0]))]
    spl = [x[0] for x in finalList]
    svl = [x[1] for x in finalList]
    dev = [eps * x for x in svl]
    Ranges = [[x - y, x + y] for x, y in zip(svl, dev)]
    snakeSPL = [parm.replace(".", "-") for parm in spl]
    return finalList, Ranges, snakeSPL


def clearTest(x):
    list_to_check = ["Clamp", "Switch", "Setting", "Pump", ".k", ".K", "Level", "Tau",
                     "Initial", "(%)", "Stenosis", "p50", "Pain", "OR", "(Days)",
                     "DC", "Metabolism", "Medulla", "Albumin", "IgG", "AGP",
                     "Available", "Pheochr", "RespiratoryCenter", "FailureRate",
                     "AldoTumor", "Bronchi", "Flux", ".Block", "Arrest", "Pelvis",
                     "Count", "Supply", "Context", "Anesthe", "Bone", "Ca.", "Adrenal",
                     "Fistula", "Adrenal", "Cerebrospina", "SID", "Degrad", "Apnea",
                     "Diet", "Daily", "Creat", "Thiaz", "Mido", "GIL", "Calcitonin",
                     "Random", "Cortisol", "CPR", "RBC", "N2", "CO", "Exercise",
                     "Hypoth", "EPO", "Estrad", "Test", "FSH", "Furos", "CellPro",
                     "Aceta", "Altitude", "hCG", "IV", "BreathHolding", "Dialy",
                     "Perito", "Posture", "Hydro", "Other", "Temp", "Corpus", "Ovarie",
                     "Bolus", "Atropine", "?", "Hgb", "Peric", "Insul", "Skin", "Torso",
                     "GlucosePool", "Lung", "Infarct", "Mineralocorticoid", "Lipid", "LH",
                     "Leptin", "Pleural", "constitu", "Thyroid", "Sizing", "Vitamin", "Block",
                     "GnRH", "Gravity", "Spirono", "Digoxin", "Desgly", "Hemit", "RespiratoryM",
                     "Cushin", "Clothes", "Follicle", "Inhi", "Para", "Oral", "OGTT", "Regurg",
                     "Sweat", "Skele", "Venti", "Gluca", "Panc", "Proge", "Table", "Hemorr",
                     "Wind", "usProt", "LowerEx", "Patent", "Constitu", "Essential", "ACTH",
                     "Cortis", "PlasmaPro", "Releasing", "Humidity", "Defib", "Glycerol",
                     "Pulmonary", "Submerg", "Reserpine", "Morphine", "Propran", "Narcan",
                     "Heta", "Isoproter", "Phenyleph", "Acetylec", "Blunt", "ProximalTubule_Conductance",
                     "PleuralCavity.Serous", "Transfusion", "Venae", "CCB", "THZ", "_Na.RLoadS",
                     "_Na.LoadS", "_Na.Load_S1Target", "_Na.Load_STarget"]
    for substring in list_to_check:
        if substring in x:
            return True
    return False


def parmSearch(x):
    data = x
    parmList = []
    valList = []

    splits = re.split("\<name\>|\<\/name\>", data, maxsplit=2)
    if len(splits) > 1:
        sName = splits[1].replace(" ", "")
        sC = data.count("<parm>")
        if sC > 0:
            for psIndex in range(sC):
                unit = re.split("\<parm\>|\<\/parm\>", data, maxsplit=2)
                newParm = sName + "." + \
                          re.split("\<name\>|\<\/name\>", unit[1].replace(" ", "").replace("\n", ""), maxsplit=2)[
                              1].replace(" ", "")
                newVal = re.split("\<val\>|\<\/val\>", unit[1], maxsplit=2)[1].replace(" ", "")

                if newVal == "TRUE":
                    newVal = 1
                elif newVal == "FALSE":
                    newVal = 0
                elif newVal == "UNDEFINED":
                    newVal = 0

                newVal = float(newVal)
                parmList.append(newParm)
                valList.append(newVal)
                data = "".join(unit[2:])

    return parmList, valList


def GenerateParmLists():
    finalList, Ranges, snakeSPL = getParmsAndRanges(hummodPath)

    ICS_fold = hummodPath
    ICS_name = "Normal"
    ICS_path = os.path.join(ICS_fold, ICS_name + ".ICS")
    with open(ICS_path, "r") as f:
        ICS_str = f.read()
        f.close()

    sSpl, sSvl, sRanges, keeps = cutDeck(ICS_str, [x[0] for x in finalList], [x[1] for x in finalList], Ranges)
    return sSpl, sSvl, sRanges, keeps
