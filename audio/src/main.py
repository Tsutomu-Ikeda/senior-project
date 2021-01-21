import json
import logging
import pathlib

import flask
import werkzeug.serving
from gevent.pywsgi import WSGIServer
from geventwebsocket.handler import WebSocketHandler

import constants
import utils

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)-8s %(message)s'
)


app = flask.Flask(__name__)


@app.route("/")
def top():
    return flask.redirect("/app")


@app.route('/gen_audio_ook', methods=['POST'])
def gen_audio_ook():
    if not (file := flask.request.files.get('file')):
        return "Bad Request", 400

    body = file.stream.read()
    print(len(body))
    if constants.LIMIT_BYTES < len(body):
        return f"ファイルサイズの上限を超えました。<br>{len(body)}バイト > {constants.LIMIT_BYTES}バイト", 400

    resp = flask.make_response(
        utils.create_wavedata(body)
    )
    resp.headers['Content-Type'] = "audio/wav"

    return resp


@app.route("/upload", methods=["POST"])
def handle_upload():
    file = flask.request.files['file']
    if file and file.filename.lower().endswith(".wav"):
        filename = file.filename
        file.save(pathlib.Path("./static/audio") / filename)
    return "OK"


@app.route('/pipe')
def pipe():
    ws = flask.request.environ['wsgi.websocket']

    if ws:
        is_mock = str(flask.request.args.get("is_mock")).lower() == 'true'
        data_type = flask.request.args.get("type")
        val_threshold = flask.request.args.get("threshold", default=40000, type=int)

        def set_size(size):
            ws.send(json.dumps({
                "size": size
            }))

        recorded = []

        def audio_callback(data):
            recorded.extend(data)

        for byte in utils.make_chunks(
            utils.get_bytes(
                utils.receive(ws, is_mock, data_type, audio_callback),
                val_threshold,
                set_size
            ),
            3 * 300,
            b""
        ):
            ws.send(b"".join(byte))

        if recorded:
            utils.save_audio_data(
                recorded
            )
        ws.close()

    return ""


@ app.route("/app")
def app_top():
    return flask.render_template('index.html')


@ app.route("/app/sender")
def app_sender():
    return flask.render_template('sender.html')


@ app.route("/app/receiver")
def app_receiver():
    return flask.render_template('receiver.html')


@ app.route("/app/dir")
def dirtree():
    path = pathlib.Path("./static/audio/")
    return flask.render_template('dirtree.html', tree=utils.make_tree(path))


@ werkzeug.serving.run_with_reloader
def runServer():
    app.debug = True
    http_server = WSGIServer(('', 8080), app, handler_class=WebSocketHandler)
    http_server.serve_forever()


if __name__ == "__main__":
    runServer()
