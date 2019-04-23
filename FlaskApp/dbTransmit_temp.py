# Samling for alle scripts til elsysprosjekt.
# Bruk kun A-Z i kommentarer og til string etc...!!

import MySQLdb

#bllnlblblblbl

#GLOBAL VARS:
MONTH_LONG_TO_SHORT = ({
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
MONTH_SHORT_TO_LONG = ({
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
LOGIN_DETALIS_VIKELVA = {
    "host":"localhost",
    "user":"jakob",
    "password":"",
    "database":"Vikelva"
}
LOGIN_DETAILS = {"Vikelva":LOGIN_DETALIS_VIKELVA}


# Returnerer data vi vil ha.
# data er hele driten fra TTN.
def getData(data):
    payload = data["payload_fields"]

    temp = payload["temp"]
    ph = payload["ph"]
    turb = payload["turb"]
    kond = payload["kond"]

    meta = data["metadata"]
    all_tid = meta["time"]

    dato = all_tid[0:10]
    tid = all_tid[11:16]

    return float(temp), float(ph), float(turb), float(kond), dato, tid

# Dato er paa format YYYY-MM-DD
def createTableName(dato):
    year_short = dato[2:4]
    month = dato[5:7]
    month_name = MONTH_DIGIT_TO_STRING[month]
    tableName = str(month_name) + "_" + str(year_short)

    return tableName

# Oppretter en dBConnection til rivername
def createConnection(rivername):

    dbCon = MySQLdb.connect(host = "localhost",user="jakob", password="", db=rivername)

    return dbCon

# Sjekker om tablename er i dbcon
# Husk at dbcon tilsvarer en database
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

# Legger inn data i tablename i tilkoblingen conn.
# Dersom den ikke finnes (ny mnd) opprettes ny tabell.
def submitData(temp, ph, turb, kond, dato, tid, valid, conn, tableName):
    try:
        c = conn.cursor()

        # Avgjore om eksisterer
        if not (tableExists(conn, tableName)):
            # Opprette tabell
            sql = "CREATE TABLE " + tableName + """(id INT NOT NULL PRIMARY KEY AUTO_INCREMENT, dato VARCHAR(10), tid VARCHAR(8), ph DECIMAL(8,5), temp DECIMAL(8,5), turb DECIMAL (8,5), kond DECIMAL(8,5), valid CHAR(1));"""

            c.execute(sql)
            conn.commit()
        # Tabell er naa garantet opprettet. Legger inn
        insert_sql = "INSERT INTO " + tableName + """(id,dato,tid,ph,temp,turb,kond,valid) VALUES (NULL,%s,%s,%s,%s,%s,%s,%s)"""
        c.execute(insert_sql, [dato, tid, ph, temp, turb, kond, valid])
        conn.commit()

        c.close()

        return "Lagt inn med suksess"

    except Exception as err:

        return "Failed: " + str(err)

# Oppdaterer tabell med

# Oppdaterer gjennomsnittstabellen
# Oppretter en ny dersom den ikke finnes (ny mnd)
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

		return "Suksess"
	except Exception as e:
		return str(e)

# True hvis datoen finnes, false hvis ikke
def dateExsists(dato, dbconn, tableName):
    sql = "SELECT * FROM " + str(tableName)
    dbcur = dbconn.cursor()
    dbcur.execute(sql)

    row = dbcur.fetchone()

    while row is not None:
        if row[1] == dato:
            return True

    return False

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
    return tempV, phV, turbV, tdsV, v

