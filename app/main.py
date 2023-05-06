import flask
import json
from beat_detection import BeatDetection
from ola_thread import OlaThread

class App():
    def __init__(self) -> None:
        self.flask_app = flask.Flask(__name__)

        with open('programs.json', 'r') as file:
            self.categories = json.load(file)["categories"]

        self.update_current_category(0)
        self.update_current_program(0)

        self.ola_thread = OlaThread(self)
        self.beat_detection = BeatDetection(self.ola_thread.on_beat)

    def update_current_category(self, id):
        self.current_category = self.categories[id]

    def update_current_program(self, id):
        self.current_program = self.current_category['programs'][id]

    def run(self):
        self.ola_thread.start()
        self.beat_detection.start()
        self.flask_app.run(host='0.0.0.0', debug=True)

app = App()
@app.flask_app.route("/", methods=["GET", "POST"])
def categories_page():
    return flask.render_template(
        'categories.html',
        categories=app.categories,
        selected_category = app.selected_category
    )

@app.flask_app.route("/test", methods=["GET", "POST"])
def test():
    return flask.render_template_string("<h1>Test</h1>")

if __name__ == '__main__':
    app.run()