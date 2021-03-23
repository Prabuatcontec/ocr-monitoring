from flask import Blueprint, render_template, request, Response, session, Flask, jsonify
from mysql import Connection

api_blueprint = Blueprint('api', __name__,)


@api_blueprint.route('/customers')
def customers():
    responseBody = { "results": Connection().getCustomer() }
    return jsonify(responseBody), 200

@api_blueprint.route('/model/<m_id>')
def model(m_id):
    return jsonify(Connection().getModel(m_id)), 200

@api_blueprint.route('/serial/<m_id>/<s>')
def serial(m_id,s):
    return jsonify(Connection().insertModel(m_id, s)), 200

@api_blueprint.route('/customer/models/<customer_id>')
def models(customer_id):
    responseBody = { "results": Connection().getModels(customer_id) }
    return jsonify(responseBody), 200