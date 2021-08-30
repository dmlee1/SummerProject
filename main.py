import os

from GenerateProtocols import generateProtocolsFromText, generateProtocolsHardCoded
from GenerateScripts import convertIndividualProtocolToScript, convertMultipleProtocolsToScripts
from FindFileForStudy import ScrapeFilesForStudies


"""
Finding files for studies
-------------------------
ScrapeFilesForStudies(fileDir="", baseDir="", interventionKeys=[], metaKeys=[], conditionKeys=[])

Scrapes the protocol files present in folder provided by path in fileDir for the provided keys of interest.
First two arguments must be passed and must be valid paths, otherwise error message is printed and program exits.
Last 3 arguments are for the keys of interest. Unlike the first two, these arguments can be empty lists.
If empty, the function just will not attempt to filter out studies based on these sections.
"""

fileDir = "C:\\Users\\dmlee\\Desktop\\Summer_Project\\protocols\\"
baseDir = "C:\\Users\\dmlee\\Desktop\\Summer_Project\\"

interventionKeys = ["NaCl", "Sodium", "Salt"]
metaKeys = ["Human"]
conditionKeys = []

ScrapeFilesForStudies(fileDir, baseDir, interventionKeys, metaKeys, conditionKeys)

input("Press [ENTER} to continue: ")

"""
Generating scripts from hardcoded protocol information
-------------------------
generateProtocolsHardCoded(outputDir)

Currently, only argument is output directory. Has hardcoded intervention list and corresponding list of runtimes.
Will then generate appropriate ICS and script. Can generate multiple samples per hardcoded input.

**Note**
There are some current issues with this that need to be resolved.

Identified potential error where GenerateParmLists() from supportFunctions.py is not generating multiple sRanges.
That is, it is generating only one set of values for each variable in the generated ICS files for each of the nnn samples.
Need confirmation if this is currently mis-programmed.

Another issue is that mathematica code given had protocolname generated as Patient{index} of the length of icsDirectories passed.
This script writing function is shared with the function generating scripts from existing protocol files.
As is, this function is generating ics files named Patient{index of icsDirectories loop}_{index of nnn loop}
while the other one is generating ics files named Patient18244_01 from Protocol_18244_1.
Need advice on this section.

One further issue is that I'm not sure what is supposed to be passed to the headWriter function. The example scripts all
had '1001' being passed, so that's what's currently been hardcoded as the argument. Please advice if it needs to be
programmatically generated.

One vital thing not currently implemented is any potential conditions (such as in currently generated protocols) that might
impact variable values in ICS. This has been currently reserved as future work.

"""
outputDir = os.path.join(baseDir, "Output")
generateProtocolsHardCoded(outputDir)

print("generateProtocolsHardCoded complete. Please check outputDir for outputted files.")
input("Press [ENTER} to continue: ")

"""
Generating scripts from generated text files
-------------------------
generateProtocolsFromText()

Current plan is to accomplish the same as above hardcoded function but from a programmatically generated text file.
No actions taken to programming it yet as need guidance on standardized format for imported text file.

"""


"""
Generating script from individual protocol file
-------------------------
convertIndividualProtocolToScript(folder_path, file_name, outputDirectories)

Converts existing protocol file to script. Like mentioned above, there is no current implementation of the conditions
portion affecting variable values in ICS. As of right now, the values in the ICS are being taken from the NORMAL.ICS
provided in Hummod folder

It is able to parse some of the diet interventions (mostly tested on sodium/salt ones). There are some existing sodium diet
administrations that this program is not able to handle at the moment. Waiting for standardization before proceeding.

Cannot handle medication interventions. Currently just skips it and resulting script is missing any medication interventions.
Waiting for standardization before proceeding. 

Posture and time able to be handled without issue.

Sample file Protocol_16357094_1.txt used as it does not have any medication administration as well as diet ones that
can currently be handled.
"""

file_n = "Protocol_16357094_1.txt"
convertIndividualProtocolToScript(fileDir, file_n, outputDir)

print("convertIndividualProtocolToScript complete. Please check outputDir for outputted files.")
input("Press [ENTER} to continue: ")


"""
Generating scripts from multiple protocol files
-------------------------
convertMultipleProtocolsToScripts(folder_path, outputDirectories)

Does the same as above function except will iterate over any protocol file present.
Has the same limitations as above.

For current progress presentation, it only goes up to Protocol_12388288_1.txt as it would take too much time to make
exemptions for files that broke the current code. Can go back at later date and update the skip list to include all files
with nonstandardized input.

Current protocols being explicitly skipped have comments in the function in GenerateScripts.py for information why
it had to be skipped.

Also, some protocols have no interventions that can be parsed from it, so there is a current, temporary if statement
that just adds a baseline gofor line so that the code doesn't break.
"""

convertMultipleProtocolsToScripts(fileDir, outputDir)

print("convertMultipleProtocolsToScripts complete. Please check outputDir for outputted files.")
input("Press [ENTER} to continue: ")


# if __name__ == '__main__':
#     print("Hello")
