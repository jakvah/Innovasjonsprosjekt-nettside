import xlsxwriter
import dbTransmit
import MySQLdb

filename = "/var/www/FlaskApp/FlaskApp/xltest.xlsx"

dbconn = MySQLdb.connect("localhost","jakob","","Vikelva")

dataset = dbTransmit.getDateData("2019-03-15","Vikelva")
#dbTransmit.createExcel(dataset,filename)

wb = xlsxwriter.Workbook('test.xlsx')
ws = wb.add_worksheet()


time_list = []
ph_list = []
turb_list = []
kond_list = []
temp_list = []
dato_list = []

for rad in dataset:
	dato_list.append(rad[1])
	time_list.append(rad[2])
	ph_list.append(float(rad[3]))
	temp_list.append(float(rad[4]))
	turb_list.append(float(rad[5]))
	kond_list.append(float(rad[6]))

# Setter opp header
ws.write(2,0,"Dato")
ws.write(2,1,"Klokkeslett")
ws.write(2,2,"pH")
ws.write(2,3,"Temperatur")
ws.write(2,4,"TDS")
ws.write(2,5,"Turbiditet")

row = 3

for x in range(len(dato_list)):
	ws.write(row, 0,dato_list[x])
	ws.write(row,1,time_list[x])
	ws.write(row,2,ph_list[x])
	ws.write(row,3,temp_list[x])
	ws.write(row,4,kond_list[x])
	ws.write(row,5,turb_list[x])
        row += 1

wb.close()

print("hurra")
