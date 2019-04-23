# Nettside backend for elsysprosjekt.
"""Bruk kun A-Z i kommentarer og kode!!!"""
# -*- coding: utf-8 -*-

from flask import Flask, render_template, redirect, request, url_for, send_file

import MySQLdb
import dbTransmit
import os
import json
import datetime
import xlsxwriter

app = Flask(__name__)
@app.route("/tid")
# Landing page legges her. Skal kanskje kordineres med resten av gruppene
def index():
    try:
        n = datetime.datetime.now()
        return str(n)
    except Exception as e:
        return str(e)

@app.route("/om")
def about():
    return render_template("about.html")


@app.route("/email")
def email():
    return render_template("epost.html")

@app.route("/andrea")
def andrea():
    try:
        return render_template('kontakt.html')
    except Exception as e:
        return str(e)

@app.route("/hisdat",methods = ["POST","GET"])
def hisdat(chart1ID = 'chart1_ID', chart1_type = 'line', chart1_height = 400,
          chart2ID = 'chart2_ID',chart2_type = 'line', chart2_height = 400,
          chartID_turb = "chart_turb_ID",chart_turb_type = "line",chart_turb_height = 400,
          chartID_kond = "chart_kond_ID", chart_kond_type = "line", chart_kond_height = 400):
    try:
        if request.method == "GET":
            dato_checked = ""
            periode_checked = "checked"
            month_checked = ""
            datastatus = False

            return render_template("hisdat.html",dato_checked = dato_checked, periode_checked = periode_checked,month_checked = month_checked,datastatus = datastatus)


        elif request.method == "POST":
            start = request.form["start"]
            slutt = request.form["slutt"]
            knapp = request.form["featured"]
            liten_periode = False

            # Slik at knappen forblir det den er valgt
            if knapp == "dato":
                dato_checked = "checked"
                periode_checked = ""
                month_checked = ""
                if start == "":
                    return render_template("hisdat.html", dato_checked=dato_checked, periode_checked=periode_checked,
                                           month_checked=month_checked, datastatus=False,error_msg = "Velg en dato!",empty = True)
            elif knapp == "periode":
                dato_checked = ""
                periode_checked = "checked"
                month_checked = ""
                if start == "" or slutt == "":
                    return render_template("hisdat.html", dato_checked=dato_checked, periode_checked=periode_checked,
                                           month_checked=month_checked, datastatus=False, error_msg="Velg en dato!",empty = True)
            elif knapp == "mnd":
                dato_checked = ""
                periode_checked = ""
                month_checked = "checked"
                try:
                    month = request.form['month']
                    year = request.form['year']
                except Exception as e:
                    return render_template("hisdat.html", dato_checked=dato_checked, periode_checked=periode_checked,
                                           month_checked=month_checked, datastatus=False, error_msg="Velg en gyldig mned!",empty = True)

            # Henter korrekte data
            if knapp == "dato":
                date = start
                dbconn = MySQLdb.connect("localhost","jakob","","Vikelva")
                if not dbTransmit.tableExists(dbconn,dbTransmit.createTableName(date)):
                    dbconn.close()
                    return render_template("hisdat.html", dato_checked=dato_checked, periode_checked=periode_checked,
                                           month_checked=month_checked, datastatus=False, error_msg="Har ingen data for denne dagen!",empty=True)
                dbconn.close()

                dataset = dbTransmit.getDateData(date,"Vikelva")
                dato = dbTransmit.displayDateFully(date)
                data_header_sql = "Data for " + str(dato)
                graph_label = str(dato)
                table_header = "Data for " + str(dato) + " i tabellform "
                accordion_header = "Oppsummering for "  + str(dato)
                excel_filename = "/var/www/FlaskApp/FlaskApp/static/excelfiles/Datapunkter_" + str(start)+".xlsx"


                datastatus = True
                month_or_period = False
                col_one_name = "Klokkeslett"
                overviewURL = ""
                overviewDATE = ""

                # Setter opp grafer
                kond_list = []
                turb_list = []
                temp_list = []
                ph_list = []
                time_list = []

                for rad in dataset:
                    time_list.append(str(rad[2]))
                    ph_list.append(float(rad[3]))
                    temp_list.append(float(rad[4]))
                    turb_list.append(float(rad[5]))
                    kond_list.append(float(rad[6]))

                chart_kond = {"renderTo": chartID_kond, "type": chart_kond_type, "height": chart_kond_height,
                              "backgroundColor": 'transparent'}
                series_kond = [{"name": graph_label, "data": kond_list}, ]
                title_kond = {"text": 'TDS utvikling i  Vikelva', "style": {"color": "black"}}
                xAxis_kond = {"categories": time_list, "labels": {"style": {"color": 'black'}}}
                yAxis_kond = {"title": {"text": 'Konduktivitet', "style": {"color": 'black'}},
                              "labels": {"style": {"color": 'black'}}}

                chart_turb = {"renderTo": chartID_turb, "type": chart_turb_type, "height": chart_turb_height,
                              "backgroundColor": 'transparent'}
                series_turb = [{"name": graph_label, "data": turb_list}, ]
                title_turb = {"text": 'Turbiditetsutvikling i  Vikelva', "style": {"color": "black"}}
                xAxis_turb = {"categories": time_list, "labels": {"style": {"color": 'black'}}}
                yAxis_turb = {"title": {"text": 'Turbditet', "style": {"color": 'black'}},
                              "labels": {"style": {"color": 'black'}}}

                chart1 = {"renderTo": chart1ID, "type": chart1_type, "height": chart1_height,
                          "backgroundColor": 'transparent'}
                series1 = [{"name": graph_label, "data": temp_list}, ]
                title1 = {"text": 'Temperaturutvikling Vikelva', "style": {"color": "black"}}
                xAxis1 = {"categories": time_list, "labels": {"style": {"color": 'black'}}}
                yAxis1 = {"title": {"text": 'Grader Celsius', "style": {"color": 'black'}},
                          "labels": {"style": {"color": 'black'}}}

                chart2 = {"renderTo": chart2ID, "type": chart2_type, "height": chart2_height,
                          "backgroundColor": 'transparent'}
                series2 = [{"name": graph_label, "data": ph_list}, ]
                title2 = {"text": 'pH utvikling Vikelva', "style": {"color": "black"}}
                xAxis2 = {"categories": time_list, "labels": {"style": {"color": 'black'}}}
                yAxis2 = {"title": {"text": 'pH', "style": {"color": 'black'}}, "labels": {"style": {"color": 'black'}}}

            elif knapp == "mnd":
                month = request.form['month']
                year = request.form['year']

                month_fin = dbTransmit.shortToLongMonth(month)
                year_fin = "20" + year

                dbconn = MySQLdb.connect("localhost","jakob","","Vikelva")
                if not dbTransmit.tableExists(dbconn,(month_fin[:3]+"_"+str(year))):
                    dbconn.close()
                    return render_template("hisdat.html", dato_checked=dato_checked, periode_checked=periode_checked,
                                           month_checked=month_checked, datastatus=False,
                                           error_msg="Har ingen data for denne perioden!", empty=True)
                dbconn.close()
                datastatus = True
                month_or_period = True
                col_one_name = "Dato"

                data_header_sql = "Data for " + month_fin + ", " + year_fin
                graph_label = "Gjennomsnitt for " + str(dbTransmit.shortToLongMonth(month)) + " " + "20" + str(year)
                table_header = "Gjennomsnittlige data for " + str(dbTransmit.shortToLongMonth(month)) + " " + "20" + str(year) + " i tabellform"
                accordion_header = "Oppsummering for " + str(dbTransmit.shortToLongMonth(month)) + " " + "20" + str(year)
                excel_filename = "/var/www/FlaskApp/FlaskApp/static/excelfiles/Datapunkter_" + str(dbTransmit.shortToLongMonth(month)) + " " + "20" + str(year)+".xlsx"

                dataset = dbTransmit.getTupleDB(month,year)
                overviewURL = dbTransmit.convertToURL(dataset)
                overviewDATE = dbTransmit.convertToDisplayDate(dataset)

                # Setter opp grafer
                kond_list = []
                turb_list = []
                temp_list = []
                ph_list = []
                time_list = []

                for rad in dataset:
                    time_list.append(float(rad[1][8:10]))
                    ph_list.append(float(rad[2]))
                    temp_list.append(float(rad[3]))
                    turb_list.append(float(rad[4]))
                    kond_list.append(float(rad[5]))

                chart_kond = {"renderTo": chartID_kond, "type": chart_kond_type, "height": chart_kond_height,
                              "backgroundColor": 'transparent'}
                series_kond = [{"name": graph_label, "data": kond_list}, ]
                title_kond = {"text": 'TDS utvikling i  Vikelva', "style": {"color": "black"}}
                xAxis_kond = {"categories": time_list, "labels": {"style": {"color": 'black'}}}
                yAxis_kond = {"title": {"text": 'Konduktivitet', "style": {"color": 'black'}},
                              "labels": {"style": {"color": 'black'}}}

                chart_turb = {"renderTo": chartID_turb, "type": chart_turb_type, "height": chart_turb_height,
                              "backgroundColor": 'transparent'}
                series_turb = [{"name": graph_label, "data": turb_list}, ]
                title_turb = {"text": 'Turbiditetsutvikling i  Vikelva', "style": {"color": "black"}}
                xAxis_turb = {"categories": time_list, "labels": {"style": {"color": 'black'}}}
                yAxis_turb = {"title": {"text": 'Turbditet', "style": {"color": 'black'}},
                              "labels": {"style": {"color": 'black'}}}

                chart1 = {"renderTo": chart1ID, "type": chart1_type, "height": chart1_height,
                          "backgroundColor": 'transparent'}
                series1 = [{"name": graph_label, "data": temp_list}, ]
                title1 = {"text": 'Temperaturutvikling Vikelva', "style": {"color": "black"}}
                xAxis1 = {"categories": time_list, "labels": {"style": {"color": 'black'}}}
                yAxis1 = {"title": {"text": 'Grader Celsius', "style": {"color": 'black'}},
                          "labels": {"style": {"color": 'black'}}}

                chart2 = {"renderTo": chart2ID, "type": chart2_type, "height": chart2_height,
                          "backgroundColor": 'transparent'}
                series2 = [{"name": graph_label, "data": ph_list}, ]
                title2 = {"text": 'pH utvikling Vikelva', "style": {"color": "black"}}
                xAxis2 = {"categories": time_list, "labels": {"style": {"color": 'black'}}}
                yAxis2 = {"title": {"text": 'pH', "style": {"color": 'black'}}, "labels": {"style": {"color": 'black'}}}

            elif knapp == "periode":
                TERSKEL = 3 # Terskel for vise gjn
                if not dbTransmit.isPeriodeValid(start,slutt):
                    return render_template("hisdat.html", dato_checked=dato_checked, periode_checked=periode_checked,
                                           month_checked=month_checked, datastatus=False,error_msg="Ugyldig periode!",empty = True)
                dbconn = MySQLdb.connect("localhost","jakob","","Vikelva")
                if not dbTransmit.tableExists(dbconn,dbTransmit.createTableName(start)) or not dbTransmit.tableExists(dbconn,dbTransmit.createTableName(slutt)):
                    dbconn.close()
                    return render_template("hisdat.html", dato_checked=dato_checked, periode_checked=periode_checked,
                                       month_checked=month_checked, datastatus=False, error_msg="Har ikke data for denne perioden!",
                                       empty=True)
                dbconn.close()

                # Bare en dag
                if dbTransmit.datesAlike(start,slutt):
                    date = start
                    dataset = dbTransmit.getDateData(date, "Vikelva")
                    dato = dbTransmit.displayDateFully(date)
                    data_header_sql = "Data for " + str(dato)
                    graph_label = str(dato)
                    table_header = "Data for " + str(dato) + " i tabellform"
                    accordion_header = "Oppsummering for " + str(dato)
                    excel_filename = "/var/www/FlaskApp/FlaskApp/static/excelfiles/Datapunkter_" + str(start)+".xlsx"

                    datastatus = True
                    month_or_period = False
                    col_one_name = "Klokkeslett"
                    overviewURL = ""
                    overviewDATE = ""

                    # Setter opp grafer
                    kond_list = []
                    turb_list = []
                    temp_list = []
                    ph_list = []
                    time_list = []

                    for rad in dataset:
                        time_list.append(str(rad[2]))
                        ph_list.append(float(rad[3]))
                        temp_list.append(float(rad[4]))
                        turb_list.append(float(rad[5]))
                        kond_list.append(float(rad[6]))

                    chart_kond = {"renderTo": chartID_kond, "type": chart_kond_type, "height": chart_kond_height,
                                  "backgroundColor": 'transparent'}
                    series_kond = [{"name": graph_label, "data": kond_list}, ]
                    title_kond = {"text": 'TDS utvikling i  Vikelva', "style": {"color": "black"}}
                    xAxis_kond = {"categories": time_list, "labels": {"style": {"color": 'black'}}}
                    yAxis_kond = {"title": {"text": 'Konduktivitet', "style": {"color": 'black'}},
                                  "labels": {"style": {"color": 'black'}}}

                    chart_turb = {"renderTo": chartID_turb, "type": chart_turb_type, "height": chart_turb_height,
                                  "backgroundColor": 'transparent'}
                    series_turb = [{"name": graph_label, "data": turb_list}, ]
                    title_turb = {"text": 'Turbiditetsutvikling i  Vikelva', "style": {"color": "black"}}
                    xAxis_turb = {"categories": time_list, "labels": {"style": {"color": 'black'}}}
                    yAxis_turb = {"title": {"text": 'Turbditet', "style": {"color": 'black'}},
                                  "labels": {"style": {"color": 'black'}}}

                    chart1 = {"renderTo": chart1ID, "type": chart1_type, "height": chart1_height,
                              "backgroundColor": 'transparent'}
                    series1 = [{"name": graph_label, "data": temp_list}, ]
                    title1 = {"text": 'Temperaturutvikling Vikelva', "style": {"color": "black"}}
                    xAxis1 = {"categories": time_list, "labels": {"style": {"color": 'black'}}}
                    yAxis1 = {"title": {"text": 'Grader Celsius', "style": {"color": 'black'}},
                              "labels": {"style": {"color": 'black'}}}

                    chart2 = {"renderTo": chart2ID, "type": chart2_type, "height": chart2_height,
                              "backgroundColor": 'transparent'}
                    series2 = [{"name": graph_label, "data": ph_list}, ]
                    title2 = {"text": 'pH utvikling Vikelva', "style": {"color": "black"}}
                    xAxis2 = {"categories": time_list, "labels": {"style": {"color": 'black'}}}
                    yAxis2 = {"title": {"text": 'pH', "style": {"color": 'black'}},
                              "labels": {"style": {"color": 'black'}}}
                else:
                    if dbTransmit.getDateDifference(start,slutt) <= TERSKEL:
                        date = start
                        dataset = dbTransmit.getPeriodData(start,slutt,TERSKEL)
                        dato1 = dbTransmit.displayDateFully(date)
                        dato2 = dbTransmit.displayDateFully(slutt)
                        data_header_sql = "Data for perioden " + str(dato1) + " - " + str(dato2)
                        table_header = "Data for perioden " + str(dato1) + " - " + str(dato2) + " i tabellform"
                        graph_label = str(dato1) + " - " + str(dato2)
                        accordion_header = "Oppsummering av perioden " + str(dato1) + " - " + str(dato2)
                        excel_filename = "/var/www/FlaskApp/FlaskApp/static/excelfiles/Datapunkt_perioden_" + str(start) + "_" + str(slutt)+".xlsx"


                        # Fin dato til tabell
                        for x in range(len(dataset)):
                            date = dataset[x][1]
                            findate = dbTransmit.displayDateNoYear(date)
                            dataset[x][1] = findate

                        datastatus = True
                        month_or_period = False
                        liten_periode = True
                        col_one_name = "Klokkeslett"
                        overviewURL = ""
                        overviewDATE = ""

                        # Setter opp grafer
                        kond_list = []
                        turb_list = []
                        temp_list = []
                        ph_list = []
                        time_list = []

                        for rad in dataset:
                            findato = rad[1]
                            sql = findato + " " + str(rad[2])
                            time_list.append(sql)
                            #time_list.append(str(rad[2]))
                            ph_list.append(float(rad[3]))
                            temp_list.append(float(rad[4]))
                            turb_list.append(float(rad[5]))
                            kond_list.append(float(rad[6]))

                        tickInterval = len(dataset) / 6

                        chart_kond = {"renderTo": chartID_kond, "type": chart_kond_type, "height": chart_kond_height,
                                      "backgroundColor": 'transparent'}
                        series_kond = [{"name": graph_label, "data": kond_list}, ]
                        title_kond = {"text": 'TDS utvikling i  Vikelva', "style": {"color": "black"}}
                        xAxis_kond = {"tickInterval":tickInterval,"categories": time_list, "labels": {"style": {"color": 'black'}}}
                        yAxis_kond = {"title": {"text": 'Konduktivitet', "style": {"color": 'black'}},
                                      "labels": {"style": {"color": 'black'}}}

                        chart_turb = {"renderTo": chartID_turb, "type": chart_turb_type, "height": chart_turb_height,
                                      "backgroundColor": 'transparent'}
                        series_turb = [{"name": graph_label, "data": turb_list}, ]
                        title_turb = {"text": 'Turbiditetsutvikling i  Vikelva', "style": {"color": "black"}}
                        xAxis_turb = {"tickInterval":tickInterval,"categories": time_list, "labels": {"style": {"color": 'black'}}}
                        yAxis_turb = {"title": {"text": 'Turbditet', "style": {"color": 'black'}},
                                      "labels": {"style": {"color": 'black'}}}

                        chart1 = {"renderTo": chart1ID, "type": chart1_type, "height": chart1_height,
                                  "backgroundColor": 'transparent'}
                        series1 = [{"name": graph_label, "data": temp_list}, ]
                        title1 = {"text": 'Temperaturutvikling Vikelva', "style": {"color": "black"}}
                        xAxis1 = {"tickInterval":tickInterval,"categories": time_list, "labels": {"style": {"color": 'black'}}}
                        yAxis1 = {"title": {"text": 'Grader Celsius', "style": {"color": 'black'}},
                                  "labels": {"style": {"color": 'black'}}}

                        chart2 = {"renderTo": chart2ID, "type": chart2_type, "height": chart2_height,
                                  "backgroundColor": 'transparent'}
                        series2 = [{"name": graph_label, "data": ph_list}, ]
                        title2 = {"text": 'pH utvikling Vikelva', "style": {"color": "black"}}
                        xAxis2 = {"tickInterval":tickInterval,"categories": time_list, "labels": {"style": {"color": 'black'}}}
                        yAxis2 = {"title": {"text": 'pH', "style": {"color": 'black'}},
                                  "labels": {"style": {"color": 'black'}}}

                    else: # over terskel
                        datastatus = True
                        month_or_period = True
                        col_one_name = "Dato"


                        data_header_sql = "Data for perioden " + dbTransmit.displayDateFully(start) + " - " + dbTransmit.displayDateFully(slutt)
                        graph_label = "Gjennomsnitt for perioden " + str(dbTransmit.displayDateFully(start)) + " - " + str(dbTransmit.displayDateFully(slutt))
                        table_header = "Data for perioden " + dbTransmit.displayDateFully(start) + " - " + dbTransmit.displayDateFully(slutt) + " i tabellform"
                        accordion_header = "Oppsummering for perioden " + dbTransmit.displayDateFully(start) + " - " + dbTransmit.displayDateFully(slutt)
                        excel_filename = "/var/www/FlaskApp/FlaskApp/static/excelfiles/Datapunkt_perioden_" + str(start) + "_" + str(slutt)+".xlsx"


                        dataset = dbTransmit.getPeriodData(start,slutt,TERSKEL)
                        for x in range(len(dataset)):
                            dataset[x] = tuple(dataset[x])

                        overviewURL = dbTransmit.convertToURL(dataset)
                        overviewDATE = dbTransmit.convertToDisplayDate(dataset)

                        # Setter opp grafer
                        kond_list = []
                        turb_list = []
                        temp_list = []
                        ph_list = []
                        time_list = []

                        for rad in dataset:
                            dato = rad[1]
                            datofin = dbTransmit.displayDateFully(dato)
                            time_list.append(datofin)
                            #time_list.append(float(rad[1][8:10]))
                            ph_list.append(float(rad[2]))
                            temp_list.append(float(rad[3]))
                            turb_list.append(float(rad[4]))
                            kond_list.append(float(rad[5]))


                        tickInterval = len(time_list) / 6
                        chart_kond = {"renderTo": chartID_kond, "type": chart_kond_type, "height": chart_kond_height,
                                      "backgroundColor": 'transparent'}
                        series_kond = [{"name": graph_label, "data": kond_list}, ]
                        title_kond = {"text": 'TDS utvikling i  Vikelva', "style": {"color": "black"}}
                        xAxis_kond = {"tickInterval":tickInterval,"categories": time_list, "labels": {"style": {"color": 'black'}}}
                        yAxis_kond = {"title": {"text": 'Konduktivitet', "style": {"color": 'black'}},
                                      "labels": {"style": {"color": 'black'}}}

                        chart_turb = {"renderTo": chartID_turb, "type": chart_turb_type, "height": chart_turb_height,
                                      "backgroundColor": 'transparent'}
                        series_turb = [{"name": graph_label, "data": turb_list}, ]
                        title_turb = {"text": 'Turbiditetsutvikling i  Vikelva', "style": {"color": "black"}}
                        xAxis_turb = {"tickInterval":tickInterval,"categories": time_list, "labels": {"style": {"color": 'black'}}}
                        yAxis_turb = {"title": {"text": 'Turbditet', "style": {"color": 'black'}},
                                      "labels": {"style": {"color": 'black'}}}

                        chart1 = {"renderTo": chart1ID, "type": chart1_type, "height": chart1_height,
                                  "backgroundColor": 'transparent'}
                        series1 = [{"name": graph_label, "data": temp_list}, ]
                        title1 = {"text": 'Temperaturutvikling Vikelva', "style": {"color": "black"}}
                        xAxis1 = {"tickInterval":tickInterval,"categories": time_list, "labels": {"style": {"color": 'black'}}}
                        yAxis1 = {"title": {"text": 'Grader Celsius', "style": {"color": 'black'}},
                                  "labels": {"style": {"color": 'black'}}}

                        chart2 = {"renderTo": chart2ID, "type": chart2_type, "height": chart2_height,
                                  "backgroundColor": 'transparent'}
                        series2 = [{"name": graph_label, "data": ph_list}, ]
                        title2 = {"text": 'pH utvikling Vikelva', "style": {"color": "black"}}
                        xAxis2 = {"tickInterval":tickInterval,"categories": time_list, "labels": {"style": {"color": 'black'}}}
                        yAxis2 = {"title": {"text": 'pH', "style": {"color": 'black'}},
                                  "labels": {"style": {"color": 'black'}}}


        # Lager excelfil
        try:
            for filename in os.listdir("/var/www/FlaskApp/FlaskApp/static/excelfiles"):
                if filename.endswith(".xlsx") and (dbTransmit.file_age("/var/www/FlaskApp/FlaskApp/static/excelfiles/" + filename) >= 86400 ):
                    dbTransmit.removeFile("/var/www/FlaskApp/FlaskApp/static/excelfiles/"+filename)

            if month_or_period:
                dbTransmit.createExcel(dataset,excel_filename,"m")
            else:
                dbTransmit.createExcel(dataset,excel_filename,"p")

            download_url = "https://gr5.vannovervakning.com/"+excel_filename[27:]
        except Exception as e:
            return str(e)

        if month_or_period:
            type = "avg"
        else:
            type = "notavg"


        # Henter max
        max_ph_indexes = dbTransmit.getMaxIndex(dataset,"ph",type)
        max_temp_indexes = dbTransmit.getMaxIndex(dataset,"temp",type)
        max_turb_indexes = dbTransmit.getMaxIndex(dataset,"turb",type)
        max_kond_indexes = dbTransmit.getMaxIndex(dataset,"kond",type)

        # Henter bare den forste atm
        max_kond_indexes = max_kond_indexes[0]
        max_turb_indexes = max_turb_indexes[0]
        max_temp_indexes = max_temp_indexes[0]
        max_ph_indexes = max_ph_indexes[0]


        max_ph_value = dbTransmit.getValue(dataset,"ph",type,max_ph_indexes)
        max_temp_value = dbTransmit.getValue(dataset,"temp",type,max_temp_indexes)
        max_turb_value = dbTransmit.getValue(dataset,"turb",type,max_turb_indexes)
        max_kond_value = dbTransmit.getValue(dataset,"kond",type,max_kond_indexes)


        if not month_or_period and not liten_periode:
            max_ph_date = dataset[max_ph_indexes][2]
            max_temp_date = dataset[max_temp_indexes][2]
            max_turb_date = dataset[max_turb_indexes][2]
            max_kond_date = dataset[max_kond_indexes][2]

        elif not liten_periode:
            max_ph_date = dbTransmit.displayDateNoYear(dataset[max_ph_indexes][1])
            max_temp_date = dbTransmit.displayDateNoYear(dataset[max_temp_indexes][1])
            max_turb_date = dbTransmit.displayDateNoYear(dataset[max_turb_indexes][1])
            max_kond_date = dbTransmit.displayDateNoYear(dataset[max_kond_indexes][1])

        elif liten_periode:
            max_ph_date = dataset[max_ph_indexes][1]
            max_temp_date = dataset[max_temp_indexes][1]
            max_turb_date = dataset[max_turb_indexes][1]
            max_kond_date = dataset[max_kond_indexes][1]


        #Henter min
        min_ph_indexes = dbTransmit.getMinIndex(dataset,"ph",type)
        min_temp_indexes = dbTransmit.getMinIndex(dataset,"temp",type)
        min_kond_indexes = dbTransmit.getMinIndex(dataset,"kond",type)
        min_turb_indexes = dbTransmit.getMinIndex(dataset,"turb",type)
        # Henter bare forst atm
        min_ph_index = min_ph_indexes[0]
        min_temp_index = min_temp_indexes[0]
        min_kond_index = min_kond_indexes[0]
        min_turb_index = min_turb_indexes[0]

        min_ph_value = dbTransmit.getValue(dataset,"ph",type,min_ph_index)
        min_temp_value = dbTransmit.getValue(dataset,"temp",type,min_temp_index)
        min_kond_value = dbTransmit.getValue(dataset,"kond",type,min_kond_index)
        min_turb_value = dbTransmit.getValue(dataset,"turb",type,min_turb_index)

        if not month_or_period and not liten_periode:
            min_ph_date = dataset[min_ph_index][2]
            min_temp_date = dataset[min_temp_index][2]
            min_turb_date = dataset[min_turb_index][2]
            min_kond_date = dataset[min_kond_index][2]

        elif not liten_periode:
            min_ph_date = dbTransmit.displayDateNoYear(dataset[min_ph_index][1])
            min_temp_date = dbTransmit.displayDateNoYear(dataset[min_temp_index][1])
            min_kond_date = dbTransmit.displayDateNoYear(dataset[min_kond_index][1])
            min_turb_date = dbTransmit.displayDateNoYear(dataset[min_turb_index][1])

        elif liten_periode:
            min_ph_date = dataset[min_ph_index][1]
            min_temp_date = dataset[min_temp_index][1]
            min_kond_date = dataset[min_kond_index][1]
            min_turb_date = dataset[min_turb_index][1]

        diff_ph_value = max_ph_value - min_ph_value
        diff_temp_value = max_temp_value - min_temp_value
        diff_kond_value = max_kond_value - min_kond_value
        diff_turb_value = max_turb_value - min_turb_value

        PHVARSEL = 15
        TEMPVARSEL = 10.0
        TURBVARSEL = 10.0
        KONDVARSEL = 10.0

        if diff_ph_value >= PHVARSEL:
            ph_kritisk = True
            ph_status = "Kritisk!"
        else:
            ph_kritisk = False
            ph_status = "Ikke kritisk"
        if diff_temp_value >=TEMPVARSEL:
            temp_kritisk = True
            temp_status = "Kritisk!"
        else:
            temp_kritisk = False
            temp_status ="Ikke kritisk"
        if diff_kond_value >= KONDVARSEL:
            kond_kritisk = True
            kond_status = "Kritisk!"
        else:
            kond_kritisk = False
            kond_status = "Ikke kritisk"
        if diff_turb_value >= TURBVARSEL:
            turb_kritisk = True
            turb_status = "Kritisk!"
        else:
            turb_kritisk = False
            turb_status = "Ikke kritisk"

        return render_template("hisdat.html",col_one_name = col_one_name, datastatus = datastatus, dato_checked = dato_checked, periode_checked = periode_checked, month_checked = month_checked,
                               dataset = dataset, data_header_sql = data_header_sql, table_header = table_header, accordion_header = accordion_header,download_url = download_url,
                               overviewDATE = overviewDATE, overviewURL = overviewURL, month_or_period = month_or_period, liten_periode = liten_periode,
                               max_ph_value = max_ph_value, max_temp_value = max_temp_value, max_turb_value = max_turb_value,max_kond_value = max_kond_value,
                               max_ph_date = max_ph_date, max_kond_date = max_kond_date, max_turb_date = max_turb_date,max_temp_date = max_temp_date,
                               min_ph_value = min_ph_value, min_temp_value = min_temp_value, min_kond_value = min_kond_value, min_turb_value = min_turb_value,
                               min_ph_date = min_ph_date, min_temp_date = min_temp_date, min_kond_date= min_kond_date, min_turb_date = min_turb_date,
                               diff_ph_value = diff_ph_value, diff_temp_value = diff_temp_value, diff_kond_value = diff_kond_value, diff_turb_value = diff_turb_value,
                               ph_kritisk = ph_kritisk, temp_kritisk = temp_kritisk, kond_kritisk = kond_kritisk, turb_kritisk = turb_kritisk,
                               ph_status = ph_status, temp_status = temp_status, kond_status = kond_status, turb_status = turb_status,
                               chart1ID=chart1ID, chart1=chart1, series1=series1, title1=title1, xAxis1=xAxis1, yAxis1=yAxis1,
                               chart2ID=chart2ID, chart2=chart2, series2=series2, title2=title2, xAxis2=xAxis2, yAxis2=yAxis2,
                               chartID_turb=chartID_turb, chart_turb=chart_turb, series_turb=series_turb,
                               title_turb=title_turb, xAxis_turb=xAxis_turb, yAxis_turb=yAxis_turb,
                               chartID_kond=chartID_kond, chart_kond=chart_kond, series_kond=series_kond,
                               title_kond=title_kond, xAxis_kond=xAxis_kond, yAxis_kond=yAxis_kond)

    except Exception as e:
        return str(e)

