import threading
import serial

class SerialThread(threading.Thread):
    def __init__(self, app):
        threading.Thread.__init__(self)
        self.app = app

        self.ser = serial.Serial('/dev/USB0', 9600)

    def send_serial(self, data:str):
        self.ser.write(data.encode())

    def receive_serial(self):
        return self.ser.readline().decode().strip()

    def run(self):
        print("Serial thread started")
        self.send_serial("Hello from Raspberry Pi!")
        while True:
            received_data = self.receive_serial()
            if received_data == "BUTTON_PRESSED":
                print("Received data:", received_data)

