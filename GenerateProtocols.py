from supportFunctions import GenerateParmLists, drawNSamples, makeServerICS
from ScriptWritingFunctions import makeServerScripts, headWriter, generateProtocol


def generateProtocolsFromText():
    return


# Currently only takes hardcoded values
def generateProtocolsHardCoded(outputDir):
    sSpl, sSvl, sRanges, keeps = GenerateParmLists()

    nnn = 5

    icsDirectories = [outputDir]
    # icsDirectories = ["InputScript"]

    rosterNames = ["System.X", "CardiacOutput.Flow", "Heart-Rate.Rate",
                   "SystemicArtys.SBP", "SystemicArtys.Pressure", "SystemicArtys.DBP",
                   "LeftHeatWallStress-Diastole.Stress-Ratio",
                   "LeftHeatWallStress-Systole.Stress-Ratio",
                   "LeftHeartPumping-Contractility.Contractility",
                   "LeftHeartPumping-Diastole.Stiffness",
                   "RightHeatWallStress-Diastole.Stress-Ratio",
                   "RightHeatWallStress-Systole.Stress-Ratio",
                   "RightHeartPumping-Contractility.Contractility",
                   "RightHeartPumping-Diastole.Stiffness",
                   "LeftHeartPumping-ContractileProtein.Mass",
                   "RightHeartPumping-ContractileProtein.Mass",
                   "LeftHeartPumping-Contractility.C-NC-Ratio", "A2Pool.[A2(pG/mL)]",
                   "ANPPool.[ANP]", "PulmVessels.BloodFlow"]

    runs = [[10080, 720], [40320, 720], [10080, 720], [10080, 720], [10080, 720]]
    interventions = [[["Apnea.EventRateTarget", 8]],
                     [["AmlodipineDailyDose.TakeDaily", 1], ["AmlodipineDailyDose.Dose", 2.5]],
                     [["LisinoprilDailyDose.TakeDaily", 1], ["LisinoprilDailyDose.Dose", 20]],
                     [["FurosemideDailyDose.TakeDaily", 1], ["FurosemideDailyDose.Dose", 500]]]

    # length of runs must always be one more than interventions
    if len(runs) != len(interventions)+1:
        print("ERROR. Length of runs provided is not equal to one more than interventions. Please check. Exiting.")
        exit(1)

    for icsIndex in range(len(icsDirectories)):
        nSamples = drawNSamples(nnn, sRanges)

        # Export
        batchFile = ""
        protocolName = "Patient{index}".format(index=str(icsIndex + 1))
        body = generateProtocol(runs, interventions)

        header = headWriter("1001")
        makeServerICS(icsDirectories[icsIndex], protocolName, nSamples, sSpl, keeps, "Nonexisting")
        makeServerScripts(icsDirectories[icsIndex], header, rosterNames, protocolName, body, nnn, "Nonexisting")


# generateProtocolsHardCoded()
