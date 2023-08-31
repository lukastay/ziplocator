import subprocess
import sys
import os

print("Starting.")
torun = True


def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])


try:
    import pandas as pd
except:
    try:
        install("pandas")
    except:
        torun = False
    else:
        import pandas as pd

try:
    import pgeocode
except:
    try:
        install("pgeocode")
    except:
        torun = False
    else:
        import pgeocode

try:
    import pathlib
except:
    try:
        install("pathlib")
    except:
        torun = False
    else:
        import pathlib

try:
    import pycountry
except:
    try:
        install("pycountry")
    except:
        torun = False
    else:
        import pycountry


def geolocation_data_adder():
    def addblankrow():
        for key in datadict.keys():
            datadict[str(key)].append("NULL")

    def countrynotfoundnumbers(countrynotfound):
        countrynotfound_unique = list(set(countrynotfound))

        countrynotfound_dict = {}

        for country_unique in countrynotfound_unique:
            timesnotfound = 0

            for countrynotfound_iteration in countrynotfound:
                if country_unique == countrynotfound_iteration:
                    timesnotfound += 1

            countrynotfound_dict[country_unique] = timesnotfound

        countrynotfound_dict = {
            k: v
            for k, v in sorted(countrynotfound_dict.items(), key=lambda item: item[1])
        }

        return countrynotfound_dict

    def countryfix(countrynotfound, country_column_name):
        countrynotfound = list(set(countrynotfound))

        for country in countrynotfound:
            country = country.title()
            while True:
                print(f"INCORRECT COUNTRY: {country}")
                country_fixed_candidate = input(
                    "Type correct country name for above country. "
                    "Or press skip to skip if you cannot figure out the correct name. \n"
                )
                country_fixed_candidate = str(country_fixed_candidate).title()

                if country_fixed_candidate.lower() == "skip":
                    break

                try:
                    candidate_title = country_fixed_candidate.title()
                    country_fixed = pycountry.countries.get(name=candidate_title)
                    country_fixed.alpha_2

                except:
                    print("That country wasn't found. Please try again.")

                else:
                    print(
                        "That is the correct country title. \n"
                        "Replacing rows in dataframe."
                    )

                    def test_column(x):
                        if x == country:
                            return country_fixed_candidate

                        else:
                            return x

                    df[country_column_name] = df[country_column_name].apply(test_column)

                    break

        return

    print("-------STARTING GEOLOCATION FINDING PROCESS---------")

    blankrows = 0
    countrynotfound = []
    yesnofix = "no"

    df[country_column_name] = df[country_column_name].fillna("None")
    df[zip_code_column_name] = df[zip_code_column_name].fillna("None")

    milestones = [
        round(it) for it in range(0, round(df.shape[0]), int(round((df.shape[0])) / 10))
    ]

    for row in range(df.shape[0]):
        if row in milestones:
            percdone = round(100 * row / df.shape[0])
            print(f"{percdone}% done with current file ({row}/{df.shape[0]})")
            milestones.remove(row)

        colloc = df.columns.get_loc(country_column_name)
        country = str(df.iloc[row, colloc])

        try:
            if len(country) > 2:
                country = pycountry.countries.get(name=country.title())
                country = country.alpha_2

        except:
            print(f"Country {country} was not found for row {row}")

            countrynotfound.append(str(df[country_column_name].loc[row]))

            blankrows += 1
            addblankrow()
            continue

        nomi = pgeocode.Nominatim(country)
        ziploc = df.columns.get_loc(zip_code_column_name)
        zip_to_query = str(df.iloc[row, ziploc])
        querydict = nomi.query_postal_code(zip_to_query).to_dict()

        if row == 0:
            datadict = {str(key): [] for key in querydict.keys()}

        tofilter = lambda key: type(datadict[str(key)]) == type([])

        for key in filter(tofilter, datadict.keys()):
            if len(str(querydict[key])) > 0:
                datadict[str(key)].append(querydict[key])

            else:
                zip_to_print = df.iloc[row, ziploc]
                print(
                    f"Cant find location data for row {row} "
                    f"Country: {country} "
                    f"Zip: {zip_to_print}"
                )
                blankrows += 1
                addblankrow()

    for key in filter(
        lambda key2: isinstance(datadict[str(key2)], list), datadict.keys()
    ):
        df[str(key)] = datadict[key]

    if blankrows == 0:
        print("Data found for all rows")
        yesnofix = "no"
        return iterationwhileadder, yesnofix

    print(
        "-----------Mistakes Fixing-------------- \n"
        f"Data not found for {blankrows} of {df.shape[0]} rows"
    )

    if len(countrynotfound) == 0:
        print("None of those rows were due to countries not being found.")
        yesnofix = "no"
        return iterationwhileadder, yesnofix

    print(
        str(len(countrynotfound)),
        "of those rows were due to countries not being found.",
    )

    yesnofix = input(
        "Type yes to fix some of those rows where country isn't found \n"
    ).lower()

    if yesnofix.lower() != "yes":
        return iterationwhileadder, yesnofix

    countrynotfound_dict = countrynotfoundnumbers(countrynotfound)

    print("Top 30 problem countries:")

    for iteration, (key, value) in enumerate(countrynotfound_dict.items()):
        if iteration < 31:
            print("Country:", key, "Number Of Rows:", value)

    while True:
        try:
            missing_number = int(
                input("How many rows will have to be missing for you to fix it? \n")
            )
        except:
            print("That's not an integer. Please enter an integer.")
        else:
            break

    countrynotfound = list(countrynotfound_dict.keys())[:missing_number]

    countryfix(countrynotfound, country_column_name)

    return iterationwhileadder, yesnofix


