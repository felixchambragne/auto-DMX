import RPi.GPIO as GPIO


GPIO.setmode(GPIO.BOARD)
pin = 7

GPIO.setup(pin, GPIO.IN)

while True:
    state = GPIO.input(pin)
    if state == 0:
        print("Low                     ", end="\r")
    else:
        print("High ----------------", end="\r")



