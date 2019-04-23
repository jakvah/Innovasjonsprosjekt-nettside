import MySQLdb
import os
import time
from datetime import date
import xlsxwriter


#GLOBAL VARS:
MONTH_CONVERTER = ({
	"januar":"jan",
	"februar":"feb",
	"mars":"mar",
	"april":"apr",
	"mai":"mai",
	"juni":"jun",
	"juli":"jul",
	"august":"aug",
	"september":"sep",
	"oktober":"okt",
	"november":"nov",
	"desember":"des"
})
MONTH_CONVERTER_INVERT = ({
	"jan":"januar",
	"feb":"februar",
	"mar":"mars",
	"apr":"april",
	"mai":"mai",
	"jun":"juni",
	"jul":"juli",
	"aug":"august",
	"sep":"september",
	"okt":"oktober",
	"nov":"november",
	"des":"desember"
})
MONTH_CONVERTER_INVERT_BIG = ({
	"jan":"Januar",
	"feb":"Februar",
	"mar":"Mars",
	"apr":"April",
	"mai":"Mai",
	"jun":"Juni",
	"jul":"Juli",
	"aug":"August",
	"sep":"September",
	"okt":"Oktober",
	"nov":"November",
	"des":"Desember"
})
MONTH_DIGIT_TO_STRING = ({
	"01":"jan",
	"02":"feb",
	"03":"mar",
	"04":"apr",
	"05":"mai",
	"06":"jun",
	"07":"jul",
	"08":"aug",
	"09":"sep",
	"10":"okt",
	"11":"nov",
	"12":"des"
})
MONTH_STRING_TO_DIGIT = ({
	"jan":"01",
	"feb":"02",
	"mar":"03",
	"apr":"04",
	"mai":"05",
	"jun":"06",
	"jul":"07",
	"aug":"08",
	"sep":"09",
	"okt":"10",
	"nov":"11",
	"des":"12"
})
LOGIN_DETAILS_VIKELVA = {
	"host":"localhost",
	"user":"jakob",
	"password":"",
	"database":"Vikelva"
}
LOGIN_DETAILS_GLOESELVA = {
	"host":"localhost",
	"user":"root",
	"password":"mysqlroot123",
	"database":"Nidelva"
}
LOGIN_DETAILS = {"Vikelva":LOGIN_DETAILS_VIKELVA,"Gloes":LOGIN_DETAILS_GLOESELVA}

# Dato er paa format YYYY-MM-DD
# tabell navn paa format mmm_yy (eks. feb_19)
def createTableName(dato):
	year_short = dato[2:4]
	month = dato[5:7]
	month_name = MONTH_DIGIT_TO_STRING[month]
	tableName = str(month_name) + "_" + str(year_short)

	return tableName

# Tar inn et tabellnavn som tilsvarer mnd
# Returnerer et tabellnavn som tilsvarer en mnd tidligere.
# mmm_yy
def getPrevMonth(tablename):
	year = int(tablename[4:6])
	month = tablename[0:3]
	month_digit = (MONTH_STRING_TO_DIGIT[month])
	# Sjekker om forst digit er null
	if month_digit[0] == "0":
		month_digit = month_digit[1]

	if int(month_digit) != 1:
		month_digit = int(month_digit)
		month_digit-= 1
		month = MONTH_DIGIT_TO_STRING["0" + str(month_digit)]
	else:
		month = "des"
		year -= 1

	tablename_prev = month + "_" + str(year)
	return tablename_prev

# Sjekker om tabellen eksisterer
def tableExists(dbcon,tablename):
	dbcur = dbcon.cursor()
    	dbcur.execute("""
        SELECT COUNT(*)
        FROM information_schema.tables
        WHERE table_name = '{0}'
        """.format(tablename.replace('\'', '\'\'')))
    	if dbcur.fetchone()[0] == 1:
        	dbcur.close()
        	return True

    	dbcur.close()
    	return False

# sjekker om en spesifikk dato med tidspunkt eksisterer
def timeDateExists(dato, tid, dbconn, tableName):
	sql = "SELECT * FROM " + str(tableName)
	dbcur = dbconn.cursor()
	dbcur.execute(sql)

	row = dbcur.fetchone()
	while row is not None:
		if row[1] == dato and row[2] == tid:
			return True
		row = dbcur.fetchone()

	return False

