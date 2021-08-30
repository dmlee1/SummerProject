import os, re
from translationLists import *
from ScriptWritingFunctions import headWriter, generateProtocolForExistingProtocols, makeServerScripts
from supportFunctions import readFile, splitProtocol, GenerateParmLists, drawNSamples, makeServerICS
from InterventionParsingFunctions import formBaseline, formTime, formDiet, formPosture


def parseInterventions(interventions):
    correspondingTrans = []
    for line in interventions:
        if re.search("(Diet)", line, flags=re.IGNORECASE):
            correspondingTrans.append(formDiet(line))
        elif re.search("(Time)", line, flags=re.IGNORECASE):
            correspondingTrans.append(formTime(line))
        elif re.search("(Posture)", line, flags=re.IGNORECASE):
            correspondingTrans.append(formPosture(line))
        elif re.search("(Measure)", line, flags=re.IGNORECASE):
            pass
        elif re.search("(Baseline)", line, flags=re.IGNORECASE):
            correspondingTrans.append(formBaseline(line))

    return correspondingTrans


def convertIndividualProtocolToScript(folder_path, file_name, outputDirectories):
    sSpl, sSvl, sRanges, keeps = GenerateParmLists()
    sampleValues = drawNSamples(1, sRanges)

    # Read in protocol to string and then split up into 4 element list
    protocolInfo = readFile(folder_path, file_name)
    protocolInfo = splitProtocol(protocolInfo)

    # Assign each element to individual list for easier comprehension
    metaInfo = protocolInfo[0]
    conditionInfo = protocolInfo[1]
    interventionInfo = protocolInfo[2]
    measurementInfo = protocolInfo[3]

    header = headWriter("1001")

    rosterNames = translateMeasures(measurementInfo)
    rawInterventions = parseInterventions(interventionInfo)

    body = generateProtocolForExistingProtocols(rawInterventions)

    protocolName = re.split("_|\.", file_name)
    protocolName = "Patient" + protocolName[1] + "_" + protocolName[2]

    makeServerICS(outputDirectories, protocolName, sampleValues, sSpl, keeps, "Existing")
    makeServerScripts(outputDirectories, header, rosterNames, protocolName, body, 1, "Existing")


def convertMultipleProtocolsToScripts(folder_path, outputDirectories):
    folder = os.listdir(folder_path)
    sSpl, sSvl, sRanges, keeps = GenerateParmLists()

    # Only look at protocols up to this one in folder as it would take too long to look at all the other ones that caused an exception
    folder = folder[:folder.index("Protocol_12388288_1.txt")]

    for protocol_file in folder:
        sampleValues = drawNSamples(1, sRanges)
        ## skip list
        ## Some of these may be trivial to account for but left here to show some nonstandardizations present in protocols

        # skip Protocol_10752530_1.txt has it has two time lines that just have duration (including a 0 for what I assume is supposed to be baseline) and no measurement unit
        # skip Protocol_11044232_1.txt and Protocol_11044232_2.txt as both have time: Time: 13 Years on Average
        # skip Protocol_11181601_1.txt as Conditions is mispelled as Condtions
        # skip Protocol_11247959_1.txt as Interventions is spelled as Intervention
        # skip Protocol_1127101_2.txt as it has Time: 5-16 days
        # skip Protocol_11318956_1.txt and Protocol_11318956_2.txt as they have Time: 14-21 days
        # skip Protocol_11373349_1.txt as it has unstandardized diet intervention lines that program does not currently support
        # skip Protocol_11463769_1.txt, Protocol_11463769_2.txt, Protocol_11463769_3.txt as they have Time: At Least 2 Days
        # skip Protocol_11893608_1.txt and Protocol_11893608_2.txt as they have Interventions spelled as Intervention
        # skip Protocol_11924724_1.txt and Protocol_11924724_2.txt as they have Time: 5-10 minutes
        # skip Protocol_11997315_1.txt, Protocol_11997315_2.txt, Protocol_11997315_3.txt as they have Interventions spelled as Intervention
        # skip Protocol_12045366_1.txt and Protocol_12045366_2.txt as they do not have baseline as beginning of interventions
        # skip Protocol_1208596_1.txt, Protocol_1208596_2.txt, Protocol_1208596_3.txt, Protocol_1208596_4.txt, Protocol_1208596_5.txt, Protocol_1208596_6.txt , Protocol_1208596_7.txt as they have Time: 15-30 Minutes

        skip_list = ["Protocol_10752530_1.txt", "Protocol_11044232_1.txt", "Protocol_11044232_2.txt", "Protocol_11181601_1.txt",
                     "Protocol_11247959_1.txt", "Protocol_1127101_2.txt", "Protocol_11318956_1.txt", "Protocol_11318956_2.txt",
                     "Protocol_11373349_1.txt", "Protocol_11463769_1.txt", "Protocol_11463769_2.txt", "Protocol_11463769_3.txt",
                     "Protocol_11893608_1.txt", "Protocol_11893608_2.txt", "Protocol_11924724_1.txt", "Protocol_11924724_2.txt",
                     "Protocol_11997315_1.txt", "Protocol_11997315_2.txt", "Protocol_11997315_3.txt", "Protocol_12045366_1.txt",
                     "Protocol_12045366_2.txt", "Protocol_1208596_1.txt", "Protocol_1208596_2.txt", "Protocol_1208596_3.txt",
                     "Protocol_1208596_4.txt", "Protocol_1208596_5.txt", "Protocol_1208596_6.txt" , "Protocol_1208596_7.txt"]

        if protocol_file in skip_list:
            continue # skips any of the files in ignore_list

        # Read in protocol to string and then split up into 4 element list
        protocolInfo = readFile(folder_path, protocol_file)
        protocolInfo = splitProtocol(protocolInfo)

        # Assign each element to individual list for easier comprehension
        metaInfo = protocolInfo[0]
        conditionInfo = protocolInfo[1]
        interventionInfo = protocolInfo[2]
        measurementInfo = protocolInfo[3]


        header = headWriter("1001")
        rosterNames = translateMeasures(measurementInfo)
        rawInterventions = parseInterventions(interventionInfo)

        # Temporary check if no parsable intervention line (i.e. no baseline, no time measure, only drug admins, etc.)
        # Will be removed once standardization achieved (or at least when baseline added to all files)
        # This just adds what baseline returns
        if not rawInterventions:
            rawInterventions.append(["gofor", "10080"])

        body = generateProtocolForExistingProtocols(rawInterventions)

        protocolName = re.split("_|\.", protocol_file)
        protocolName = "Patient" + protocolName[1] + "_" + protocolName[2]
        makeServerICS(outputDirectories, protocolName, sampleValues, sSpl, keeps, "Existing")
        makeServerScripts(outputDirectories, header, rosterNames, protocolName, body, 1, "Existing")
