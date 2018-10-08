#!flask/bin/python
import six
import sys
import re
import urllib
import json
import time
from flask import Flask, jsonify, abort, request, make_response, url_for
from flask_httpauth import HTTPBasicAuth
from num2words import num2words
from itertools import chain
from datetime import timedelta
from chatbot import ChatbotSimulator
import requests
import json
import datetime
import base64



app = Flask(__name__)


@app.errorhandler(400)
def bad_request(error):
    return make_response(jsonify({'error': 'Bad request'}), 400)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Please, set the values.'}), 404)


@app.route('/chatbot-demo/api/v1/section=<int:section>&message=<string:message>&input_value=<int:input_value>&retry=<int:retry>&record=<string:record>', methods=['GET'])
def get_task(section, message, input_value, retry, record):
    cb = ChatbotSimulator(section, message, input_value, retry, record)
    return jsonify(cb.chatbot_response()) 


if __name__ == '__main__':
    app.run(debug=True)
