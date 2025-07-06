import os
import time
import cv2
import numpy as np
from flask import Flask, render_template, request
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/analyze", methods=["POST"])
def analyze():
    file = request.files['screenshot']
    if file:
        filename = secure_filename(file.filename)
        path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(path)
        time.sleep(5)
        signal = analyze_candle(path)
        return render_template("index.html", signal=signal)
    return render_template("index.html", signal="Error: No file.")

def analyze_candle(image_path):
    img = cv2.imread(image_path)
    if img is None:
        return "Unable to read image."

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    body_detected = False
    tall_candle_detected = False
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        if h > 50 and w < 20:
            tall_candle_detected = True
        if h > 20 and w > 10:
            body_detected = True

    if tall_candle_detected and body_detected:
        return "PUT"
    elif tall_candle_detected:
        return "CALL"
    else:
        return "No strong signal detected."

if __name__ == "__main__":
    app.run(debug=True)
