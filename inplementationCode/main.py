# first, import modules needed for the program to run. 
import math                                 # 'math' is needed to run trignometric calculations
import csv                                  # '#csv' is needed to receive outputs as .csv file format
import os                                   # 'os' is needed for getcwd (current working directory)
# import arcpy                                # arcpy is used for spatial outputs to be used on ArcGIS

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
        for i in range(len(PointElevationList)):
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

PointElevationList = [StartingElevation] # Creates an empty list to append calculated elevation into
InstrumentHeightList = [] # Creates an empty list to append calculated height of instrument into

for index in range(len(PointElevationList)): # Creates an index within the range of the above inputs
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
    
print("Data in CSV format generated.")