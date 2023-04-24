from ola.ClientWrapper import ClientWrapper
import flask
import json
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
        
        self.wrapper = ClientWrapper()
        self.dmx_controller = DmxController(self, self.wrapper)
        self.wrapper.Run()
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