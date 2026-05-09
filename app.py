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

@app.route('/')
def index():
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

    # Totals logic
    total_chandlo = sum(int(item['chandlo'] or 0) for item in records)
    total_vasan = sum(int(item['vasan'] or 0) for item in records)
    total_anya = sum(int(item['anya'] or 0) for item in records)

    return render_template('index.html', 
                           records=records, 
                           filters=request.args,
                           t_chandlo=total_chandlo,
                           t_vasan=total_vasan,
                           t_anya=total_anya)

@app.route('/add-page')
def add_page():
    return render_template('add_data.html')

@app.route('/edit/<name>')
def edit_page(name):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM info WHERE fullname = %s", (name,))
    record = cursor.fetchone()
    conn.close()
    return render_template('edit.html', record=record)

@app.route('/update/<old_name>', methods=['POST'])
def update_record(old_name):
    fullname = request.form.get('fullname')
    prasang = request.form.get('prasang')
    pname = request.form.get('pname')
    tarikh = request.form.get('tarikh')
    chandlo = request.form.get('chandlo') or 0
    vasan = request.form.get('vasan') or 0
    anya = request.form.get('anya') or 0
    notru = request.form.get('notru')
    gone = request.form.get('gone')
    city = request.form.get('city')

    conn = get_db_connection()
    cursor = conn.cursor()
    sql = """UPDATE info SET 
             fullname=%s, prasang=%s, pname=%s, tarikh=%s, 
             chandlo=%s, vasan=%s, anya=%s, notru=%s, gone=%s, city=%s 
             WHERE fullname=%s"""
    
    cursor.execute(sql, (fullname, prasang, pname, tarikh, chandlo, vasan, anya, notru, gone, city, old_name))
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

@app.route('/save', methods=['POST'])
def save():
    data = (
        request.form.get('prasang'),
        request.form.get('fullname'),
        request.form.get('pname'),
        request.form.get('tarikh'),
        request.form.get('chandlo') or 0,
        request.form.get('vasan') or 0,
        request.form.get('anya') or 0,
        request.form.get('notru'),
        request.form.get('gone'),
        request.form.get('city')
    )
    conn = get_db_connection()
    cursor = conn.cursor()
    # Ensure column order matches your DB
    sql = "INSERT INTO info (prasang, fullname, pname, tarikh, chandlo, vasan, anya, notru, gone, city) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    cursor.execute(sql, data)
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

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

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)