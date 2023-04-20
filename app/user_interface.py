import flask

app = flask.Flask(__name__)

@app.flask_app.route("/")
def home_page():
    return flask.render_template('index.html')

if __name__ == "__main__":
    app.run(port=80, debug=True)