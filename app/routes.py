from flask import Flask, render_template, request, redirect, url_for
import os
import sqlite3

app = Flask(__name__)
DB_PATH = 'timetable.db'

# DB 초기화
def init_db():
    if not os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''CREATE TABLE availability (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        day TEXT NOT NULL,
                        hour INTEGER NOT NULL)''')
        conn.commit()
        conn.close()

init_db()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        name = request.form['name']
        return redirect(url_for('select_time', name=name))
    return render_template('index.html')

@app.route('/select-time/<name>', methods=['GET', 'POST'])
def select_time(name):
    if request.method == 'POST':
        selected_str = request.form['time']  # ex: "Mon-10,Tue-12,Wed-15"
        selected = [item for item in selected_str.split(',') if '-' in item]

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        for item in selected:
            try:
                day, hour = item.split('-')
                c.execute("INSERT INTO availability (name, day, hour) VALUES (?, ?, ?)",
                          (name, day, int(hour)))
            except Exception as e:
                print("Error with:", item, e)
                continue
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    return render_template('select_time.html', name=name)


@app.route('/timetable')
def timetable():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT name, day, hour FROM availability")
    data = c.fetchall()
    conn.close()
    return render_template('timetable.html', data=data)
