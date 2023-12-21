## VerticalSurvey.py
## Last modified: December 7, 2023
## Authored by:
# Matthew De Matos - ArcPy function, comments at top of code
# Rajesh Dulal - Write to CSV, Arithmetic check functions, calculations, user input
# Emmanuel Ignatius - Test values
# Priyanka Rathod - User input, test values
# Alanah Reveler - User input string manipulation, test values, metadata export

## This program is designed for surveyors to be able to input the field data they have collected
# during a closed vertical survey and have an automatic output of their field data, calculations
# of elevation for each point, and a small, simple map with the outputs plotted. This will expedite
# many of the post-processes that surveyors need to complete after they finish their surveys.

## Program structure:
# The main program function first asks for the user to input their field data. Before measurements are entered, a 
# .txt file is created. Then the user inputs their measurements and coordinates for as many points as
# they need. An arithmetic check (function) is performed for vertical accuracy, and if it is successful, a function 
# to export a table with the values to a .csv file. This .csv file is then used in a final function to create a shapefile
# that is added to an ArcGIS Pro project so the points can be plotted on a map and exported as a PDF.

## Assumptions
# The user has accurate coordinate data for the points in the survey
# The user has access to ArcGIS Pro and the version of ArcGIS Pro can complete these functions
# Program is run in the ArcGIS Python environment
# The user has downloaded the folder with the necessary structure to run properly
# The curvature of small paths has an almost null effect on the surveyed part of the earth's surface

## Limitations
# Measurements are not atmospherically corrected
# Cannot be used for open traverses
# User can only input 3 decimals for coordinate values

## Special Cases and Known Problems
# Program accepts future year inputs and impossible days of the month
# Inputs could be more efficient and user friendly
# Coordinate input should not be required for turning points - this program requires more fieldwork with GPS

## Class content by Karen Whillans from GEOM 67 (Fall 2023 Term) at Fleming College extensively referenced to complete this code ##

# first, import modules needed for the program to run. 
import csv                                  # '#csv' is needed to receive outputs as .csv file format
import os                                   # 'os' is needed for getcwd (current working directory)
import arcpy                                # arcpy is used for spatial outputs to be used on ArcGIS
import string                               # string is for string manipulation

# A function to determine elevation and height of the instrument for surverying calculations
def ElevationCalculator(BS, FS, SElev):
    HeightI = SElev + BS
    Elev = HeightI - FS
    return Elev, HeightI

