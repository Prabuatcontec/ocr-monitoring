import jyserver.Flask as jsf
from flask import Flask, flash, render_template, request, Response, session
from werkzeug import secure_filename
from requests.auth import HTTPBasicAuth
import os
import sys
import pytesseract
import argparse
import cv2
import re
import time
import calendar
from PIL import Image, ImageTk
from camera import VideoCamera
from image import ImageProcess
import requests
import json
from api import api_blueprint
from routes import routes_blueprint
from mysql import Connection
from selenium import webdriver
from config import Config
from filehandling import HoldStatus
import threading
import face_recognition
import pickle
__author__ = 'Prabu <mprabu@gocontec.com>'
__source__ = ''
encodeListKnown = "global"
app = Flask(__name__)

app.register_blueprint(api_blueprint, url_prefix='/api')
app.register_blueprint(routes_blueprint, url_prefix='/')

# global camera
# camera = VideoCamera()
@jsf.use(app)
class App:
    def __init__(self):
        self.count = 5

    def increment(self):
        r = HoldStatus(self.js.document.getElementById(
            "user").innerHTML).readFile("_scan")
        if r == "1":
            self.js.document.getElementById("on_status").style.display = "none"
            self.js.document.getElementById(
                "off_status").style.display = "block"
        else:
            self.js.document.getElementById(
                "on_status").style.display = "block"
            self.js.document.getElementById(
                "off_status").style.display = "none"

        r = HoldStatus("").readFile("_serial")
        self.js.document.getElementById("dc_").innerHTML = r

#background process happening without any refreshing
@app.route('/background_process_enable/<string:val>')
def background_process_enable(val):
    HoldStatus("0").writeFile(val,"_update")
    return ('{"nothing":1}')


@app.route('/video_feed/<string:user>')
def video_feed(user):
    return Response(gen( VideoCamera(), user),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


def gen(camera, user):
    while True:
        frame = camera.getMotion(user)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame[0] + b'\r\n\r\n')


@app.route("/video", methods=['POST','GET'])
def ocr():
    # del camera
    # camera = VideoCamera()
    path = "employee"
    images = []
    classNames = []
    myList = os.listdir(path)
    for cl in myList:
        curImg = cv2.imread(f'{path}/{cl}')
        images.append(curImg)
        classNames.append(os.path.splitext(cl)[0])

    all_face_encodings = []
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        all_face_encodings.append(encode)

    with open('dataset_faces.dat', 'wb') as f:
        pickle.dump(all_face_encodings, f)

    with open('class_names.dat', 'wb') as f:
        pickle.dump(classNames, f)
    if request.method == 'GET':
        HoldStatus("").writeFile("-", "_serial")
        HoldStatus(session['user']).writeFile("0", "_scan")
        HoldStatus("").writeFile("0", "_serialrowcount")
        HoldStatus("").writeFile("", "_goodData")
        dict = {}
        # run_func()
        # for value in Connection().getModels(request.form['customer']):
        #     mdict1 = {value[1]:value[2]}  
        #     dict.update(mdict1) 
        # HoldStatus("").writeFile(json.dumps(dict),"_validation")
        return App.render(render_template("ocr.html", user=session['user'] ))

@app.route("/logout", methods=['GET'])
def logout():
    session.clear()
    return App.render(render_template("index.html", error=""))

def maintenance():
    """ Background thread doing various maintenance tasks """
    readText = ImageProcess()
    while True:
        # do things...
        readText.readData()
        time.sleep(MAINTENANCE_INTERVAL)

if __name__ == '__main__':
    app.secret_key = 'A0Zr98j/3yX R~XHHER!jmN]LWX/,?RT'
    # t1 = threading.Thread(target=onoff, name='t1')
    # t1.start()

    MAINTENANCE_INTERVAL = .1

    threading.Thread(target=maintenance, daemon=True).start()
    app.run(host="0.0.0.0", port=5000, debug=True)
