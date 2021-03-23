from flask import Blueprint, render_template, request, Response, session, Flask, jsonify
from mysql import Connection
from filehandling import HoldStatus
from camera import VideoCamera
from requests.auth import HTTPBasicAuth
import requests
from config import Config
import json

routes_blueprint = Blueprint('routes', __name__,)


@routes_blueprint.route("")
def index():
  return render_template("index.html", error="")


@routes_blueprint.route("/receiving", methods=['GET', "POST"])
def receiving():
  if request.method == 'POST':
    response = requests.post(
      Config.API_USER_URL + 'users/login', data=json.dumps({"username": request.form['username'], "password": request.form['password'], "Site": "Matamoros"}),
      headers={'Content-Type': 'application/json'}
    )
    if response.status_code != 200:
      return render_template("index.html", error="Authentication Failed!")
    a = response.json()
    session['user'] = a['user']['userName']

    response = requests.get(
        Config.API_URL + 'customers',
        headers={'Content-Type': 'application/json'}
    )
    a = response.json()
    HoldStatus("0").writeFile("0", "_update")
    HoldStatus("").writeFile("","_validation")
    return render_template("receiving.html", customers=a['results'], user=session['user'])
  if request.method == 'GET':
    response = requests.get(
        Config.API_URL + 'customers',
        headers={'Content-Type': 'application/json'}
    )
    a = response.json()
    HoldStatus("0").writeFile("0", "_update")
    HoldStatus("").writeFile("","_validation")
    return render_template("receiving.html",customers=a['results'], user=session['user'])
