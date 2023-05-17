import flask
import json
from beat_detection import BeatDetection
from ola_thread import OlaThread

class App():
    def __init__(self) -> None:
        self.flask_app = flask.Flask(__name__)

        with open('programs.json', 'r') as file:
            self.categories = json.load(file)["categories"]

        self.set_selected_program(0, 0)
        self.current_category = None
        self.current_category_id = None
        self.current_program_id = None
 
        self.ola_thread = OlaThread(self)
        self.beat_detection = BeatDetection(self.ola_thread.dmx_controller.on_beat)

    def set_current_category(self, category_id):
        self.current_category_id = int(category_id)
        self.current_category = self.categories[self.current_category_id]

    def set_selected_program(self, category_id, program_id):
        self.selected_category_id = int(category_id)
        self.selected_program_id = int(program_id)
        
        self.selected_category = self.categories[self.selected_category_id]
        self.selected_program = self.selected_category['programs'][self.selected_program_id]
        print("NEW PROGRAM SELECTED: " + self.selected_program["name"])
        

    def run(self):
        self.ola_thread.start()
        self.beat_detection.start()
        self.flask_app.run(host='0.0.0.0')

app = App()
@app.flask_app.route("/", methods=["GET", "POST"])
def categories_page():
    if flask.request.method == "POST":
        app.set_current_category(flask.request.form['category_id'])
        return flask.redirect(flask.url_for('programs_page'))
    
    return flask.render_template(
        'categories.html',
        categories=app.categories,
        selected_category_id = app.selected_category_id
    )

@app.flask_app.route("/programs", methods=["GET", "POST"])
def programs_page():
    
    if app.current_category == None:
        return flask.redirect(flask.url_for('categories_page'))

    if flask.request.method == "POST":
        app.set_selected_program(app.current_category_id, flask.request.form['program_id'])
        app.ola_thread.dmx_controller.update_current_step()

    if app.current_category == app.selected_category:
        app.current_program_id = app.selected_program_id
    else:
        app.current_program_id = None

    return flask.render_template(
        'programs.html',
        programs = app.current_category['programs'],
        selected_program_id = app.current_program_id
    )

if __name__ == '__main__':
    app.run()