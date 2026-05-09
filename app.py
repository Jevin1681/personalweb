import os
from flask import Flask, render_template, request, redirect, url_for
import mysql.connector

app = Flask(__name__)

def get_db_connection():
    db_password = os.environ.get('DB_PASSWORD')
    return mysql.connector.connect(
        host="mysql-3217e234-jevinsachaniya.j.aivencloud.com",
        user="avnadmin",
        password=db_password,
        database="personalweb",
        port=17622,
        ssl_disabled=False
    )

@app.route('/', methods=['GET', 'HEAD'])
def index():
    if request.method == 'HEAD':
        return '', 200

    fullname_filter = request.args.get('fullname', '')
    city_filter = request.args.get('city', '')

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = "SELECT * FROM info WHERE 1=1"
    params = []
    if fullname_filter:
        query += " AND fullname LIKE %s"
        params.append(f"%{fullname_filter}%")
    if city_filter:
        query += " AND city LIKE %s"
        params.append(f"%{city_filter}%")

    cursor.execute(query, params)
    records = cursor.fetchall()
    conn.close()

    total_chandlo = 0
    total_vasan = 0
    total_anya = 0

    for item in records:
        try:
            val = item.get('chandlo')
            if val and str(val).strip().isdigit():
                total_chandlo += int(val)
        except (ValueError, TypeError):
            pass
        try:
            val = item.get('vasan')
            if val and str(val).strip().isdigit():
                total_vasan += int(val)
        except (ValueError, TypeError):
            pass
        try:
            val = item.get('anya')
            if val and str(val).strip().isdigit():
                total_anya += int(val)
        except (ValueError, TypeError):
            pass

    return render_template('index.html',
                           records=records,
                           filters=request.args,
                           t_chandlo=total_chandlo,
                           t_vasan=total_vasan,
                           t_anya=total_anya)

@app.route('/profile/<name>')
def profile(name):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM info WHERE fullname = %s", (name,))
    record = cursor.fetchone()
    conn.close()
    if record:
        return render_template('profile.html', record=record)
    return "User Not Found", 404

@app.route('/add-page')
def add_page():
    return render_template('add_data.html')

@app.route('/save', methods=['POST'])
def save_record():
    data = request.form
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO info (fullname, prasang, pname, tarikh, chandlo, vasan, anya, notru, gone, city) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
        (data['fullname'], data.get('prasang'), data.get('pname'), data.get('tarikh'),
         data.get('chandlo') or None, data.get('vasan') or None, data.get('anya') or None,
         data.get('notru'), data.get('gone'), data.get('city'))
    )
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/edit/<name>')
def edit_page(name):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM info WHERE fullname = %s", (name,))
    record = cursor.fetchone()
    conn.close()
    return render_template('edit.html', record=record)

@app.route('/update/<int:record_id>', methods=['POST'])
def update_record(record_id):
    data = request.form
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE info SET fullname=%s, prasang=%s, pname=%s, tarikh=%s, chandlo=%s, vasan=%s, anya=%s, notru=%s, gone=%s, city=%s WHERE id=%s",
        (data['fullname'], data.get('prasang'), data.get('pname'), data.get('tarikh'),
         data.get('chandlo') or None, data.get('vasan') or None, data.get('anya') or None,
         data.get('notru'), data.get('gone'), data.get('city'), record_id)
    )
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/delete/<name>')
def delete_record(name):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM info WHERE fullname = %s", (name,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))
