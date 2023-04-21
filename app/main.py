from ola.ClientWrapper import ClientWrapper
import flask
from controller import Controller
from user_interface import UserInterface

class App():
    def __init__(self) -> None:
        self.flask_app = flask.Flask(__name__)

    def run(self):
        self.flask_app.run(port=80, debug=True)
        self.user_interface = UserInterface()
        wrapper = ClientWrapper()
        self.controller = Controller(wrapper)
        wrapper.Run()

app = App()
@app.flask_app.route("/")
def categories_page():
    return flask.render_template('categories.html')

if __name__ == '__main__':
    app.run()