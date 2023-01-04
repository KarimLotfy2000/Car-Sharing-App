from flask import Flask, request, render_template, url_for
from werkzeug.utils import redirect

import connect
import csv
import re
from date_time_util import convertDateAndTimeToDB2DateTime
from datetime import datetime


app = Flask(__name__, template_folder='template')

currentUser = "1"

conn = connect.DBUtil().getExternalConnection()
conn.jconn.setAutoCommit(False)

def csv_reader(path):
    with open(path, "r") as csvfile:
        tmp = {}
        reader = csv.reader(csvfile, delimiter='=')
        for line in reader:
            tmp[line[0]] = line[1]
    return tmp

config = csv_reader("properties.settings")

@app.route('/', methods=['GET'])
def viewMain():
    conn = connect.DBUtil().getExternalConnection()
    con = conn.cursor()
    try:
        query_free_trips = "select fahrt.fid fahrt, fahrt.startort startort, fahrt.zielort zielort, fahrt.fahrtkosten fahrtkosten, sum(reservieren.anzPlaetze) anzPlaetze, max(fahrt.maxPlaetze) maxPlaetze, fahrt.transportmittel transportmittel from reservieren, fahrt where fahrt.fid not in (select fahrt from reservieren where kunde = " + currentUser + ") and fahrt.fid = reservieren.fahrt group by fahrt.fid, fahrt.startort, fahrt.zielort, fahrt.fahrtkosten, fahrt.transportmittel having max(fahrt.maxPlaetze) > sum(reservieren.anzPlaetze)"
        con.execute(query_free_trips)
        free_trips = con.fetchall()
        query_reserved_by_user = "select fahrt.fid fahrt, fahrt.startort startort, fahrt.zielort zielort, fahrt.status status, fahrt.transportmittel transportmittel from reservieren, fahrt where reservieren.kunde = " + currentUser + " and fahrt.fid = reservieren.fahrt"
        con.execute(query_reserved_by_user)
        reserved_by_user = con.fetchall()
        query_non_reserved_trips = "select fahrt.fid fahrt, fahrt.startort startort, fahrt.zielort zielort, fahrt.fahrtkosten fahrtkosten, fahrt.maxPlaetze maxPlaetze, fahrt.transportmittel transportmittel from fahrt where fahrt.fid not in (select distinct fahrt from reservieren)"
        con.execute(query_non_reserved_trips)
        non_reserved_trips = con.fetchall()

        con.close()
        return render_template('view_main.html', data={"free_trips": free_trips, "reserved_by_user": reserved_by_user, "non_reserved_trips": non_reserved_trips})
    except Exception as e:
        con.rollBack()
        con.close()
        return render_template(redirect('viewMain'))

@app.route('/newDrive', methods=['GET'])
def newDriveGet():
    return render_template('new_drive.html', errors=[])

@app.route('/newDrive', methods=['POST'])
def newDrivePost():
    conn = connect.DBUtil().getExternalConnection()
    con = conn.cursor()

    try:
        von = request.form.get('von')
        bis = request.form.get('bis')
        maxkap = request.form.get('maxkap')
        kosten = request.form.get('kosten')
        transportmittel = request.form.get('transportmittel')
        fahrtdatum = request.form.get('fahrtdatum')
        fahrttime = request.form.get('fahrttime')
        beschreibung = request.form.get('beschreibung')

        errors = []
        if maxkap is None or not maxkap.isnumeric() or int(maxkap) > 10:
            errors.append("Maximum number of places is not valid.")
        if kosten is None or not kosten.isnumeric() or int(kosten) < 0:
            errors.append("Travel expenses is not valid.")
        travel_date_str = convertDateAndTimeToDB2DateTime(fahrtdatum, fahrttime)
        travel_date = datetime.strptime(travel_date_str, '%Y-%m-%d %H:%M:%S.%f')
        present = datetime.now()
        if travel_date is None or present > travel_date:
            errors.append("Travel date is not valid.")
        if beschreibung is None or len(beschreibung) > 50:
            errors.append("Travel description is not valid.")

        if len(errors) == 0:
            new_drive_query = "INSERT INTO fahrt (startort, zielort, fahrtdatumzeit, maxPlaetze, fahrtkosten, anbieter, transportmittel, beschreibung) VALUES(?, ?, ?, ?, ?, ?, ?, ?)"
            con.execute(new_drive_query, (von, bis, travel_date_str, int(maxkap), float(kosten), int(currentUser), int(transportmittel), beschreibung))

            con.close()
            return redirect(url_for('viewMain'))

        else:
            return render_template('new_drive.html', errors=errors)
    except Exception as e:
        con.rollBack()
        con.close()
        return render_template(redirect('viewMain'))