# Sjekker om en dato eksisterer
def dateExsists(dato,dbconn,tableName):
	sql = "SELECT * FROM " + str(tableName)
	dbcur = dbconn.cursor()
	dbcur.execute(sql)

	set = dbcur.fetchall()
	for row in set:
		if row[1] == dato:
			return True

	return False

# Oppdaterer gjennomsnittstabeller
def updateAvgTable(dbconn, tableName):
	try:
		dbcur = dbconn.cursor()
		avg_tableName = "avg_" + tableName

		if not tableExists(dbconn, avg_tableName):
			# Trenger ikke tid kolonnen ettersom gjensnt
			sql = "CREATE TABLE " + avg_tableName + "(id INT NOT NULL PRIMARY KEY AUTO_INCREMENT, \
							dato VARCHAR(10), \
							avg_ph DECIMAL(8,5), avg_temp DECIMAL(8,5), \
							avg_turb DECIMAL (8,5), avg_kond DECIMAL(8,5), \
							valid CHAR(1));"
			dbcur.execute(sql)
			dbconn.commit()

		# For the time beeing
		valid = "y"

		totalPhValue = 0
		totalTempValue = 0
		totalTurbValue = 0
		totalKondValue = 0

		# I utgangspunktet er alle disse de samme, men er mulighet for manglende data
		amountOfPh = 0
		amountOfTemp = 0
		amountOfTurb = 0
		amountOfKond = 0

		sql = "SELECT * FROM " + tableName
		dbcur.execute(sql)

		# Tuple of tuple med alle data
		dataSet = dbcur.fetchall()

		for rowNumber in range(len(dataSet)):
			currentRow = dataSet[rowNumber]
			currentDate = currentRow[1]

			totalPhValue += currentRow[3]
			totalTempValue += currentRow[4]
			totalTurbValue += currentRow[5]
			totalKondValue += currentRow[6]

			amountOfKond += 1
			amountOfTurb += 1
			amountOfPh += 1
			amountOfTemp += 1

			# Hvis current er ulik neste dag, legg inn i database, nullstill
			# Kan bli out_of_range error, derfor try,except
			try:
				nextDay = dataSet[(rowNumber + 1)][1]

				if currentDate != nextDay:
					avg_ph = totalPhValue / amountOfPh
					avg_temp = totalTempValue / amountOfTemp
					avg_turb = totalTurbValue / amountOfTurb
					avg_kond = totalKondValue / amountOfKond

					if dateExsists(currentDate,dbconn,avg_tableName):

						delete_sql = "DELETE FROM " + avg_tableName + " WHERE dato = '" + currentDate +"'"

						try:
							dbcur.execute(delete_sql)
						except Exception as e:
							print(e)

						dbconn.commit()

					sql = "INSERT INTO " + avg_tableName + """(id,dato,avg_ph,avg_temp,avg_turb,avg_kond,valid) VALUES (NULL,%s,%s,%s,%s,%s,%s)"""
					dbcur.execute(sql, [currentDate, avg_ph, avg_temp, avg_turb, avg_kond, valid])
					dbconn.commit()

					# Nullstille for ny dag
					totalPhValue = 0
					totalTempValue = 0
					totalTurbValue = 0
					totalKondValue = 0

					amountOfPh = 0
					amountOfTemp = 0
					amountOfTurb = 0
					amountOfKond = 0

			except IndexError:
				# Det finnes ingen neste dag, legg sammen og send inn
				avg_ph = totalPhValue / amountOfPh
				avg_temp = totalTempValue / amountOfTemp
				avg_turb = totalTurbValue / amountOfTurb
				avg_kond = totalKondValue / amountOfKond

				if dateExsists(currentDate, dbconn, avg_tableName):
					delete_sql = "DELETE FROM " + str(avg_tableName) + " WHERE dato = '" + str(currentDate) + "'"

					try:
						dbcur.execute(delete_sql)
					except Exception as e:
						print(str(e))

					dbconn.commit()

				sql = "INSERT INTO " + avg_tableName + """(id,dato,avg_ph,avg_temp,avg_turb,avg_kond,valid) VALUES (NULL,%s,%s,%s,%s,%s,%s)"""
				dbcur.execute(sql,[currentDate, avg_ph, avg_temp, avg_turb, avg_kond, valid])
				dbconn.commit()

		dbcur.close()

		return "Har oppdatert avg_tables med suksess!"
	except Exception as e:
		return str(e)


