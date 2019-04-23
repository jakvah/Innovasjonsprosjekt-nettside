import MySQLdb
import dbTransmit

# rivername = str(input("Specify rivername: "))
try:
    conn = MySQLdb.connect("localhost", "jakob","", "Vikelva")
    c = conn.cursor()

    c.execute("drop database Vikelva")
    conn.commit()
    c.execute("create database Vikelva")
    c.close()
    print("Vikelva has been cleared!")

    filename_temp = "/var/www/FlaskApp/FlaskApp/static/realtimedata/realtime_temp.csv"
    filename_ph = "/var/www/FlaskApp/FlaskApp/static/realtimedata/realtime_ph.csv"
    filename_turb = "/var/www/FlaskApp/FlaskApp/static/realtimedata/realtime_turb.csv"
    filename_kond = "/var/www/FlaskApp/FlaskApp/static/realtimedata/realtime_kond.csv"

    dbTransmit.clearCSV(filename_temp)
    dbTransmit.clearCSV(filename_ph)
    dbTransmit.clearCSV(filename_turb)
    dbTransmit.clearCSV(filename_kond)

    print("Realtime CSV files has been cleard!")
except Exception as e:
    print (str(e))
