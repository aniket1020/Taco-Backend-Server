import ResponseTemplates

from flask import Flask

app = Flask(__name__)


@app.route("/")
def main():
    return ResponseTemplates.getLandingPage()


@app.route("/help", methods=['GET'])
def taco_help():
    return ResponseTemplates.getHelp()


@app.route("/taco-request", methods=['POST'])
def taco_request():
    return "<p>Hello World</p>"


if __name__ == '__main__':
    app.run(debug=True)
