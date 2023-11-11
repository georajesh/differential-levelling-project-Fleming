#Function definition
def calculate_elevation (backsight, foresight, elevation):
    elevation = elevation + backsight - foresight
    
    return elevation

# try:
# Display program purpose
print("This application calculates and checks the elevation of differential survey data.")
print()
print('************************************************************') 
print()

table_data = {'back_sight' : 0, 'fore_sight' : 0, 'height': 0}
benchmark = float(input("Enter the elevation of benchmark: "))
#Using indefinite Lop
while True:
    back_sight = float(input("Enter the backsight reading: "))
    table_data[back_sight] += 1

    fore_sight = float(input("Enter the foresight reading: "))
    table_data[fore_sight] += 1

    height = calculate_elevation (back_sight, fore_sight, height)
    table_data[height] +=1


    answer = input("Do you want to enter another station? (Y/N)")
    answer = answer.upper()
    if answer == "N":
        break

        
# #Except specific Exception
# #General Exception
# except Exception as message:
#     print("Error: "+ message)