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
        selected_str = request.form['time']
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
        conn.commit()
        conn.close()
        return redirect(url_for('index'))

    return render_template('select_time.html', name=name)

@app.route('/timetable')
def timetable():
    # 데이터를 딕셔너리로 구조화: {(day, hour): [name1, name2, ...]}
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT name, day, hour FROM availability")
    raw_data = c.fetchall()
    conn.close()

    table_data = {}  # (day, hour) → [names]
    for name, day, hour in raw_data:
        key = (day, int(hour))
        if key not in table_data:
            table_data[key] = []
        table_data[key].append(name)

    return render_template('timetable.html', table_data=table_data)

@app.route('/reset', methods=['POST'])
def reset_timetable():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM availability")
    conn.commit()
    conn.close()
    return redirect(url_for('timetable'))

