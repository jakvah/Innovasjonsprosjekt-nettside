
import MySQLdb
import dbTransmit
from datetime import date
import os, time

filename = "/var/www/FlaskApp/FlaskApp/static/excelfiles/Datapunkter_2019-04-23.xlsx"

def file_age(filepath):
    return time.time() - os.path.getmtime(filepath)

seconds = file_age(filename)
print(seconds)
#print(os.path.getmtime(filename))

