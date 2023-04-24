from ola.ClientWrapper import ClientWrapper
import flask
import json
import threading
from dmx_controller import DmxController

class App():
    def __init__(self) -> None:
        self.flask_app = flask.Flask(__name__)

        with open('programs.json', 'r') as file:
            self.categories = json.load(file)["categories"]

        self.selected_category = 0
        self.selected_program_id = 0
        self.update_selected_program()
    
    def update_selected_program(self):
        self.selected_program = self.categories[self.selected_category]['programs'][self.selected_program_id]["steps"]

    def run(self):
        ola_thread = OlaThread(app)
        ola_thread.start()
        self.flask_app.run(host='0.0.0.0', debug=True)

class OlaThread(threading.Thread):
    def __init__(self, app):
        threading.Thread.__init__(self)
        self.app = app

    def run(self):
        wrapper = ClientWrapper()
        dmx_controller = DmxController(self.app, wrapper)
        wrapper.Run()

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