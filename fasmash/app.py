from flask import Flask, render_template, send_from_directory, request, redirect
import os
import random

app = Flask(__name__)

# مسیر پوشه static (سازگار با Render و ویندوز)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_FOLDER = os.path.join(BASE_DIR, "static")

# ذخیره امتیاز عکس‌ها
scores = {}

@app.route("/")
def home():
    # اگر پوشه static وجود نداشت
    if not os.path.exists(IMAGE_FOLDER):
        return f"Folder not found: {IMAGE_FOLDER}"

    images = [
        img for img in os.listdir(IMAGE_FOLDER)
        if img.lower().endswith((".jpg", ".jpeg", ".png"))
    ]

    if len(images) < 2:
        return "حداقل دو عکس داخل پوشه static قرار بده."

    img1, img2 = random.sample(images, 2)

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
    print("Loser
