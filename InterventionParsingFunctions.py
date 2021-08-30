import re
from translationLists import *

def formDiet(line, transList=dietTranslationList):
    nutrient = ""
    amount = ""
    period = ""

    # If dietary line contains Low *** Diet or High *** Diet
    # Can be removed once standardization applied to all future protocols
    if bool(re.search("(Low|High).*(Diet)", line, flags=re.IGNORECASE)):
        # print("--------------")
        nutrient = re.split("Diet", line[0:line.index("(")])[0].strip()
        nutrient = re.split("(Low|High)", nutrient, flags=re.IGNORECASE)[2].strip()
        y = re.search("\((.+)\)", line).group(1)
        if y.count("/") > 0:
            print("Check under first if statement in formDiet!!")
            exit(1)
        else:
            periodTrans = {"daily": "day"}

            quantity = re.split("(\d+)", y)[1].strip()
            amount = re.split("(\d+)", y)[2].strip()
            unit = amount.split()[0].lower()
            period = amount.split()[1].lower()

            # convert medication administration period to appropriate term
            if period in periodTrans:
                period = periodTrans.get(period)

            searchTerm = nutrient + " " + unit


    ## All other cases
    else:
        nutrient = re.split("Dietary", line[0:line.index("(")])[1].replace("Intake", "").strip()
        y = re.search("\((.+)\)", line).group(1)

        ## If amount contains more than 2 slashes, e.g. G/kg body weight/Day
        if y.count("/") >= 2:
            amount = y[0:y.rindex("/")].strip()
            period = y[y.rindex("/") + 1:len(y)].strip()

        ## If amount only contains one slash, e.g. mmol/Day
        elif y.count("/") == 1:
            amount, period = [x.strip() for x in re.split("\/", y)]
        else:
            print("ERROR IN FORMDIET")

        quantity = amount[0:amount.index(" ")]
        unit = amount[amount.index(" ") + 1:len(amount)]

        unit = unit.lower()
        period = period.lower()
        searchTerm = nutrient + " " + unit

    # Retrieves corresponding Hummod diet variable
    parm = transList.get(searchTerm)

    return [parm, quantity]


def formTime(line="", transList=unitTranslationList):
    splits = re.split("Time:(?:\s)*|\s", line)
    period = splits[1].strip()
    unit = splits[2].strip().lower()

    # Get appropriate multiplication value to convert whatever time unit into minutes
    mult = transList.get(unit)
    value = str(float(period) * int(mult))

    return ["gofor", value]


def formPosture(line="", transList=postureTranslationList):
    splits = re.split("Posture\s?=", line)
    posture = splits[1].strip()

    # Retrieves Hummod posture variable
    control = transList.get(posture)

    return control

def formMedication(line=""):
    # To be created once medication administration standardized

    return


def formBaseline(line=""):
    return ["gofor", "10080"]