@app.route("/hisdat/date/<date>")
def datepage(date,
             chart1ID='chart1_ID', chart1_type='line', chart1_height=400,
             chart2ID='chart2_ID', chart2_type='line', chart2_height=400,
             chartID_turb="chart_turb_ID", chart_turb_type="line", chart_turb_height=400,
             chartID_kond="chart_kond_ID", chart_kond_type="line", chart_kond_height=400
             ):
    try:
        dato_checked = ""
        periode_checked = ""
        month_checked = "checked"

        dataset = dbTransmit.getDateData(date, "Vikelva")
        dato = dbTransmit.displayDateFully(date)
        data_header_sql = "Data for " + str(dato)
        graph_label = str(dato)
        table_header = "Data for " + str(dato) + " i tabellform"
        accordion_header = "Oppsummering for " + str(dato)
        excel_filename = "/var/www/FlaskApp/FlaskApp/static/excelfiles/Datapunkter_" + str(date) + ".xlsx"

        datastatus = True
        month_or_period = False
        col_one_name = "Klokkeslett"
        overviewURL = ""
        overviewDATE = ""

        # Setter opp grafer
        kond_list = []
        turb_list = []
        temp_list = []
        ph_list = []
        time_list = []

        for rad in dataset:
            time_list.append(str(rad[2]))
            ph_list.append(float(rad[3]))
            temp_list.append(float(rad[4]))
            turb_list.append(float(rad[5]))
            kond_list.append(float(rad[6]))

        chart_kond = {"renderTo": chartID_kond, "type": chart_kond_type, "height": chart_kond_height,
                      "backgroundColor": 'transparent'}
        series_kond = [{"name": graph_label, "data": kond_list}, ]
        title_kond = {"text": 'TDS utvikling i  Vikelva', "style": {"color": "black"}}
        xAxis_kond = {"categories": time_list, "labels": {"style": {"color": 'black'}}}
        yAxis_kond = {"title": {"text": 'Konduktivitet', "style": {"color": 'black'}},
                      "labels": {"style": {"color": 'black'}}}

        chart_turb = {"renderTo": chartID_turb, "type": chart_turb_type, "height": chart_turb_height,
                      "backgroundColor": 'transparent'}
        series_turb = [{"name": graph_label, "data": turb_list}, ]
        title_turb = {"text": 'Turbiditetsutvikling i  Vikelva', "style": {"color": "black"}}
        xAxis_turb = {"categories": time_list, "labels": {"style": {"color": 'black'}}}
        yAxis_turb = {"title": {"text": 'Turbditet', "style": {"color": 'black'}},
                      "labels": {"style": {"color": 'black'}}}

        chart1 = {"renderTo": chart1ID, "type": chart1_type, "height": chart1_height,
                  "backgroundColor": 'transparent'}
        series1 = [{"name": graph_label, "data": temp_list}, ]
        title1 = {"text": 'Temperaturutvikling Vikelva', "style": {"color": "black"}}
        xAxis1 = {"categories": time_list, "labels": {"style": {"color": 'black'}}}
        yAxis1 = {"title": {"text": 'Grader Celsius', "style": {"color": 'black'}},
                  "labels": {"style": {"color": 'black'}}}

        chart2 = {"renderTo": chart2ID, "type": chart2_type, "height": chart2_height,
                  "backgroundColor": 'transparent'}
        series2 = [{"name": graph_label, "data": ph_list}, ]
        title2 = {"text": 'pH utvikling Vikelva', "style": {"color": "black"}}
        xAxis2 = {"categories": time_list, "labels": {"style": {"color": 'black'}}}
        yAxis2 = {"title": {"text": 'pH', "style": {"color": 'black'}}, "labels": {"style": {"color": 'black'}}}

        # Lager excelfil
        try:
            for filename in os.listdir("/var/www/FlaskApp/FlaskApp/static/excelfiles"):
                if filename.endswith(".xlsx"):
                    dbTransmit.removeFile("/var/www/FlaskApp/FlaskApp/static/excelfiles/" + filename)

            if month_or_period:
                dbTransmit.createExcel(dataset, excel_filename, "m")
            else:
                dbTransmit.createExcel(dataset, excel_filename, "p")

            download_url = "https://gr5.vannovervakning.com/" + excel_filename[27:]
        except Exception as e:
            return str(e)

        return render_template("hisdat.html", col_one_name=col_one_name, datastatus=datastatus, dato_checked=dato_checked,
                               periode_checked=periode_checked, month_checked=month_checked, dataset=dataset,
                               data_header_sql=data_header_sql, table_header = table_header, accordion_header = accordion_header,
                               overviewDATE=overviewDATE, overviewURL=overviewURL, month_or_period=month_or_period, download_url = download_url,
                               chart1ID=chart1ID, chart1=chart1, series1=series1, title1=title1, xAxis1=xAxis1,
                               yAxis1=yAxis1,
                               chart2ID=chart2ID, chart2=chart2, series2=series2, title2=title2, xAxis2=xAxis2,
                               yAxis2=yAxis2,
                               chartID_turb=chartID_turb, chart_turb=chart_turb, series_turb=series_turb,
                               title_turb=title_turb, xAxis_turb=xAxis_turb, yAxis_turb=yAxis_turb,
                               chartID_kond=chartID_kond, chart_kond=chart_kond, series_kond=series_kond,
                               title_kond=title_kond, xAxis_kond=xAxis_kond, yAxis_kond=yAxis_kond)
    except Exception as e:
        return str(e)