# Sender inn data. Tar seg av avg_tabell med update_avg ovenfor
def submitData(temp,ph,turb,kond,dato,tid,valid,river):
	try:
		# Finner korrekt tabell
		monthDigit = dato[5:7]
		shortMonth = MONTH_DIGIT_TO_STRING[monthDigit]
		shortYear = dato[2:4]
		tableName = shortMonth + "_" + shortYear

		login_config = LOGIN_DETAILS[river]

		# Oppretter MySQLdb connection
		conn = MySQLdb.connect(**login_config)
		c = conn.cursor()

		# Avgjore om eksisterer
		if not (tableExists(conn,tableName)):
			#Opprette tabell
			sql = "CREATE TABLE " + tableName + "(id INT NOT NULL PRIMARY KEY AUTO_INCREMENT, \
			dato VARCHAR(10), tid VARCHAR(8), \
			ph DECIMAL(8,5), temp DECIMAL(8,5), \
			turb DECIMAL (8,5), kond DECIMAL(8,5), \
			valid CHAR(1));"

			c.execute(sql)
			conn.commit()

		insert_sql = "INSERT INTO " + tableName + """(id,dato,tid,ph,temp,turb,kond,valid) VALUES (NULL,%s,%s,%s,%s,%s,%s,%s)"""
		c.execute(insert_sql,[dato,tid,ph,temp,turb,kond,valid])
		conn.commit()

		c.close()

		# Oppdaterer gjennomsnittet for denne dagen
		status = updateAvgTable(conn,tableName)

		return "Tilbakemeldig fra vanlig tabell: Lagt inn data i vanlig tabell " \
               "med suksess \nTilbakemedlig fra avg_tables: " + status

	except Exception as err:
		return "Tilbakemeldig fra vanlig tabell: "+ str(err) + "\nTilbakemedling fra avg_tables: " \
                "Ikke oppdatert avg_tables pga feil i vanlig tabell"

# Henter gjennomsnitt tabell for aktuell mnd og year
def getTupleDB(month, year):
	login_config = LOGIN_DETAILS["Vikelva"]

	conn = MySQLdb.connect(**login_config)
	c = conn.cursor()

	avg_tableName = "avg_" + str(month) + "_" + str(year)
	sql = "SELECT * FROM " + avg_tableName
	c.execute(sql)

	dataSet = c.fetchall()
	return dataSet

# Legger inn data i scriptet som fyller databser med random data
def submitForFilling(temp,ph,turb,kond,dato,tid,valid,river):
	try:
		# Finner korrekt tabell
		monthDigit = dato[5:7]
		shortMonth = MONTH_DIGIT_TO_STRING[monthDigit]
		shortYear = dato[2:4]
		tableName = shortMonth + "_" + shortYear

		login_config = LOGIN_DETAILS[river]

		# Oppretter MySQLdb connection
		conn = MySQLdb.connect(**login_config)
		c = conn.cursor()

		# Avgjore om eksisterer
		if not (tableExists(conn,tableName)):
			#Opprette tabell
			sql = "CREATE TABLE " + tableName + "(id INT NOT NULL PRIMARY KEY AUTO_INCREMENT, \
			dato VARCHAR(10), tid VARCHAR(8), \
			ph DECIMAL(8,5), temp DECIMAL(8,5), \
			turb DECIMAL (8,5), kond DECIMAL(8,5), \
			valid CHAR(1));"

			c.execute(sql)
			conn.commit()

		insert_sql = "INSERT INTO " + tableName + """(id,dato,tid,ph,temp,turb,kond,valid) VALUES (NULL,%s,%s,%s,%s,%s,%s,%s)"""
		c.execute(insert_sql,[dato,tid,ph,temp,turb,kond,valid])
		conn.commit()

		c.close()

		# Oppdaterer gjennomsnittet for denne dagen
		#updateAvgTable(conn,tableName)

		return "Lagt inn med suksess og oppdatert avg_table"

	except Exception as err:
		return "Failed: " + str(err)