@app.route('/viewDrive/<id>/<errors>', methods=['GET'])
def viewDrive(id, errors):
    conn = connect.DBUtil().getExternalConnection()
    con = conn.cursor()

    if errors == 'empty':
        errors = ''
    try:
        view_drive_query = "select fahrt.startort, fahrt.zielort, fahrt.fahrtdatumzeit, fahrt.status, fahrt.fahrtkosten, fahrt.anbieter, fahrt.transportmittel, cast(fahrt.beschreibung as varchar(32000)), benutzer.email, fahrt.maxPlaetze, fahrt.fid, ap.anzPlaetze from fahrt, (select sum(anzPlaetze) anzPlaetze from reservieren where fahrt = " + id + ") ap, benutzer where fid = " + id + " and benutzer.bid = fahrt.anbieter"
        con.execute(view_drive_query)
        view_drive = con.fetchone()
        free_trip = False
        if view_drive[11] is None:
            view_drive_query = "select fahrt.startort, fahrt.zielort, fahrt.fahrtdatumzeit, fahrt.status, fahrt.fahrtkosten, fahrt.anbieter, fahrt.transportmittel, cast(fahrt.beschreibung as varchar(32000)), benutzer.email, fahrt.maxPlaetze, fahrt.fid from fahrt, benutzer where fid = " + id + " and benutzer.bid = fahrt.anbieter"
            con.execute(view_drive_query)
            view_drive = con.fetchone()
            free_trip = True
        query_avg_ratings = "select avg(rating) from bewertung, schreiben where bewertung.beid = schreiben.bewertung and schreiben.fahrt = " + id
        con.execute(query_avg_ratings)
        avg_ratings = con.fetchall()
        query_users_ratings = "select benutzer.email, bewertung.rating, cast(bewertung.textnachricht as varchar(32000)) from benutzer, bewertung, schreiben where benutzer.bid = schreiben.benutzer and bewertung.beid = schreiben.bewertung and schreiben.fahrt = " + id
        con.execute(query_users_ratings)
        users_ratings = con.fetchall()

        con.close()
        return render_template('view_drive.html', data=view_drive, free_trip=free_trip, avg_ratings=avg_ratings, users_ratings=users_ratings, errors=errors.split("-"))
    except Exception as e:
        con.rollBack()
        con.close()
        return render_template(redirect('viewMain'))

@app.route('/newReservation/<id>', methods=['POST'])
def newReservation(id):
    conn = connect.DBUtil().getExternalConnection()
    con = conn.cursor()
    try:
        seats = int(request.form['seats'])
        query_trip = "select status, anbieter, maxPlaetze from fahrt where fid = " + id
        con.execute(query_trip)
        trip = con.fetchall()
        query_num_reserved_seats = "select sum(anzPlaetze) from reservieren where fahrt = " + id
        con.execute(query_num_reserved_seats)
        num_reserved_seats_results = con.fetchall()
        num_reserved_seats = num_reserved_seats_results[0][0]
        if num_reserved_seats is None:
            num_reserved_seats = 0
        query_already_reserved = "select * from reservieren where kunde = " + currentUser + " and fahrt = " + id
        con.execute(query_already_reserved)
        already_reserved = con.fetchall()
        errors = ""
        flag = False
        if str(trip[0][1]) == currentUser:
            if flag:
                errors += "-"
            else:
                flag = True
            errors += "Creator of the trip can not reserve seats in it."
        if trip[0][0] != "offen":
            if flag:
                errors += "-"
            else:
                flag = True
            errors += "Trip is not open"
        if seats + num_reserved_seats > trip[0][2]:
            if flag:
                errors += "-"
            else:
                flag = True
            errors += "Not enough seats"
        if seats > 2 or seats < 1:
            if flag:
                errors += "-"
            else:
                flag = True
            errors += "Number of seats must be 1 or 2"
        if len(already_reserved) > 0:
            if flag:
                errors += "-"
            else:
                flag = True
            errors += "You can not reserve the same trip multiple times"
        if len(errors) == 0:
            errors = "empty"
            query_insert_reservation = "insert into reservieren (kunde, fahrt, anzPlaetze) values (?, ?, ?)"
            con.execute(query_insert_reservation, (currentUser, id, seats))
            if seats + num_reserved_seats == trip[0][2]:
                query_close_trip = "update fahrt set status = 'geschlossen' where fid = " + id
                con.execute(query_close_trip)

        con.close()
        return redirect(url_for('viewDrive', id=id, errors=errors))
    except Exception as e:
        con.rollBack()
        con.close()
        return render_template(redirect('viewMain'))

