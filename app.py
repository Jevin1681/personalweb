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

    # Calculate Totals
    total_chandlo = sum(item['chandlo'] for item in records if item['chandlo'])
    total_vasan = sum(item['vasan'] for item in records if item['vasan'])
    total_anya = sum(item['anya'] for item in records if item['anya'])

    return render_template('index.html', 
                           records=records, 
                           filters=request.args,
                           t_chandlo=total_chandlo,
                           t_vasan=total_vasan,
                           t_anya=total_anya)
    

@app.route('/add-page')
def add_page():
    return render_template('add_data.html')

@app.route('/save', methods=['POST'])
def save():
    # Database ke saare 10 columns yahan receive ho rahe hain
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
    sql = "INSERT INTO info VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    cursor.execute(sql, data)
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/profile/<name>')
def profile(name):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM info WHERE fullname = %s", (name,))
    person = cursor.fetchone()
    conn.close()
    return render_template('profile.html', person=person)


if __name__ == '__main__':
    # Render sets a PORT environment variable automatically
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)