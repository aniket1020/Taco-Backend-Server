import os

from dotenv import load_dotenv
from Utility import ResponseTemplates
from flask import Flask, request
from TacoLLM import RequestHandler
from Utility.AthenticationToken import require_token

app = Flask(__name__)
load_dotenv()


@app.route("/")
def main():
    return ResponseTemplates.getLandingPage()


@app.route("/help", methods=['GET'])
def taco_help():
    return ResponseTemplates.getHelp()


@app.route("/taco-request", methods=['POST'])
@require_token
def taco_request():
    inputQuery = request.form.get("message")
    return RequestHandler.handleRequest(inputQuery)


if __name__ == '__main__':
    app.run()
