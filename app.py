from Utility import ResponseTemplates
from flask import Flask, request
from TacoLLM import RequestHandler, ContextInitializer

app = Flask(__name__)


@app.route("/")
def main():
    return ResponseTemplates.getLandingPage()


@app.route("/help", methods=['GET'])
def taco_help():
    return ResponseTemplates.getHelp()


@app.route("/taco-request", methods=['POST'])
def taco_request():
    inputQuery = request.form.get("message")
    return RequestHandler.handleRequest(inputQuery)


if __name__ == '__main__':
    # Initialize chromadb collection
    # ContextInitializer.initializeContext()
    app.run()
