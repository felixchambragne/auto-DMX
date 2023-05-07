import RPi.GPIO as GPIO


GPIO.setmode(GPIO.BOARD)
pin = 4

GPIO.setup(pin, GPIO.IN)

while True:
    state = GPIO.input(pin)
    print(state)