@app.route('/deleteTrip/<id>', methods=['GET'])
def deleteTrip(id):
    conn = connect.DBUtil().getExternalConnection()
    con = conn.cursor()
    try:
        query_trip = "select anbieter from fahrt where fid = " + id
        con.execute(query_trip)
        trip = con.fetchall()
        errors = ""
        if str(trip[0][0]) != currentUser:
            errors += "Only creator of the trip can remove it."
        if len(errors) == 0:
            query_delete_schreiben = "delete from schreiben where fahrt = " + id
            con.execute(query_delete_schreiben)
            query_delete_ratings = "delete from bewertung where beid in (select bewertung from schreiben where fahrt = " + id + ")"
            con.execute(query_delete_ratings)
            query_delete_reservations = "delete from reservieren where fahrt = " + id
            con.execute(query_delete_reservations)
            query_delete_reservations = "delete from fahrt where fid = " + id
            con.execute(query_delete_reservations)
            return redirect(url_for('viewMain'))
        else:

            con.close()
            return redirect(url_for('viewDrive', id=id, errors=errors))
    except Exception as e:
        con.rollBack()
        con.close()
        return render_template(redirect('viewMain'))

@app.route('/newRating/<id>', methods=['GET'])
def newRatingGet(id):
    try:
        return render_template('new_rating.html', id=id, errors="")
    except Exception as e:
        return render_template(redirect('viewMain'))


@app.route('/newRating/<id>', methods=['POST'])
def newRatingPost(id):
    conn = connect.DBUtil().getExternalConnection()
    con = conn.cursor()
    try:
        text = request.form.get('text')
        rating = request.form.get('rating')

        query_already_rated = "select benutzer from schreiben where fahrt = " + id + " and benutzer = " + currentUser
        con.execute(query_already_rated)
        already_rated = con.fetchall()
        errors = ""
        if len(already_rated) > 0:
            errors += "You already have rated this trip."
            return render_template('new_rating.html', id=id, errors=errors)


        query_new_rating = "insert into bewertung(textnachricht, erstellungsdatum , rating ) values (  clob('"+text+"' ),current date, "+str(rating)+")"
        con.execute(query_new_rating)
        query_last_id = "select sysibm.identity_val_local() as id from bewertung"
        con.execute(query_last_id)
        last_id = int(con.fetchone()[0])
        query_insert_schreiben = "insert into schreiben (benutzer ,fahrt ,bewertung) values (?, ?, ?)"
        con.execute(query_insert_schreiben, (currentUser, id, last_id))
        return redirect(url_for('viewMain'))

    except Exception as e:
        con.rollBack()
        con.close()
        return render_template(redirect('viewMain'))


@app.route('/viewSearch', methods=['GET'])
def viewSearchGet():
    try:
        return render_template('view_search.html', data=[])
    except Exception as e:
        return render_template(redirect('viewMain'))


@app.route('/viewSearch', methods=['POST'])
def viewSearchPost():
    conn = connect.DBUtil().getExternalConnection()
    con = conn.cursor()
    try:
        start = request.form.get('start')
        end = request.form.get('end')
        date = request.form.get('date')

        query_search = "select fid, startort, zielort, transportmittel, fahrtkosten from fahrt where (upper(startort) like upper(\'%" + start + "%\') or upper(zielort) like upper(\'%" + end + "%\')) and year(fahrtdatumzeit) = year(\'" + date + "\') and month(fahrtdatumzeit) = month(\'" + date + "\') and day(fahrtdatumzeit) = day(\'" + date + "\')"
        con.execute(query_search)
        results = con.fetchall()
        return render_template('view_search.html', data=results)

    except Exception as e:
        con.rollBack()
        con.close()
        return render_template(redirect('viewMain'))


if __name__ == "__main__":
    port = int("9" + re.match(r"([a-z]+)([0-9]+)", config["username"], re.I).groups()[1])
    app.run(host='0.0.0.0', port=port, debug=True)
