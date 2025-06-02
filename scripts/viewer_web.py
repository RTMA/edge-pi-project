import flask
import time
import os
from logger_setup import setup_logger

logger = setup_logger()

DEBUG_FOLDER = os.path.abspath("../debug")

logger.info("DEBUG_FOLDER: %s", DEBUG_FOLDER)

webapp = flask.Flask(__name__)

def get_latest_image(folder):
    try:
        files = sorted(
            [f for f in os.listdir(folder) if f.endswith(".jpg")],
            key=lambda x: os.path.getmtime(os.path.join(folder, x)),
            reverse=True
        )
        return os.path.join(folder, files[0]) if files else None
    except Exception as e:
        logger.error("Fout bij ophalen van afbeelding: %s", e)
        return None


@webapp.route("/video_feed")
def feed():
    def generate_frames():
        while True:
            latest = get_latest_image(DEBUG_FOLDER)
            if latest:
                with open(latest, 'rb') as f:
                    frame = f.read()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            time.sleep(0.1)
    return flask.Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@webapp.route("/")
def index():
    return flask.render_template_string("""
    <!doctype html>
    <html>
        <head>
            <title>Video Feed</title>
        </head>
        <body>
            <h1>Live Video Feed</h1>
            <img src='/video_feed' alt='Video Feed'>
        </body>
    </html>
    """
    )

if(__name__ == "__main__"):
    webapp.run(host="0.0.0.0", port=5050)