# Henter alle rader fra aktuell dato
# Dato = YYYY-MM-DD
def getDateData(dato,river):
	login_cfg = LOGIN_DETAILS[river]
	conn = MySQLdb.connect(**login_cfg)
	c = conn.cursor()

	month = dato[5:7]
	month_f = MONTH_DIGIT_TO_STRING[month]
	year = dato[2:4]
	tableName = month_f + "_" + year
	sql = "SELECT * FROM " + tableName + """ where dato = '""" + dato + """'"""

	c.execute(sql)

	dataSet = c.fetchall()

	c.close()
	return dataSet

def shortToLongMonth(month):
	return MONTH_CONVERTER_INVERT[month]

def digitToString(digit):
	return MONTH_DIGIT_TO_STRING[digit]

# Lager en liste med URLer som passer til datoene i listen
# Brukes til aa kunne klikke paa en dato aa komme til denne datoen
def convertToURL(dataTuple):
	# Lager list med url
	urlList = []
	for row in dataTuple:
		dato = row[1]
		url = "/hisdat/date/" + dato
		urlList.append(url)

	overview = {}
	for n in range(len(urlList)):
		t = tuple(dataTuple[n])
		overview[t] = urlList[n]
	return overview

# Konverterer dato paa et "stygt" format til en pent format
# Innkommende dato paa format YYYY-MM-DD
def convertToDisplayDate(dataTuple):
	dateList = []
	for row in dataTuple:
		date = row[1]
		dispDate = displayDateNoYear(date) # Evt med displayDateFully
		dateList.append(dispDate)

	overview = {}
	for n in range(len(dateList)):
		t = tuple(dataTuple[n])
		overview[t] = dateList[n]
	return overview


# Gir en fullstendig dato som kan vises
# Innkommende dato paa format YYYY-MM-DD
def displayDateFully(dato):
	month = dato[5:7]
	month = MONTH_DIGIT_TO_STRING[month]
	month = MONTH_CONVERTER_INVERT[month]

	day = dato[8:10]
	if int(day) < 10:
		day = str(day)
		day = day[-1]

	year = dato[0:4]

	return day +". " + month + " " + year

# Gir en pen dato uten aar
# Innkommende dato paa format YYYY-MM-DD
def displayDateNoYear(dato):
	month = dato[5:7]
	month = MONTH_DIGIT_TO_STRING[month]
	month = MONTH_CONVERTER_INVERT[month]

	day = dato[8:10]
	if int(day) < 10:
		day = str(day)
		day = day[-1]
	return day + ". " + month

def shortToLongBigMonth(month):
	bigm = MONTH_CONVERTER_INVERT_BIG[month]
	return bigm

# validate_data(temp, ph, turb, tds) returns 'y' if the paranmeter is within a valid
# range, and 'n' if it is outside a valid range. It also returns a boolean variable
# v, which returns True only if all the data is valid.
def validate_data(temp, ph, turb, tds):
	tempV, phV, turbV, tdsV = 'y', 'y', 'y', 'y'
	v = True
	if temp <= -10 or temp >= 30:
		tempV = 'n'
	if ph <= 0 or ph >= 14:
		phV = 'n'
	if turb <= 0 or turb >= 3000:
		turbV = 'n'
	if tds <= 0 or tds >= 1000:
		tdsV = 'n'

	if tempV == 'n' or phV == 'n' or turbV == 'n' or tdsV == 'n':
		v = False
	return v

# Henter hele tabellen i tabelename
def getTableData(dbconn, tablename):
	cur = dbconn.cursor()
	sql = "SELECT * FROM " + tablename
	cur.execute(sql)
	dataset = cur.fetchall()
	cur.close()

	return dataset

# Returnerer lengden paa tabellen
def getTableLength(dbconn, tablename):
	cur = dbconn.cursor()
	sql = "SELECT * FROM " + tablename
	cur.execute(sql)
	dataset = cur.fetchall()
	l = int(len(dataset))
	return l


