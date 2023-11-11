# Display program purpose
print("This application calculates and checks the elevation of differential survey data.")
print()
print('************************************************************') 
print()

table_data = {'backsight' : None, 'foresight' : None, 'elevation' : None}
benchmark = float(input("Enter the elevation of benchmark: "))
#Using indefinite Lop
while True:
    station = str(input("Enter the station name: "))

    back_sight = float(input("Enter the backsight reading: "))

    fore_sight = float(input("Enter the foresight reading: "))
    
    elevation = benchmark + back_sight - fore_sight
    
    key = len(table_data) + 1
    table_data[key] = {'backsight': back_sight, 'foresight': fore_sight, 'elevation': elevation}

    benchmark = elevation
    answer = input("Do you want to enter another station? (Y/N)")
    answer = answer.upper()
    if answer == "N":
        break
print("Station\t Backsight\t Foresight\t Elevation")
for item in {'backsight'}:
    print(f"{station}\t {back_sight}\t\t {fore_sight}\t\t {elevation}")
        