def getcolumns():
    zipfound = 0
    countryfound = 0

    global country_column_name
    global zip_code_column_name
    zip_code_column_name = "NULL"
    country_column_name = "NULL"

    for col in list(df.columns):
        if "zip" in col.lower():
            zip_code_column_name = col
            zipfound += 1

        for i in ["country", "nation", "kingdom"]:
            if i in col.lower():
                country_column_name = col
                countryfound += 1

    if zipfound > 1:
        zip_code_column_name = input(
            "Multiple columns with zip found in name. "
            "Enter correct zip code column name with correct capitalization \n"
        )

    if zip_code_column_name == "NULL":
        zip_code_column_name = input(
            "No column with zip code detected. "
            "Please type zip code column name with correct capitalization. \n"
        )

    while not zip_code_column_name in df.columns:
        zip_code_column_name = input(
            "That zip code column name was not found in the column names. "
            "Please try again. Make sure capitalization is correct. \n"
        )

    if countryfound > 1:
        country_column_name = input(
            "Multiple columns with country or nation or kingdom found in name. "
            "Enter correct country column name with correct capitalization. \n"
        )

    if country_column_name == "NULL":
        country_column_name = input(
            "No column with country detected. "
            "Please type coutnry column name with correct capitalization. \n"
        )

    while not country_column_name in df.columns:
        country_column_name = input(
            "That country column name was not found in the column names. "
            "Please try again. Make sure the capitalization is correct. \n"
        )

    print(
        "Columns found. \n"
        f"Zip code column: {zip_code_column_name}"
        f"Country columns: {country_column_name}"
    )

    return zip_code_column_name, country_column_name


def geoloc():
    whileiteration = 0
    global df

    while True:
        if whileiteration > 30:
            break

        file = input(
            "Go to file explorer. Right click file and click copy as path. "
            "Then paste and press enter. \n"
        )

        filelist = []

        for i in file:
            filelist.append(i)

        file = "".join(filelist)

        if file[-3:] == "csv":
            df = pd.read_csv(file)
            break

        elif file[-4:] == "xlsx":
            print(
                "Warning: you are using an excel workbook file. \n"
                "Formulas will not be saved. \n"
                "Make sure to copy and paste the data from the \n"
                "output file into your original file to keep your formulas."
            )
            warningunderstood = input(
                "Press any key and press enter to confirm you read this warning. \n"
            )

            df = pd.read_excel(file, index_col=0)

            break

        else:
            print(
                "Error: extension not csv or xlsv for file in getfilepath \n"
                f"File is {file}\n"
                "Please try again."
            )

        whileiteration += 1

    zip_code_column_name, country_column_name = getcolumns()

    yesnofix = "yes"
    global iterationwhileadder
    iterationwhileadder = 0

    while yesnofix == "yes":
        if iterationwhileadder > 15:
            break

        if iterationwhileadder > 0:
            print("-------------RESTARTING GEOLOCATION ADDER----------------")

        iterationwhileadder, yesnofix = geolocation_data_adder()

        iterationwhileadder += 1

    print(
        "----------FINISHED-------------- \n" "Done getting geolocation data for file."
    )

    if file[-3:] == "csv":
        outputfile = file[:-4] + "_GEOLOCATION.csv"

    elif file[-4:] == "xlsx":
        outputfile = file[:-5] + "_GEOLOCATION.csv"

    df.to_csv(outputfile, index=False)
    print("Geolocation file saved as", outputfile)


if torun == True:
    geoloc()

print("Excel Geolocation Finder by Lukas Taylor")

file = input("Press any key and press enter to close.")
