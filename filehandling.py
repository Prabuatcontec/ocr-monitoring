import sys
import pytesseract
import argparse
import cv2
import tkinter
import re
from PIL import Image, ImageTk
from pyzbar import pyzbar
from flask import session
import json
import calendar
import time
from mysql import Connection
from modelunitvalidation import ModelValidation
from config import Config
import os.path
from os import path

ds_factor = 0.6


class HoldStatus(object):
    def __init__(self, user):
        self.user = user

    def writeFile(self, val, name):
        file = open(Config.UPLOAD_FOLDER + str(self.user) + name + ".txt", "w")
        file.write(val)
        file.close()

    def readFile(self, name):
        file = open(Config.UPLOAD_FOLDER+str(self.user) +
                    str(name) + ".txt", "r")
        r = file.read()
        file.close()
        return r
