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
import os.path
ds_factor = 0.6

os.environ['OMP_THREAD_LIMIT'] = '1'
class ImageProcess(object):
    def readData(self):
        with open("static/uploads/_serial.txt", 'r') as t:
            for i,line in enumerate(t):
                    if(int(HoldStatus("").readFile("_serialrowcount")) < i):
                        HoldStatus("").writeFile(str(i), "_serialrowcount")
                        print('line=',str(i))
                        data = line
                        line = line.replace('"', '')         # i == n-1 for nth line
                        line = line.replace('[', '')
                        line = line.replace(']', '')
                        line = line.split(',')
                        if os.path.isfile("static/uploads/boxER_"+line[0]+".jpg"):
                            image = cv2.imread("static/uploads/boxER_"+line[0]+".jpg")
                            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                            #print ("ffff")
                            text = pytesseract.image_to_string(Image.fromarray(gray))
                            validation = open("static/uploads/_validation.txt", 'r').read()
                            strVal = str(validation)
                            models = json.loads(strVal)
                            #print(text.encode('utf-8'))
                            valid = '1'
                            for key, value in models.items():
                                if key.replace('"', "") in text:
                                    #print(key)
                                    model = key
                                    valid = str(value).replace("'",'"')
                                    jsonArray =json.loads(str(valid))
                                    count = 0
                                    
                                    line.pop(0) 
                                    valid = ModelValidation().validate(
                                        jsonArray["data"], line)
                                    if valid == '0':
                                        line.insert(0,str(model))
                                        print('valid')
                                        file1 = open("static/uploads/_goodData.txt", "a")  
                                        file1.write("\n")
                                        file1.write(str(line))
                                    else:
                                        print('invalid')
                                        
                                        
                                    break
                                elif key.replace('"', "") not in text:
                                    continue
            

            return 1
