import MySQLdb
import dbTransmit
import random

valid = "y"

filename_temp = "/var/www/FlaskApp/FlaskApp/static/realtimedata/realtime_temp.csv"
filename_ph = "/var/www/FlaskApp/FlaskApp/static/realtimedata/realtime_ph.csv"
filename_turb = "/var/www/FlaskApp/FlaskApp/static/realtimedata/realtime_turb.csv"
filename_kond = "/var/www/FlaskApp/FlaskApp/static/realtimedata/realtime_kond.csv"
m_pr_h = 1

print("Legger inn tilfeldig genererte verdier ...")
for month in range(1,13):

    month = str(month)
    if int(month) < 10:
        month_f = "0"+month
    else:
        month_f = month

    for day in range(1,28):
        day = str(day)
        if int(day) < 10:
            day_f = "0"+day
        else:
            day_f = day

        for hour in range(24):
            hour = str(hour)
            if int(hour)< 10:
                hour_f = "0"+hour
            else:
                hour_f = hour

            ph = random.uniform(0.0, 14.0)
            temp = random.uniform(0.0, 20.0)
            kond = random.uniform(0.0, 20.0)
            turb = random.uniform(0.0, 20.0)


            dato = "2019" + "-" + month_f + "-" + day_f
            tid = hour_f + ":" + "00"

            dbTransmit.updateCSV(filename_temp,tid,temp,m_pr_h)
            dbTransmit.updateCSV(filename_kond,tid,kond,m_pr_h)
            dbTransmit.updateCSV(filename_turb,tid,turb,m_pr_h)
            dbTransmit.updateCSV(filename_ph,tid,ph,m_pr_h)

            dbTransmit.submitForFilling(temp, ph, turb, kond, dato, tid, valid, "Vikelva")
    sql = month + "/12 av data lagt inn ..."
    print(sql)

print("Tilfeldige data lagt inn i Vikelva")
print("")
print("Genererer gjennomsnittverdier ... ")
print("")
conn = MySQLdb.connect("localhost","jakob","","Vikelva")
list = ["apr_19","aug_19","des_19","feb_19","jan_19","jul_19","jun_19","mai_19","mar_19","nov_19","okt_19","sep_19"]

for m in range(len(list)):
    s = list[m]
    dbTransmit.updateAvgTable(conn,s)
    if m == 0:
        print("")

    sql = str(m+1) + "/12 av gjennomsnittsverdier lagt inn ..."
    print(sql)

print("Gjennonsmittsverdier lagt inn med suksess")
