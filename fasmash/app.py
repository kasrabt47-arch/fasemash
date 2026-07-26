from flask import Flask, render_template, request, redirect
import os
import random
import sqlite3
from datetime import datetime

app = Flask(__name__)
DB_NAME = "facemash.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS visitors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ip TEXT,
        browser TEXT,
        platform TEXT,
        visit_time TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS votes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        winner TEXT,
        loser TEXT,
        vote_time TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()
# مسیر پوشه static
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_FOLDER = os.path.join(BASE_DIR, "static")

# امتیاز عکس‌ها
scores = {}

# لیست بازدیدکننده‌ها
visitors = []

# تعداد کل بازدیدها
total_visits = 0


@app.route("/")
def home():

    global total_visits

    total_visits += 1

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    ip = request.remote_addr

    cursor.execute("SELECT id FROM visitors WHERE ip = ?", (ip,))
    exists = cursor.fetchone()

    if not exists:
        cursor.execute("""
            INSERT INTO visitors (ip, browser, platform, visit_time)
            VALUES (?, ?, ?, ?)
        """, (
            ip,
            str(request.user_agent.browser),
            str(request.user_agent.platform),
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))
        conn.commit()

    conn.close()

    return render_template(
        "index.html",
        img1=img1,
        img2=img2
    )


@app.route("/vote", methods=["POST"])
def vote():
    winner = request.form["winner"]
    loser = request.form["loser"]

    scores[winner] = scores.get(winner, 0) + 1
    scores[loser] = scores.get(loser, 0)

    print("Winner:", winner)
    print("Loser :", loser)

    # ذخیره رأی در دیتابیس
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO votes (winner, loser, vote_time)
        VALUES (?, ?, ?)
    """, (
        winner,
        loser,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    conn.commit()
    conn.close()

    return redirect("/")


@app.route("/admin")
def admin():

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # تعداد کل بازدیدها
    cursor.execute("SELECT COUNT(*) FROM visitors")
    total_visits = cursor.fetchone()[0]

    # تعداد کل رأی‌ها
    cursor.execute("SELECT COUNT(*) FROM votes")
    total_votes = cursor.fetchone()[0]

    # آخرین 50 بازدیدکننده
    cursor.execute("""
        SELECT DISTINCT ip, browser, platform, visit_time
        FROM visitors
        ORDER BY id DESC
    """)
    visitors = cursor.fetchall()

    # رتبه‌بندی عکس‌ها
    cursor.execute("""
        SELECT winner, COUNT(*) AS score
        FROM votes
        GROUP BY winner
        ORDER BY score DESC
    """)
    ranking = cursor.fetchall()

    conn.close()

    return render_template(
        "admin.html",
        total_visits=total_visits,
        total_votes=total_votes,
        visitors=visitors,
        ranking=ranking
    )

if __name__ == "__main__":
    app.run(debug=True)