# Create a function that takes in five lists of values and a file name
def write_to_csv(StationList, XList, YList, BacksightList, InstrumentHeightList, ForesightList, PointElevationList):

    # Create a list of fieldnames
    fieldnames = ['Station', 'Longitude', 'Latitude', 'Backsight', 'InstrumentHeight', 'Foresight', 'Elevation']

    # Open the file in write mode and create a csv writer
    with open('data.csv', 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        # Write the header row
        writer.writeheader()

        # Iterate over the lists of values and write each row
        for i in range(len(ForesightList)):
            # Create a dictionary for the current row
            rowdict = {
                'Station' : StationList[i],
                'Longitude' : XList[i],
                'Latitude' : YList[i],
                'Backsight': BacksightList[i],
                'InstrumentHeight': InstrumentHeightList[i],
                'Foresight': ForesightList[i],
                'Elevation': PointElevationList[i]    
            }
            # Write the row to the CSV file
            writer.writerow(rowdict)

#This is a function to calculate the arithmetic check on surveyed data.
def acheck(ElevationList, BList, FList):
    if (ElevationList[0] - ElevationList[-1]) == (sum(BList) - sum(FList)):
        print("The arithmetic check is done. It seems everything is correct.")
    else:
        print("The check is incomplete. It seems there is an error in your data.")

### Create a function to derive shapefile from user input and creates PDF with a simple layout ##
## ArcGIS documentation for ArcPy extensively used for this section - https://pro.arcgis.com/en/pro-app/3.1/arcpy/get-started/installing-python-for-arcgis-pro.htm ##
def exportPDF(project):

    # Remove spaces from project name to add to file names #
    projectSpaceless = project.replace(" ", "")

    # Get current directory for geodatabase and convert csv file to point shapefile #
    cwd = os.getcwd()

    arcpy.env.workspace = cwd + r"\PSPGrp5.gdb"
    arcpy.management.XYTableToPoint(cwd + r"\data.csv", r"\PointData\surveypoints" + projectSpaceless + ".shp", "Longitude", "Latitude")
    arcpy.conversion.FeatureClassToGeodatabase(cwd + r"\PointData\surveypoints" + projectSpaceless + ".shp", cwd + "\PSPGrp5.gdb")

    # Set project to work on layout and create layer file from shapefile #
    aprx = arcpy.mp.ArcGISProject(cwd + r"\PSPGrp5.aprx")

    in_layer = cwd + r"\PSPGrp5.gdb\surveypoints" + projectSpaceless 
    layers_out = "Benchmarks " + projectSpaceless 
    output_location = cwd + r"\{}.lyrx".format(layers_out)
    
    ##Referenced https://gis.stackexchange.com/questions/217980/arcpy-makefeaturelayer-management-for-feature-class-within-feature-dataset-with for help ##
    arcpy.MakeFeatureLayer_management(in_layer, "Benchmarks " + projectSpaceless)
    arcpy.SaveToLayerFile_management ("Benchmarks " + projectSpaceless, layers_out)

    # Add layer file to map at the top of the content pane #
    insertLyr = arcpy.mp.LayerFile(output_location)
    m = aprx.listMaps("*")[0]
    refLyr = m.listLayers("*")[0]
    m.insertLayer(refLyr, insertLyr, "BEFORE")

    # Save copy so newly created layer is retrievable in project copy, change aprx variable to new project #
    aprx.saveACopy(cwd + r"\Plotted" + projectSpaceless + ".aprx")
    del aprx

    # Set project to work on layout and create layer file from shapefile #
    aprx = arcpy.mp.ArcGISProject(cwd + r"\Plotted" + projectSpaceless + ".aprx")

    # # Apply symbology to the point layer #
    ## Karen Whillans assisted with the symbology section ##
    m2 = aprx.listMaps("*")[0]
    lyr = m2.listLayers("Ben*")[0]
    sym = lyr.symbology
    if lyr.isFeatureLayer and hasattr(sym, "renderer"):
        sym.renderer.symbol.applySymbolFromGallery("Circle 4")
        sym.renderer.symbol.size = 12
        sym.renderer.symbol.color = {'RGB' : [255, 0, 0, 90]}
        lyr.symbology = sym

    ## Referenced https://gis.stackexchange.com/questions/429842/using-arcpy-with-arcgis-pro-to-zoom-to-features-and-export-pdf for help with zoom to layer ##
    # Set map frame extent to point layer and zoom out so the points are not at the edges of the frame #
    lyt = aprx.listLayouts("PointLayout")[0]
    mf = lyt.listElements("mapframe_element", "MyMapFrame")[0]
    mf.camera.setExtent(mf.getLayerExtent(lyr))
    m.defaultCamera = mf.camera
    mf.camera.scale *= 1.08

    # Change title to include project name and export to PDF
    txts = lyt.listElements()
    for txt in txts:
        if txt.name == "Title":
            txt.text = project + " Vertical Survey Benchmarks"

    lyt.exportToPDF(cwd + r"\PlottedPoints" + projectSpaceless + ".pdf")

    aprx.save()
    del aprx

# Input Section
def main():
    # Metadata Input
    print("****************You have entered the metadata input section.****************")
    Year = str(input("Please enter the year (YYYY): "))
    Month =str(input("\n" + "Please enter the month (MM): "))
    Day = str(input("\n" + "Please enter the day (DD): "))

    ProjectName=str(input("\n" + "Please enter the project name: "))
    print("Weather Conditions:" + "\n" + "Sunny" + "\t\t" + "Cloudy" + "\t\t" + "Rainy" + "\t\t" + "Snowy" + "\t\t" + "Windy")
    WeatherCondition= str(input("\n" + "Please enter the weather condition: "))
    InstrumentName = str(input("\n" +  "Please enter the instrument name: "))

    #String manipulation to capitlize project name 
    Project_Capitalize=string.capwords(ProjectName)

    #String manipulation for Date
    monthdictionary = {'01': 'January','02': 'February','03': 'March','04': 'April','05': 'May','06': 'June','07': 'July','08': 'August','09': 'September','10': 'October','11': 'November','12': 'December'}
    Date = monthdictionary[Month] + " " + Day + ',' + Year 

    #String manipulation weather
    weather=string.capwords(WeatherCondition)

    #string manipulation on intrument used 
    Instrument_comma=InstrumentName.replace(',',', ')
    CapitalizeInstrument=string.capwords(Instrument_comma)
    Instruments=CapitalizeInstrument.split(',')

    ############## Meta data to txt file ###########

    #Meta data to txt file
    fo1 = open('metadata.txt', 'w')
    fo1.write('Project Name: ' + Project_Capitalize+'\n'\
            + 'Date of Survey: ' + Date + '\n' \
            + 'Weather: ' + weather + '\n' \
            + 'Intruments Used: '+ '\n'\
            +' ')
    # fo1= open('README.txt', 'a') 
    fo1.write('\n'.join(Instruments))
    fo1.close()

    print("File Exported")

    print()
    print()
    print()
    print()
    print()
    print()

    # Survey Data Input
    print("****************You are on the survey data input Section.******************")
    StartingElevation = float(input("Please enter the starting elevation of the survey: ")) # Creates Starting eleveation as a reference for subsequent calculations
    ForesightList = [] # Creates an empty list for Foresight inputs
    BacksightList = [] # Creates and empty list for Backsight inputs
    StationList = []   # Creates and empty list for station inputs
    XList = []  # Creates and empty list for X-coordinates inputs
    YList = []  # Creates and empty list for Y-coordinates inputs
    print("\n" + "Please Enter the Following: ")

    try:
        while True: # While Loop goes until the user specifies a break, allowing for traverses of all sizes.

            Station = str(input("\n" + "Enter the name of the station: ")) 
            StationList.append(Station) # adds the foresight to the list

            Longitude = float(input("\n" + "Enter the longitude of the station: ")) 
            XList.append(Longitude) # adds the Longitude to the list

            Latitude = float(input("\n" + "Enter the latitude of the station: ")) 
            YList.append(Latitude) # adds the Latitude to the list

            Foresight = float(input("\n" + "Enter the foresight to the next station (If first station, leave as 0): ")) 
            ForesightList.append(Foresight) # adds the foresight to the list
        
            Backsight = float(input("\n" + "Enter the backsight to the previous station (If last station, leave as 0): ")) 
            BacksightList.append(Backsight)	# adds the backsight to the list

            print()
            answer = input("\n" + "Did you have another station (Y/N)? : ")
            print()
            if  answer.upper() == 'N' : # Should make it so that lower case n inputs also work
                break
    except ValueError:
        print("Value Error: Please enter appropriate inputs to our specifications.")
    except TypeError:
        print("Type Error: Please enter appropriate inputs to our specifications.")
    except Exception as message:
        message = "A General Error has occured, Pease try rerunning the program."
        print("Error:", message)
                        
    # End of Inputs

    # Calculations
    Elevation = StartingElevation
    PointElevationList = [StartingElevation] # Creates an empty list to append calculated elevation into
    InstrumentHeightList = [] # Creates an empty list to append calculated height of instrument into
    for index in range(len(ForesightList)-1): # Creates an index within the range of the above inputs
        Station = StationList[index]    # retrives the station from the list for calculations
        Longitude = XList[index]    # retrives the XCoordinates from the list for calculations
        Latitude = YList[index] # retrives the YCoordinates from the list for calculations
        Backsight = BacksightList[index] # retrives the Backsight from the list for calculations
        Foresight = ForesightList[index +1] # retrieves the Foresight from the list for calculations 
        Elevation, InstrumentHeight = ElevationCalculator(Backsight, Foresight, Elevation) # calls the elevation calculations function to return elevation and Instrument Height
        PointElevationList.append(Elevation) # appends calculated elevation into the Point elevation list
        InstrumentHeightList.append(InstrumentHeight) # appends calculated Instrument Height into the list   
    InstrumentHeightList.append(0) # appends final Instrument Height into the list as 0

    # Exporting values to CSV file 
    # Print a message indicating that the file was written successfully
    # Call the function to write the lists of values to a CSV file
    write_to_csv(StationList, XList, YList, BacksightList, InstrumentHeightList, ForesightList, PointElevationList)
        
    print("\n" + "Data in CSV format generated.")
    #Calls the function to do Arithmatic Check
    acheck(PointElevationList, BacksightList, ForesightList)

    #Exports the point map into the pdf.
    exportPDF(ProjectName)

    print("\n" + "File Exported")

if __name__ == '__main__':
    main()