#Gammel dashboard
@app.route('/dashboard')
# Viser siste 24h. Intervall blir bestemt med m_pr_h
def graph(chart1ID = 'chart1_ID', chart1_type = 'line', chart1_height = 400,
          chart2ID = 'chart2_ID',chart2_type = 'line', chart2_height = 400,
          chartID_turb = "chart_turb_ID",chart_turb_type = "line",chart_turb_height = 400,
          chartID_kond = "chart_kond_ID", chart_kond_type = "line", chart_kond_height = 400):
    try:

        # Henter dato og finner aktuell og forrige mnd's tabellnavn
        date_time = str(datetime.datetime.now())
        dato = date_time[0:10] # YYYY-MM-DD
        tablename = dbTransmit.createTableName(dato)
        prev_tablename = dbTransmit.getPrevMonth(tablename)

        # Antall maalinger pr time som skal vises.
        m_pr_h = 1

        conn = MySQLdb.connect("localhost","jakob","","Vikelva")
        if not dbTransmit.tableExists(conn,tablename):
            return "Ingen data som kan vises :("


        # Dersom true: mer enn en tabell
        if dbTransmit.tableExists(conn,prev_tablename):
            if dbTransmit.getTableLength(conn,tablename) >= (24 * m_pr_h):
                dataset = dbTransmit.getTableData(conn, tablename)

                ph_list = []
                temp_list = []
                turb_list = []
                kond_list = []

                time_list = []

                # Henter ut siste 24 verdier
                for x in range(len(dataset)):
                    if x > ((24 * m_pr_h) -1):
                        break

                    ph = float(dataset[len(dataset) - 1 - x][3])
                    temp = float(dataset[len(dataset) - 1 - x][4])
                    turb = float(dataset[len(dataset) - 1 - x][5])
                    kond = float(dataset[len(dataset) - 1 - x][6])

                    time = dataset[len(dataset) - 1 - x][2]

                    ph_list.append(ph)
                    temp_list.append(temp)
                    turb_list.append(turb)
                    kond_list.append(kond)
                    time_list.append(time)
            else:
                dataset_current = dbTransmit.getTableData(conn,tablename)
                antall_current = len(dataset_current)
                antall_prev = (m_pr_h * 24) - antall_current

                ph_list = []
                temp_list = []
                turb_list = []
                kond_list = []

                time_list = []
                # Henter ut all fra current date
                for x in range(len(dataset_current)):
                    if x > ((24 * m_pr_h) - 1):
                        break

                    ph = float(dataset_current[len(dataset_current) - 1 - x][3])
                    temp = float(dataset_current[len(dataset_current) - 1 - x][4])
                    turb = float(dataset_current[len(dataset_current) - 1 - x][5])
                    kond = float(dataset_current[len(dataset_current) - 1 - x][6])

                    time = dataset_current[len(dataset_current) - 1 - x][2]

                    ph_list.append(ph)
                    temp_list.append(temp)
                    turb_list.append(turb)
                    kond_list.append(kond)
                    time_list.append(time)

                dataset_prev = dbTransmit.getTableData(conn,prev_tablename)
                for x in range(antall_prev):
                    ph = float(dataset_prev[len(dataset_prev)-1 -x][3])
                    temp = float(dataset_prev[len(dataset_prev)-1 -x][4])
                    turb = float(dataset_prev[len(dataset_prev)-1-x][5])
                    kond = float(dataset_prev[len(dataset_prev)-1-x][6])

                    time = dataset_prev[len(dataset_prev)-1-x][2]

                    ph_list.append(ph)
                    temp_list.append(temp)
                    turb_list.append(turb)
                    kond_list.append(kond)
                    time_list.append(time)



        # Hvis ikke true, bare en tabell
        else:
            dataset = dbTransmit.getTableData(conn,tablename)

            ph_list = []
            temp_list = []
            turb_list = []
            kond_list = []

            time_list = []

            # Henter ut siste 24 * m_pr_h verdier
            for x in range(len(dataset)):
                if x > ((24 * m_pr_h) -1):
                    break

                ph = float(dataset[len(dataset)-1-x][3])
                temp = float(dataset[len(dataset)-1-x][4])
                turb = float(dataset[len(dataset)-1-x][5])
                kond = float(dataset[len(dataset)-1-x][6])

                time = dataset[len(dataset)-1-x][2]

                ph_list.append(ph)
                temp_list.append(temp)
                turb_list.append(turb)
                kond_list.append(kond)
                time_list.append(time)

        ph_rev = []
        temp_rev = []
        kond_rev = []
        turb_rev = []
        time_list_rev = []
        for x in range(len(ph_list)):
            ph_rev.append(ph_list[len(ph_list)-1-x])
            temp_rev.append(temp_list[len(temp_list)-1-x])
            kond_rev.append(kond_list[len(kond_list)-1-x])
            turb_rev.append(turb_list[len(turb_list)-1-x])
            time_list_rev.append(time_list[len(time_list)-1-x])


        ph_list = ph_rev
        temp_list = temp_rev
        kond_list = kond_rev
        turb_list = turb_rev
        time_list = time_list_rev

        chart_kond = {"renderTo": chartID_kond, "type": chart_kond_type, "height": chart_kond_height, "backgroundColor":'transparent' }
        series_kond = [{"name": 'Siste 24h', "data": kond_list},]
        title_kond = {"text": 'TDS utvikling i  Vikelva', "style":{"color":"black"}}
        xAxis_kond = { "categories": time_list, "labels": {"style": {"color": 'black'}}}
        yAxis_kond = {"title": {"text": 'Konduktivitet',"style": {"color": 'black'}},"labels": {"style": {"color": 'black'}}}

        chart_turb = {"renderTo": chartID_turb, "type": chart_turb_type, "height": chart_turb_height, "backgroundColor":'transparent' }
        series_turb = [{"name": 'Siste 24h', "data": turb_list},]
        title_turb = {"text": 'Turbiditetsutvikling i  Vikelva',"style":{"color":"black"}}
        xAxis_turb = { "categories": time_list,"labels": {"style": {"color": 'black'}}}
        yAxis_turb = {"title": {"text": 'Turbditet',"style": {"color": 'black'}},"labels": {"style": {"color": 'black'}}}

        chart1 = {"renderTo": chart1ID, "type": chart1_type, "height": chart1_height, "backgroundColor":'transparent'}
        series1 = [{"name": 'Siste 24h', "data": temp_list},]
        title1 = {"text": 'Temperaturutvikling Vikelva',"style":{"color":"black"}}
        xAxis1 = {"categories": time_list,"labels": {"style": {"color": 'black'}}}
        yAxis1 = {"title": {"text": 'Grader Celsius',"style": {"color": 'black'}},"labels": {"style": {"color": 'black'}}}

        chart2 = {"renderTo": chart2ID, "type": chart2_type, "height": chart2_height,"backgroundColor":'transparent'}
        series2 = [{"name": 'Siste 24h', "data": ph_list},]
        title2 = {"text": 'pH utvikling Vikelva',"style":{"color":"black"}}
        xAxis2 = {"categories": time_list,"labels": {"style": {"color": 'black'}}}
        yAxis2 = {"title": {"text": 'pH',"style": {"color": 'black'}},"labels": {"style": {"color": 'black'}}}

        return render_template('graf.html',
                               chart1ID=chart1ID, chart1=chart1, series1=series1, title1=title1, xAxis1=xAxis1, yAxis1=yAxis1,
                               chart2ID = chart2ID, chart2 = chart2, series2 = series2, title2 = title2, xAxis2 = xAxis2, yAxis2 = yAxis2,
                               chartID_turb = chartID_turb, chart_turb = chart_turb, series_turb = series_turb, title_turb = title_turb, xAxis_turb = xAxis_turb, yAxis_turb = yAxis_turb,
                               chartID_kond = chartID_kond, chart_kond = chart_kond, series_kond = series_kond, title_kond = title_kond, xAxis_kond = xAxis_kond, yAxis_kond = yAxis_kond)
    except Exception as e:
        return str(e)

