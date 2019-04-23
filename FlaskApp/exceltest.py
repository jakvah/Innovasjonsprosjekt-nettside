
import xlsxwriter
import dbTransmit

data = dbTransmit.getDateData("2019-01-01","Vikelva")
print(data)
dbTransmit.createExcel(data,"/var/www/FlaskApp/FlaskApp/static/excelfiles/test.xlsx")

print("yay")

