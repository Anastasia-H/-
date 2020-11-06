from gevent.pywsgi import WSGIServer
from flask import Flask
app = Flask(__name__)

@app.route('/api/v1/hello-world-5')
def hello_world():
    return 'Hello World 5'

server = WSGIServer(('127.0.0.1',5000),app)
server.serve_forever()