@app.route("/recieve_data", methods = ["POST"])
# rask test med gammelt script
def recieve():
    try:
        # Henter data fra TTN
        data = request.get_json()

        measurements = data['payload_fields']
        temp = measurements['temp']
        ph = measurements['ph']
        turb = measurements['turb']
        kond = measurements['kond']

        # Endrer type fra string til float
        temp = float(temp)
        ph = float(ph)
        turb = float(turb)
        kond = float(kond)

        # Henter ut timestamp. Spilitter i dato og tid. Format spesifisert ved koden.
        metadata = data['metadata']
        time = metadata['time']
        date = time[0:10]  # YYYY-MM-DD
        clock = time[11:16]  # HH:MM
        clock = dbTransmit.addOneHour(clock)
        clock = dbTransmit.addOneHour(clock)

        # Kanskje legge til noe som sjekker om dette er valid data.
        # Benytter imidlertidig valid = 'Y' her
        valid = 'Y'

        # Framtid: Legge til funksjon som finner ut hvilken elv, dersom vi har flere elver.
        # Atm bare en elv
        rivername = "Vikelva"

        # Legger inn i Nidelva
        status = dbTransmit.submitData(temp, ph, turb, kond, date, clock, valid, rivername)

        #Opdaterer csv fil med siste 24 for realtime
        m_pr_h = 1

        filename_temp = "/var/www/FlaskApp/FlaskApp/static/realtimedata/realtime_temp.csv"
        filename_ph = "/var/www/FlaskApp/FlaskApp/static/realtimedata/realtime_ph.csv"
        filename_turb = "/var/www/FlaskApp/FlaskApp/static/realtimedata/realtime_turb.csv"
        filename_kond = "/var/www/FlaskApp/FlaskApp/static/realtimedata/realtime_kond.csv"

        csvstatus_temp = dbTransmit.updateCSV(filename_temp,clock,temp,m_pr_h)
        csvstatus_ph = dbTransmit.updateCSV(filename_ph, clock, ph, m_pr_h)
        csvstatus_turb = dbTransmit.updateCSV(filename_turb, clock, turb, m_pr_h)
        csvstatus_kond = dbTransmit.updateCSV(filename_kond, clock, kond, m_pr_h)
        return status + "\n" + csvstatus_temp + "\n" + csvstatus_ph + "\n" + csvstatus_turb + "\n" + csvstatus_kond

    except Exception as e:
        return str(e)

@app.route("/datepicker",methods=["POST","GET"])
def pick():
    if request.method == "GET":
        return render_template('pick.html')
    else:
        data = request.form["date"]

        return render_template('pick.html',data = data)

@app.route("/")
def realtime():
    try:
        return render_template("realtime.html")
    except Exception as e:
        return str(e)
    
@app.route("/product")
def product():
    try:
        return render_template("product.html")
    except Exception as e:
        return str(e)

@app.route("/footer")
def fot():
    return render_template("footer.html")

if __name__ == "__main__":
    app.run()
