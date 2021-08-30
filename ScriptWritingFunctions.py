import os
from supportFunctions import checkPath


def headWriter(model):
    str1 = "\nModel(\"{model_insert}\"); \n".format(model_insert=model)
    str2 = "Auth(\"client-m-01\", \"nXzG6x04y6mGfnZj3\");\n\n"
    str3 = "	Restart();\n"
    return str1 + str2 + str3


def rosterWriter(rost_names=[]):
    roster = ""
    if rost_names:
        head = "\nRoster(new string[]\n{\n"
        tail = "});\n\n"
        roster = head
        for i in rost_names:
            roster = roster + "\"{i}\",\n".format(i=i)
        roster = roster + tail
    return roster


def loadICSWriter(name=""):
    if name:
        return "LoadICS(\"{ICS_name}\");\n\n".format(ICS_name=name)
    return ""


def goforWriter(time_info):
    if len(time_info) == 2:
        if time_info[0] == "gofor":
            return "GoFor({time_str}, {time_str});\n".format(time_str=str(time_info[1]))
        else:
            if time_info[0] * time_info[1] == 0:
                return ""
            else:
                return "GoFor({time_str}, {int_str});\n".format(time_str=str(time_info[0]), int_str=str(time_info[1]))
    else:
        print("List passed to goforWriter is not of length 2. Please investigate.")
        print("Exiting now...")
        exit(1)


def setValWriter(name, val):
    return "SetValue(\"{name}\", {value});\n".format(name=name, value=str(val))


def saveSolWriter(name=""):
    if name:
        return "\nSaveSolutionLocal(\"{name}\");\n".format(name=name)
    return ""


def saveICSWriter(name):
    return "SaveICSLocal(\"{name}\");\n\n".format(name=name)


# Generates interventions for Scripts
def generateProtocol(runs, interventions):
    body = ""
    if len(runs) != len(interventions) + 1:
        print("there should be one more gofor than intervention")
    else:
        body = goforWriter(runs[0])
        for protIndex in range(len(interventions)):
            tempIntervention = []
            for intIndex in range(len(interventions[protIndex])):
                tempIntervention.append(setValWriter(interventions[protIndex][intIndex][0],
                                                     interventions[protIndex][intIndex][1]))
            body = body + ''.join(tempIntervention) + goforWriter(runs[protIndex + 1])
    return body


def generateProtocolForExistingProtocols(interventions):
    body = ""

    if interventions[0][0] == "gofor":
        body = goforWriter(interventions[0])
    else:
        # print("ERROR: first line on intervention is not initial baseline")
        # exit(1)
        print("WARNING: first line on intervention list is not initial baseline")

    for line in interventions[1:]:
        if line[0] == "gofor":
            body = body + goforWriter(line)
        else:
            body = body + setValWriter(line[0], line[1])

    return body


def makeServerScripts(file_dest, header, rosterNames, protocolName, body, nnn=1, whichCallingFunc="", serverDir=None):
    roster = rosterWriter(rosterNames)
    batchFile = ""

    for i in range(1, nnn + 1):
        if whichCallingFunc == "Existing":
            localName = protocolName
        else:
            localName = protocolName + "_" + str(i)
        script = header + roster + loadICSWriter(localName + ".ICS") + body + \
                 saveSolWriter(localName + ".CSV") + "ClearRoster();\n" + saveICSWriter(localName + "-Finished.ICS")
        scriptName = os.path.join(checkPath(file_dest), localName + ".CSX")
        with open(scriptName, "w+") as f1:
            f1.write(script)
            f1.close()
