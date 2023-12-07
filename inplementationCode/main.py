## VerticalSurveyCalculator.py
## Last modified on December 3rd, 2023
## Authored by: 
## Matthew De Matos - ArcPy function to export data as layout
## Rajesh Dulal 
## Emmanuel Ignatius
## Alanah Reveler
## Priyanka Rathod

## Purpose
#This program allows a user to input data collected during a vertical survey (backsight, foresight,
#starting elevation, coordinates) from any number of points and calculates the elevation at each point. 
#Then it exports this data into a .csv file to be represented in a chart, which is then used to create a 
#shapefile and plot the points onto a simple layout exported as a PDF.

## Assumptions
#The user has accurate coordinate data for the benchmarks. 
#The user will be running the program from a folder that is structured with the necessary elements for 
#the program to run (this would be provided to the user as a .zip file containing the .aprx file and 
#PointData folder).

## Limitations
# To export the map, the user must be able to use ArcGIS Pro

# first, import modules needed for the program to run. 
import math                                 # 'math' is needed to run trignometric calculations
import csv                                  # '#csv' is needed to receive outputs as .csv file format
import os                                   # 'os' is needed for getcwd (current working directory)
import arcpy                                # arcpy is used for spatial outputs to be used on ArcGIS
import string                                 #'import is needed for string manipulation 

# A function to determine elevation and height of the instrument for surverying calculations
def ElevationCalculator(BS, FS, SElev):
    Elev = SElev
    HeightI = SElev + BS
    Elev = HeightI - FS
    SElev = Elev
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
        for i in range(len(BacksightList)):
            # Create a dictionary for the current row
            rowdict = {
                'Station' : StationList[i],
                'Longitude' : XList[i],
                'Latitude' : YList[j],
                'Backsight': BacksightList[i],
                'InstrumentHeight': InstrumentHeightList[i],
                'Foresight': ForesightList[i],
                'Elevation': PointElevationList[i]    
            }
            # Write the row to the CSV file
            writer.writerow(rowdict)


### Creates a function to derive shapefile from user input and creates PDF with a simple map layout ##
def exportPDF():
    # Get current directory for geodatabase and convert csv file to point shapefile #
    cwd = os.getcwd()

    arcpy.env.workspace = cwd + r"\PSPGrp5.gdb"
    pointfile = arcpy.management.XYTableToPoint(cwd + r"\data.csv", r"\PointData\surveypoints.shp", "Longitude", "Latitude")
    arcpy.conversion.FeatureClassToGeodatabase(cwd + r"\PointData\surveypoints.shp", cwd + "\PSPGrp5.gdb")

    # Set project to work on layout and create layer file from shapefile #
    aprx = arcpy.mp.ArcGISProject(cwd + r"\PSPGrp5.aprx")

    in_layer = cwd + r"\PSPGrp5.gdb\surveypoints" 
    layers_out = "Benchmarks" 
    output_location = cwd + r"\{}.lyrx".format(layers_out)

    arcpy.MakeFeatureLayer_management(in_layer, "Benchmarks")
    arcpy.SaveToLayerFile_management ("Benchmarks" , layers_out)

    # Add layer file to map at the top of the content pane #
    insertLyr = arcpy.mp.LayerFile(output_location)
    m = aprx.listMaps("*")[0]
    refLyr = m.listLayers("*")[0]
    m.insertLayer(refLyr, insertLyr, "BEFORE")

    # Save so newly created layer is retrievable by program #
    aprx.save()

    # Apply symbology to the point layer ** NOT FULLY WORKING YET #
    lyr = m.listLayers("Benchmarks")[0]
    sym = lyr.symbology
    # if lyr.isFeatureLayer and hasattr(sym, "renderer"):
    sym.renderer.symbol.applySymbolFromGallery("Circle 4")
    sym.renderer.symbol.size = 12
    lyr.symbology = sym

    # Set map frame extent to point layer and zoom out so the points are not at the edges of the frame #
    lyt = aprx.listLayouts("PointLayout")[0]
    mf = lyt.listElements("mapframe_element", "MyMapFrame")[0]
    mf.camera.setExtent(mf.getLayerExtent(lyr))
    m.defaultCamera = mf.camera
    mf.camera.scale *= 1.08

    # Export map as PDF and return completion statement
    lyt.exportToPDF(cwd + r"\PlottedPoints.pdf")
    aprx.save()
    del aprx
    return print("Map successfully exported as a PDF.")

Year = str(input("Please Enter the year (YYYY)"))
Month =str(input("Please Enter the Month (MM)"))
Day = str(input("Please Enter the Day (DD)"))

# Program to calculate the elevation of points using data acquired from a Vertical Survey.
# Display purpose of Program

print("Welcome!")
print("Calculation of Elevation of unknown points using Vertical Survey data")