# Legger inn time og value i en csv fil.
# Sorger for at det er maks 24*(m_pr_h) verdier
# Filename boer vaere absolute path
def updateCSV(filename, time, value, m_pr_h):
	try:
		file = open(filename, 'r')
		length = file.readlines()[1:]
		#print(len(length))
		if len(length) < (24 * m_pr_h):
			# Bare legg til
			file.close()
			file = open(filename, 'a')
			linebreak = "\n"
			file.write(linebreak)
			newline = str(time) + "," + str(value)
			file.write(newline)
			file.close()
		else:
			# Legger til og fjerner
			lines = length[1:]
			file.close()

			file = open(filename, 'w')
			file.write("Tid, Siste 24 timer \n")
			for line in lines:
				file.write(line)

			linebreak = "\n"
			file.write(linebreak)
			file.close()
			newline = str(time) + "," + str(value)
			file = open(filename, 'a')
			file.write(newline)
			file.close()
		return "Data lagt inn i " + str(filename[46:])
	except Exception as e:
		return str(e)

# Fjerner alle verdier fra CSV fil
def clearCSV(filename):
	file = open(filename,'w')
	file.write("Tid, Verdi")
	file.close()

# date = YYYY-MM-DD
def getDateIndex(date):
	dataset = getDateData(date,"Vikelva")
	day = date[8:]
	index = 0
	for rad in dataset:
		dato = rad[1]
		tableday = dato[8:]
		if tableday == day:
			break
		index += 1
	return index

def isPeriodeValid(start,slutt):
	startyear = start[:4]
	endyear = slutt[:4]


	startmonth = start[5:7]
	endmonth = slutt[5:7]

	if int(startyear) < int(endyear):
		return True
	if int(startmonth) < int(endmonth):
		return True

	elif int(startmonth) == int(endmonth):
		startday = start[8:]
		endday = slutt[8:]
		if int(startday) < int(endday):
			return True
		elif int(startday) == int(endday):
			return True
		elif int(startday) > int(endday):
			return False

	elif int(startmonth) > int(endmonth):
		return False

#YYYY-MM-DD
def datesAlike(date1,date2):
    if date1 == date2:
        return True
    return False

