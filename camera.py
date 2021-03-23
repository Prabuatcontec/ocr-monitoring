import os
import sys
import pytesseract
import argparse
import cv2
import numpy as np
import tkinter
import re
from PIL import Image, ImageTk, ImageEnhance
from pyzbar import pyzbar
from flask import session
import json
import calendar
import asyncio
import time
from mysql import Connection
from modelunitvalidation import ModelValidation
from filehandling import HoldStatus
import playsound
from scipy.ndimage import interpolation as inter
import math
import time
from requests.auth import HTTPBasicAuth
import requests
from config import Config
import random
import pandas
from datetime import datetime 
import pickle
ds_factor = 0.6
path = 'dataset'


import face_recognition

recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read('trainer/trainer.yml')
cascadePath = "haarcascade_frontalface_default.xml"
detector = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
faceCascade = cv2.CascadeClassifier(cascadePath)
font = cv2.FONT_HERSHEY_SIMPLEX

class VideoCamera(object):
    def __init__(self):
        self.video = cv2.VideoCapture(0)

    def __del__(self):
        self.video.release()

    def delCam(self):
        self.video.release()

    
    def Reverse(lst): 
        return [ele for ele in reversed(lst)] 

    def on_off(self, model):
        img = Image.open("static/img/off.png", mode='r')
        roi_img = img.crop(box)

        img_byte_arr = io.BytesIO()
        roi_img.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()
        return img_byte_arr

    def get_frame(self, user):
        success, image = self.video.read()
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        ret, jpeg = cv2.imencode('.jpg', image)
       
        gmt = time.gmtime()
        ts = calendar.timegm(gmt)
        barcodes = pyzbar.decode(image)
        start_time = time.time()

        if len(barcodes) > 0:
            text = pytesseract.image_to_string(Image.fromarray(gray))
            validation = self.read_data(user)
            strVal = str(validation)
            models = json.loads(strVal)
            text = text.replace('\n', ' ')
            
            counts = 0
            valid = 0
            model = ''
            valid = ''
            for key, value in models.items():
                if key.replace('"', "") in text:
                    model = key
                    valid = str(value).replace("'",'"')
                    jsonArray =json.loads(str(valid))
                    count = 0
                    serials = []
                    

                    for barcode in barcodes:
                        barcodeData = barcode.data.decode("utf-8")
                        serials.append(barcodeData)
                        count = count + 1
                    HoldStatus(user).writeFile(
                        json.dumps([ele for ele in reversed(serials)]), "_serial")

                    valid = ModelValidation().validate(
                        jsonArray["data"], [ele for ele in reversed(serials)])

                    if valid == '0':
                        cv2.imwrite("static/uploads/boxER_%d.jpg" % ts, image)
                    HoldStatus(user).writeFile(valid, "_scan")
                        
                    break
                elif key.replace('"', "") not in text:
                    continue
        # print("--- %s seconds ---" % (time.time() - start_time))
        return [jpeg.tobytes(), 0]

    def get_Singleframe(self, user):
        success, image = self.video.read()
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        ret, jpeg = cv2.imencode('.jpg', image)
       
        gmt = time.gmtime()
        ts = calendar.timegm(gmt)
        barcodes = pyzbar.decode(image)
        start_time = time.time()

        if len(barcodes) > 0:
            fillenameImage = str(str(ts)+'-'+str(random.randint(0,99999)))
            
            serials = []
                    
            for barcode in barcodes:
                barcodeData = barcode.data.decode("utf-8")
                serials.append(barcodeData)
            # validation = data = open("static/uploads/_validation.txt", 'r').read()
            # strVal = str(validation)
            # models = json.loads(strVal)
            # model = 'DMS2004UHD'
            # valid = '1'
            # for key, value in models.items():
            #     if key.replace('"', "") == model:
            #         valid = str(value).replace("'",'"')
            #         jsonArray =json.loads(str(valid))
            #         break
            #     else:
            #         continue
            
            # valid = ModelValidation().validate(
            #                     jsonArray["data"], [ele for ele in reversed(serials)])
            
            
            # if valid == '0':
            serials.append(fillenameImage)
            cv2.imwrite("static/uploads/boxER_%s.jpg" % fillenameImage, image)
            file1 = open("static/uploads/_serial.txt", "a")  
            file1.write("\n")
            file1.write(json.dumps([ele for ele in reversed(serials)]))
        return [jpeg.tobytes(), 0]

    def rotate(image, angle):
        # Obtain the dimensions of the image
        (height, width) = image.shape[:2]
        (cX, cY) = (width / 2, height / 2)

        # Grab the rotation components of the matrix
        matrix = cv2.getRotationMatrix2D((cX, cY), -angle, 1.0)
        cos = np.abs(matrix[0, 0])
        sin = np.abs(matrix[0, 1])

        # Find the new bounding dimensions of the image
        new_width = int((height * sin) + (width * cos))
        new_height = int((height * cos) + (width * sin))

        # Adjust the rotation matrix to take into account translation
        matrix[0, 2] += (new_width / 2) - cX
        matrix[1, 2] += (new_height / 2) - cY

        # Perform the actual rotation and return the image
        return cv2.warpAffine(image, matrix, (new_width, new_height))

 
    def get_ocr(self):
        count = 0
        while self.video.isOpened():
            ret, frame = self.video.read()
            img1 = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            text = pytesseract.image_to_string(Image.fromarray(img1))
            gmt = time.gmtime()
            ts = calendar.timegm(gmt)
            print("Extracted eeText: ", text)
            if ret:
                if text.upper().strip() != "":
                    cv2.imwrite("static/uploads/box_%d.jpg" %
                                ts, frame)     # save frame as JPEG file
                    count += 1
                else:
                    count = 0

            if cv2.waitKey(0) & 0xFF == ord('q'):
                break
            print("Extracted Text: ", text)
        return frame

    def getImagesAndLabels(self, path):
        imagePaths = [os.path.join(path,f) for f in os.listdir(path)]     
        faceSamples=[]
        ids = []

        for imagePath in imagePaths:

            PIL_img = Image.open(imagePath).convert('L') # convert it to grayscale
            img_numpy = np.array(PIL_img,'uint8')

            id = int(os.path.split(imagePath)[-1].split(".")[1])
            faces = detector.detectMultiScale(img_numpy)

            for (x,y,w,h) in faces:
                faceSamples.append(img_numpy[y:y+h,x:x+w])
                ids.append(id)

        return faceSamples,ids


    def getMotion(self, user):
        static_back = None
        motion_list = [ None, None ]
        time = []
        faceSamples=[]
        ids = []
        count = 0
        face_id = 3
        id = 1
        minW = 0.1*self.video.get(3)
        minH = 0.1*self.video.get(4)
        df = pandas.DataFrame(columns = ["Start", "End", "X", "Y","XW", "YH","touched"])
        # faces,ids = self.getImagesAndLabels(path)
        # recognizer.train(faces, np.array(ids))
        # recognizer.write('trainer/trainer.yml')
        # exit()
        names = ['Corona', 'Prabu', 'Prabu'] 
        
        with open('dataset_faces.dat', 'rb') as f:
	        encodeListKnown = pickle.load(f)

        with open('class_names.dat', 'rb') as f:
	        classNames = pickle.load(f)
        while True:
            check, frame = self.video.read()
            motion = 0
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.GaussianBlur(gray, (21, 21), 0)
            
            
            # imgS = cv2.resize(frame,(0,0), None, 0.25, 0.25)
            # imgS = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # facesCurFrame = face_recognition.face_locations(imgS)
            # encodeCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)

            # for encodeFace,faceLoc in zip(encodeCurFrame, facesCurFrame):
            #     matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
            #     faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
            #     matchIndex = np.argmin(faceDis)

            #     if matches[matchIndex]:
            #         name =  classNames[matchIndex].upper()
            #         y1,x2,y2,x1 = faceLoc
            #         cv2.rectangle(frame, (x1, y1), (x2, y2),(0,255,0), 2)
            #         cv2.rectangle(frame, (x1, y2-35), (x2, y2),(0,255,0), cv2.FILLED)
                    #cv2.rectangle(frame, name, (x1+6, y2-6),cv2.FONT_HERSHEY_SIMPLEX,1,(255,255,255), 2)

            if static_back is None:
                static_back = gray
                continue
            #----------------------------------------------

            
            # frame = cv2.flip(frame, -1) # Flip vertically
            # gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)

            # faces = faceCascade.detectMultiScale( 
            #     gray,
            #     scaleFactor = 1.2,
            #     minNeighbors = 5,
            #     minSize = (int(minW), int(minH)),
            # )
            # for(x,y,w,h) in faces:
            #     #cv2.rectangle(frame, (x,y), (x+w,y+h), (0,255,0), 2)
            #     id, confidence = recognizer.predict(gray[y:y+h,x:x+w])
            #     # Check if confidence is less them 100 ==> "0" is perfect match 
            #     print('facew--------------------------------------------------------------')
            #     if (confidence < 100):
            #         print(str(id))
            #         id = names[id]
            #         confidence = "  {0}%".format(round(100 - confidence))
            #     else:
            #         id = "Corana"
            #         confidence = "  {0}%".format(round(100 - confidence))
                
            #     #cv2.putText(frame, str(id), (x+5,y-5), font, 1, (255,255,255), 2)
            #     #cv2.putText(frame, str(confidence), (x+5,y+h-5), font, 1, (255,255,0), 1)  
            # #----------------------------------------------
            # img = cv2.flip(frame, -1) # flip video image vertically
            # gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            # faces = detector.detectMultiScale(gray, 1.3, 5)

            # for (x,y,w,h) in faces:

            #     cv2.rectangle(frame, (x,y), (x+w,y+h), (255,0,0), 2)     
            #     count += 1
            #     print('hauuu')
            #     # Save the captured image into the datasets folder
            #     cv2.imwrite("dataset/User." + str(face_id) + '.' + str(random.randint(0,99999)) + ".jpg", gray[y:y+h,x:x+w])
        
            diff_frame = cv2.absdiff(static_back, gray)
            thresh_frame = cv2.threshold(diff_frame, 30, 255, cv2.THRESH_BINARY)[1]
            thresh_frame = cv2.dilate(thresh_frame, None, iterations = 2)
            
            # Finding contour of moving object 
            (_, cnts, _) = cv2.findContours(thresh_frame.copy(),  
                            1, 2) 
            x = y = w = h = 1

            x = 0
            y = 130
            w = 110 
            h = 160
            cv2.rectangle(frame, (x, y), (x + w, y + h), (250, 255, 0), 3) 

            x = 130
            y = 0
            w = 110 
            h = 160
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 3) 
            for contour in cnts: 
                if cv2.contourArea(contour) < 100: 
                    continue
                motion = 1
        
                (x, y, w, h) = cv2.boundingRect(contour) 
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3) 
            ret, jpeg = cv2.imencode('.jpg', frame)
            # Appending status of motion 
            motion_list.append(motion) 
        
            motion_list = motion_list[-2:] 
        
            # Appending Start time of motion 
            if motion_list[-1] == 1 and motion_list[-2] == 0: 
                time.append(datetime.now()) 
        
            # Appending End time of motion 
            if motion_list[-1] == 0 and motion_list[-2] == 1: 
                time.append(datetime.now()) 
        
            # # Displaying image in gray_scale 
            # cv2.imshow("Gray Frame", gray) 
        
            # # Displaying the difference in currentframe to 
            # # the staticframe(very first_frame) 
            # cv2.imshow("Difference Frame", diff_frame) 
        
            # # Displaying the black and white image in which if 
            # # intensity difference greater than 30 it will appear white 
            # cv2.imshow("Threshold Frame", thresh_frame) 
        
            # # Displaying color frame with contour of motion of object 
            # cv2.imshow("Color Frame", frame) 
        
            # key = cv2.waitKey(1) 
            # # if q entered whole process will stop 
            # if key == ord('q'): 
            #     # if something is movingthen it append the end time of movement 
            #     if motion == 1: 
            #         time.append(datetime.now()) 
            #     break
            
            if motion == 1: 
                print(' action')
                time.append(datetime.now())
            else:
                print('no action')
            touched = '0'
            if ( ((x >= 0 and x < 111) or (y < 131 and y > 291))):
                touched = '1'
            if ( ((x >= 130 and x < 111) or (y > 0 and y > 291))):
                touched = '2'
                
            # Appending time of motion in DataFrame 
            for i in range(0, len(time), 2): 
                df = df.append({"Start":id, "End":time[i], "X": str(x), "Y": str(y), "XW": str(x + w), "YH": str(y + h),"touched": touched}, ignore_index = True)
                df.to_csv('Time_of_movements.csv',mode='a',header=False)
            
            # Creating a CSV file in which time of movements will be saved 
            
            return [jpeg.tobytes(), 0]
        
        
        return [jpeg.tobytes(), 0]
