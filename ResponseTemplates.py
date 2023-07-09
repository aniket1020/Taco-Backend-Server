def getLandingPage():
    return """
    <!DOCTYPE html>
<html>
<head>
  <title>Welcome to My Server</title>
  <style>
    body {
      font-family: Arial, sans-serif;
      text-align: center;
      padding: 50px;
    }

    h1 {
      color: #333;
      font-size: 30px;
    }

    p {
      color: #666;
      font-size: 20px;
    }
  </style>
</head>
<body>
  <h1>This is a TACO web-server</h1>
  <p>Use the provided access-token to make requests on following API end-points</p>
  <br>
  <p>For starters checkout the '/help' page...</p>
</body>
</html>
    """


def getHelp():
    return """
    <p>Help page</p>
    """