# YYYY-MM-DD
# Sketchy ting som ble gjrot i etterkant; alle list() arguemnter, og +2 indez korreksjon
def getPeriodData(start,slutt,TERSKEL):
	login_config = LOGIN_DETAILS["Vikelva"]
	# Oppretter MySQLdb connection
	conn = MySQLdb.connect(**login_config)

	if datesAlike(start,slutt):
		dataset = getDateData(start,"Vikelva")
		return dataset

	else:
		mnd_list = ["jan","feb","mar","apr","mai","jun","jul","aug","sep","okt","nov","des"]
		startyear = start[0:4]
		sluttyear = slutt[0:4]
		start_month_no_year = MONTH_DIGIT_TO_STRING[start[5:7]]
		end_month_no_year = MONTH_DIGIT_TO_STRING[slutt[5:7]]

		start_mnd_list_index = mnd_list.index(start_month_no_year)
		end_mnd_list_index = mnd_list.index(end_month_no_year)

		# Finner indexer til vanlig
		tempnavn = createTableName(start)
		tempset = getTableData(conn,tempnavn)
		start_date_table_index = 0 # denne sier hvor i mnd tabell start dato er
		for rad in tempset:
			if rad[1] == start:
				break
			start_date_table_index += 1

		tempnavn = createTableName(slutt)
		tempset = getTableData(conn,tempnavn)
		end_date_table_index = 0 # denne sier hvor i mdn tabell slutt dato er
		for rad in tempset:
			if rad[1] == slutt:
				break
			end_date_table_index += 1

		# Finner indexer til avg table
		tempset = getTupleDB(start_month_no_year,startyear[2:])
		start_date_avg_table_index = 0
		for rad in tempset:
			if rad[1] == start:
				break
			start_date_avg_table_index += 1

		tempset = getTupleDB(end_month_no_year, sluttyear[2:])
		end_date_avg_table_index = 0
		for rad in tempset:
			if rad[1] == slutt:
				break
			end_date_avg_table_index += 1

		# Finner tablename list
		tablename_list = []
		if (int(sluttyear) - int(startyear)) == 0:
			for x in range(start_mnd_list_index,end_mnd_list_index+1):
				m = mnd_list[x]
				y = startyear[2:]
				tablename = m + "_" + y
				tablename_list.append(tablename)
		else:
			# Lager year list
			year_list = []
			temp = startyear
			while temp != sluttyear:
				year_list.append(temp)
				temp = str(int(temp) +1)
			year_list.append(sluttyear)

			# Fikser start year tabeller
			print(start_mnd_list_index)
			for x in range(start_mnd_list_index,12):
				m = mnd_list[x]
				y = startyear[2:]
				tablename = m + "_" + y
				tablename_list.append(tablename)
			# Alle uten start og slutt year
			for y in year_list:
				print(y)
				if not (y == startyear or y == sluttyear):
					y = y[2:]
					for x in range(12):
						m = mnd_list[x]
						tablename = m + "_" + y
						tablename_list.append(tablename)
			# Slutt year
			for x in range(end_mnd_list_index +1):
				m = mnd_list[x]
				y = sluttyear[2:]
				tablename = m + "_" + y
				tablename_list.append(tablename)


		# Henter data
		if getDateDifference(start,slutt) <= TERSKEL:
			dataset = []
			if (start[5:7] == slutt[5:7]) and (int(sluttyear) - int(startyear) == 0):

				mnd_set = getTableData(conn,tablename_list[0])
				for x in range(start_date_table_index,end_date_table_index +24): # +24 fordi vi skal ha med hele dagen.
					dataset.append(list(mnd_set[x]))
			else:
				for t in tablename_list:
					mnd_set = getTableData(conn,t)
					if t == createTableName(start):
						for x in range(start_date_table_index,len(mnd_set)):
							dataset.append(list(mnd_set[x]))
					elif t == createTableName(slutt):
						for x in range(end_date_table_index +24): # +24 fordi vil skal ha med hele dagen
							dataset.append(list(mnd_set[x]))
					else:
						for m in mnd_set:
							dataset.append(list(m))
		else:
			dataset = []
			if (start[5:7] == slutt[5:7]) and (int(sluttyear) - int(startyear) == 0):
				mnd_set = getTupleDB(start_month_no_year,startyear[2:])
				for x in range(start_date_avg_table_index,end_date_avg_table_index +1):
					dataset.append(list(mnd_set[x]))
			else:
				for t in tablename_list:
					mnd_set = getTupleDB(t[0:3],t[4:])
					if t == createTableName(start):
						for x in range(start_date_avg_table_index,len(mnd_set)):
							dataset.append(list(mnd_set[x]))
					elif t == createTableName(slutt):
						for x in range(end_date_avg_table_index +1):
							dataset.append(list(mnd_set[x]))
					else:
						for m in mnd_set:
							dataset.append(list(m))

		return dataset

# type; g for gjennomsnitt, alt annet er hele pakken
def createExcel(dataset,filename,type):
    try:
        wb = xlsxwriter.Workbook(filename)
        ws = wb.add_worksheet()

        time_list = []
        dato_list = []
        ph_list = []
        turb_list = []
        kond_list = []
        temp_list = []

        if type != "m":
            for rad in dataset:
                dato_list.append(rad[1])
                time_list.append(rad[2])
                ph_list.append(float(rad[3]))
                temp_list.append(float(rad[4]))
                turb_list.append(float(rad[5]))
                kond_list.append(float(rad[6]))

            # Setter opp header
            ws.write(0, 0, "Dato")
            ws.write(0, 1, "Klokkeslett")
            ws.write(0, 2, "pH")
            ws.write(0, 3, "Temperatur")
            ws.write(0, 4, "TDS")
            ws.write(0, 5, "Turbiditet")

            row = 1
            for x in range(len(dato_list)):
                ws.write(row, 0, dato_list[x])

                ws.write(row, 1, time_list[x])
                ws.write(row, 2, ph_list[x])
                ws.write(row, 3, temp_list[x])
                ws.write(row, 4, kond_list[x])
                ws.write(row, 5, turb_list[x])

                row += 1

        else:
            for rad in dataset:
                dato_list.append(rad[1])
                ph_list.append(float(rad[2]))
                temp_list.append(float(rad[3]))
                turb_list.append(float(rad[4]))
                kond_list.append(float(rad[5]))
            # Setter opp header
            ws.write(0, 0, "Dato")
            ws.write(0, 1, "pH")
            ws.write(0, 2, "Temperatur")
            ws.write(0, 3, "TDS")
            ws.write(0, 4, "Turbiditet")

            row = 1

            for x in range(len(dato_list)):
                ws.write(row, 0, dato_list[x])
                ws.write(row, 1, ph_list[x])
                ws.write(row, 2, temp_list[x])
                ws.write(row, 3, kond_list[x])
                ws.write(row, 4, turb_list[x])

                row += 1

        wb.close()
    except Exception as e:
        return str(e)

