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

### Create a function to derive shapefile from user input and creates PDF with a simple layout ##

def exportPDF(project):

    # Remove spaces from project name to add to file names #
    projectSpaceless = project.replace(" ", "")

    # Get current directory for geodatabase and convert csv file to point shapefile #
    cwd = os.getcwd()

    arcpy.env.workspace = cwd + r"\PSPGrp5.gdb"
    pointfile = arcpy.management.XYTableToPoint(cwd + r"\data.csv", r"\PointData\surveypoints" + projectSpaceless + ".shp", "Longitude", "Latitude")
    arcpy.conversion.FeatureClassToGeodatabase(cwd + r"\PointData\surveypoints" + projectSpaceless + ".shp", cwd + "\PSPGrp5.gdb")

    # Set project to work on layout and create layer file from shapefile #
    aprx = arcpy.mp.ArcGISProject(cwd + r"\PSPGrp5.aprx")

    in_layer = cwd + r"\PSPGrp5.gdb\surveypoints" + projectSpaceless 
    layers_out = "Benchmarks " + projectSpaceless 
    output_location = cwd + r"\{}.lyrx".format(layers_out)

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
    m2 = aprx.listMaps("*")[0]
    lyr = m2.listLayers("Ben*")[0]
    sym = lyr.symbology
    if lyr.isFeatureLayer and hasattr(sym, "renderer"):
        sym.renderer.symbol.applySymbolFromGallery("Circle 4")
        sym.renderer.symbol.size = 12
        sym.renderer.symbol.color = {'RGB' : [255, 0, 0, 90]}
        lyr.symbology = sym

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
    Month =str(input("\n" + "Please enter the Month (MM): "))
    Day = str(input("\n" + "Please enter the Day (DD): "))

    ProjectName=str(input("\n" + "Please enter the Project name: "))
    print("Weather Conditions:" + "\n" + "Sunny" + "\t\t" + "Cloudy" + "\t\t" + "Rainy" + "\t\t" + "Snowy" + "\t\t" + "Windy")
    WeatherCondition= str(input("\n" + "Please enter the Weather condition: "))
    IntrumentName = str(input("\n" +  "Please enter the Instrument name: "))

    #String manipulation to capitlize project name 
    Project_Capitalize=string.capwords(ProjectName)

    #String manipulation for Date
    monthdictionary = {'01': 'January','02': 'February','03': 'March','04': 'April','05': 'May','06': 'June','07': 'July','08': 'August','09': 'September','10': 'October','11': 'November','12': 'December'}
    Date = monthdictionary[Month] + " " + Day + ',' + Year 

    #String manipulation weather
    weather=string.capwords(WeatherCondition)

    #string manipulation on intrument used 
    Instrument_comma=IntrumentName.replace(',',', ')
    CapitizeInstrument=string.capwords(Instrument_comma)
    Instruments=CapitizeInstrument.split(',')

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
    StartingElevation = float(input("Please enter the Starting Elevation of the Survey: ")) # Creates Starting eleveation as a reference for subsequent calculations
    ForesightList = [] # Creates an empty list for Foresight inputs
    BacksightList = [] # Creates and empty list for Backsight inputs
    StationList = []   # Creates and empty list for station inputs
    XList = []  # Creates and empty list for X-coordinates inputs
    YList = []  # Creates and empty list for Y-coordinates inputs
    print("\n" + "Please Enter the Following: ")

    try:
        while True: # While Loop goes until the user specifies a break, allowing for traverses of all sizes.

            Station = str(input("\n" + "Enter the name of the Station: ")) 
            StationList.append(Station) # adds the foresight to the list

            Longitude = float(input("\n" + "Enter the Longitude of the Station: ")) 
            XList.append(Longitude) # adds the Longitude to the list

            Latitude = float(input("\n" + "Enter the Latitude of the Station: ")) 
            YList.append(Latitude) # adds the Latitude to the list

            Foresight = float(input("\n" + "The Foresight to the next station (If first station leave as 0): ")) 
            ForesightList.append(Foresight) # adds the foresight to the list
        
            Backsight = float(input("\n" + "The Backsight to the previous station (If last station leave as 0): ")) 
            BacksightList.append(Backsight)	# adds the backsight to the list

            print()
            answer = input("\n" + "Did you have another station (Y/N)? : ")
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
    csv_output = write_to_csv(StationList, XList, YList, BacksightList, InstrumentHeightList, ForesightList, PointElevationList)
        
    print("\n" + "Data in CSV format generated.")

    exportPDF(ProjectName)

    print("\n" + "File Exported")

if __name__ == '__main__':
    main()