#Metadata input from user

ProjectName = []
ProjectName = str(input("Please assign a name for the project: "))

InstrumentName = []
InstrumentName = str(input("Please assign a name for the instruments used for the survey: "))

InsNumber = []
InsNumber = str(input("Please number the instrument: "))

WeatherCondition = []
WeatherCondition = str(input("Please describe the weather in one or two words: "))


############## String Manipulation ###########

# test values
# ProjectName='Test project'
# WeatherCondition= 'Cloudy'
# IntrumentName = 'Tripod,rod,level'

#String manipulation to capitlize project name 
Project_Capitalize=string.capwords(ProjectName)

#String manipulation for Date
monthdictionary = {'01': 'Jan.','02': 'Feb.','03': 'March','04': 'April','05': 'May','06': 'June','07': 'July','08': 'Aug.','09': 'Sept','10': 'Oct.','11': 'Nov.','12': 'Dec.'}
Date =monthdictionary[Month] + " " + Day + ',' + Year 

#String manipulation weather
weather=string.capwords(WeatherCondition)

#string manipulation on intrument used 
Instrument_comma=IntrumentName.replace(',',', ')
CapitizeInstrument=string.capwords(Instrument_comma)
Instruments=CapitizeInstrument.split(',')

############## Meta data to txt file ###########

#Meta data to txt file
fo1 = open('README.txt', 'w')
fo1.write('Project Name: ' + Project_Capitalize+'\n'\
        + 'Date of Survey: ' + Date + '\n' \
        + 'Weather: ' + weather + '\n' \
        + 'Intruments Used: '+ '\n'\
        +' ')
# fo1= open('README.txt', 'a') 
fo1.write('\n'.join(Instruments))
fo1.close()

print("File Exported")

# Input Section
StartingElevation = float(input("Please enter the Starting Elevation of the Survey: ")) # Creates Starting eleveation as a reference for subsequent calculations
ForesightList = [] # Creates an empty list for Foresight inputs
BacksightList = [] # Creates and empty list for Backsight inputs
StationList = []   # Creates and empty list for station inputs
XList = []  # Creates and empty list for X-coordinates inputs
YList = []  # Creates and empty list for Y-coordinates inputs
print("Please Enter the Following: ")

try:
    while True: # While Loop goes until the user specifies a break, allowing for traverses of all sizes.

        Station = str(input("Enter the name of the Station: ")) 
        StationList.append(Station) # adds the foresight to the list

        Longitude = float(input("Enter the Longitude of the Station: ")) 
        XList.append(Longitude) # adds the Longitude to the list

        Latitude = float(input("Enter the Latitude of the Station: ")) 
        YList.append(Latitude) # adds the Latitude to the list

        Foresight = float(input("The Foresight to the next station (If first station leave as 0): ")) 
        ForesightList.append(Foresight) # adds the foresight to the list
    
        Backsight = float(input("The Backsight to the previous station (If last station leave as 0): ")) 
        BacksightList.append(Backsight)	# adds the backsight to the list

        print()
        answer = input("Did you have another station (Y/N)? : ")
        print()
        if  answer.upper() == 'N' : # Should make it so that lower case n inputs also work
            break
except ValueError:
    print("Value Error: Please Enter Appropriate Inputs to our Specifications.")
except TypeError:
    print("Type Error: Please Enter Appropriate Inputs to our Specifications.")
except Exception as message:
    message = "A General Error has occured, Please try rerunning the program."
    print("Error:", message)
                    
# End of Inputs

# Calculations

PointElevationList = [] # Creates an empty list to append calculated elevation into
InstrumentHeightList = [] # Creates an empty list to append calculated height of instrument into

for index in range(len(BacksightList)): # Creates an index within the range of the above inputs
    Station = StationList[index]    # retrives the station from the list for calculations
    Longitude = XList[index]    # retrives the XCoordinates from the list for calculations
    Latitude = YList[index] # retrives the YCoordinates from the list for calculations
    Backsight = BacksightList[index] # retrives the Backsight from the list for calculations
    Foresight = ForesightList[index] # retrieves the Foresight from the list for calculations 
    Elevation, InstrumentHeight = ElevationCalculator(Backsight, Foresight, StartingElevation) # calls the elevation calculations function to return elevation and Instrument Height
    PointElevationList.append(Elevation) # appends calculated elevation into the Point elevation list
    InstrumentHeightList.append(InstrumentHeight) # appends calculated Instrument Height into the list   



# Exporting values to CSV file 
# Print a message indicating that the file was written successfully
# Call the function to write the lists of values to a CSV file
csv_output = write_to_csv(StationList, XList, YList, BacksightList, InstrumentHeightList, ForesightList, PointElevationList)

# Call function to create shapefile and export layout as PDF
exportPDF()

print("Data in CSV format generated.")