# HH:MM
def addOneHour(clock):
	hour = clock[:2]
	if hour[0] != "0":
		if int(hour) < 23:
			hour = int(hour) + 1
			hour = str(hour)
		else:
			hour = "00"
	else:
		if int(hour[1]) < 9:
			hour = int(hour) + 1
			hour = "0" + str(hour)
		else:
			hour = "10"

	return hour + ":" + clock[3:5]

#YYYY-MM-DD
def getDateDifference(date1,date2):
	y1 = date1[:4]
	y2 = date2[:4]

	m1 = date1[5:7]
	m2 = date2[5:7]

	d1 = date1[8:]
	d2 = date2[8:]

	d1 = date(int(y1), int(m1), int(d1))
	d2 = date(int(y2), int(m2), int(d2))

	delta = d2 - d1
	diff = int(delta.days)

	return diff

def removeFile(filename):
    try:
        os.remove(filename)
        return "Slettet med suksess"
    except Exception as e:
        return str(e)

# type = avg for gjennomsnittstabeller
def getMaxIndex(dataset,parameter,type):
	if type == "avg":
		if parameter == "ph":
			col = 2
		elif parameter == "temp":
			col = 3
		elif parameter == "turb":
			col = 4
		elif parameter == "kond":
			col = 5
		else:
			return "Ugyldig paramter"

	else:
		if parameter == "ph":
			col = 3
		elif parameter == "temp":
			col = 4
		elif parameter == "turb":
			col = 5
		elif parameter == "kond":
			col = 6
		else:
			return "Ugyldig paramter"

	currentMax = 0
	indexList = []
	for index in range(len(dataset)):
		value = float(dataset[index][col])
		if value == currentMax:
			indexList.append(index)
			currentMax = value
		elif value > currentMax:
			del indexList
			indexList = []
			indexList.append(index)
			currentMax = value


	return indexList

def getMinIndex(dataset,parameter,type):
	if type == "avg":
		if parameter == "ph":
			col = 2
		elif parameter == "temp":
			col = 3
		elif parameter == "turb":
			col = 4
		elif parameter == "kond":
			col = 5
		else:
			return "Ugyldig paramter"

	else:
		if parameter == "ph":
			col = 3
		elif parameter == "temp":
			col = 4
		elif parameter == "turb":
			col = 5
		elif parameter == "kond":
			col = 6
		else:
			return "Ugyldig paramter"

	currentMin = float(dataset[0][col])
	indexList = []
	for index in range(len(dataset)):
		value = float(dataset[index][col])
		if value == currentMin:
			indexList.append(index)
			currentMin = value
		elif value < currentMin:
			del indexList
			indexList = []
			indexList.append(index)
			currentMin = value

	return indexList
def getValue(dataset,parameter,type,index):
	if type == "avg":
		if parameter == "ph":
			col = 2
		elif parameter == "temp":
			col = 3
		elif parameter == "turb":
			col = 4
		elif parameter == "kond":
			col = 5
		else:
			return "Ugyldig paramter"

	else:
		if parameter == "ph":
			col = 3
		elif parameter == "temp":
			col = 4
		elif parameter == "turb":
			col = 5
		elif parameter == "kond":
			col = 6
		else:
			return "Ugyldig paramter"

	value = dataset[index][col]
	return value

#returnerer filname i sekunder
def file_age(filepath):
	return time.time() - os.path.getmtime(filepath)
