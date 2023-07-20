import flask
import json
from beat_detection import BeatDetection
from ola_thread import OlaThread
from serial_thread import SerialThread

class App():
    def __init__(self) -> None:


        with open('programs.json', 'r') as file:
            self.categories = json.load(file)["categories"]

        self.set_selected_program(0, 0)
        self.current_program_id = None
 
        self.ola_thread = OlaThread(self)
        self.beat_detection = BeatDetection(self.ola_thread.dmx_controller.on_beat, self.ola_thread.dmx_controller.on_start_blank, self.ola_thread.dmx_controller.on_stop_blank)
        self.serial_thread = SerialThread(self)

    def set_selected_program(self, category_id, program_id):
        self.selected_category_id = int(category_id)
        self.selected_program_id = int(program_id)
        
        self.selected_category = self.categories[self.selected_category_id]
        self.selected_program = self.selected_category['programs'][self.selected_program_id]

        print("NEW PROGRAM SELECTED: " + self.selected_program["name"])

    def run(self):
        self.ola_thread.start()
        self.beat_detection.start()
        self.serial_thread.start()

        
"""@app.flask_app.route('/get_categories', methods=['GET'])
def get_categories():
    filename = 'programs.json'
    return flask.send_file(filename, mimetype='application/json')

@app.flask_app.route('/set_program', methods=['GET'])
def set_program():
    category_id = flask.request.args.get('category_id')
    program_id = flask.request.args.get('program_id')
    app.set_selected_program(category_id, program_id)
    app.ola_thread.dmx_controller.on_new_program_selected()
    return "New program selected"

@app.flask_app.route('/start_strob', methods=['GET'])
def start_strob():
    app.ola_thread.dmx_controller.start_strob()
    return "Start Strob"

@app.flask_app.route('/stop_strob', methods=['GET'])
def stop_strob():
    app.ola_thread.dmx_controller.stop_strob()
    return "Stop Strob"

@app.flask_app.route('/resume_program', methods=['GET'])
def resume_program():
    app.ola_thread.dmx_controller.manual_program_paused = False
    app.ola_thread.dmx_controller.resume_program()
    return "Resume Program"

@app.flask_app.route('/pause_program', methods=['GET'])
def pause_program():
    app.ola_thread.dmx_controller.manual_program_paused = True
    app.ola_thread.dmx_controller.pause_program()
    return "Pause Program"""""

if __name__ == '__main__':
    app = App()
    app.run()