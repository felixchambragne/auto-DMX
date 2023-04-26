import smbus
import time
import csv

bus = smbus.SMBus(1)

def read_pcf8591():
    bus.write_byte(0x48, 0x40)
    return bus.read_byte(0x48)

values = []
timestamps = []

# Set the duration of the data collection
duration = 10 # seconds

start_time = time.time()

# Collect data for the specified duration
while time.time() - start_time < duration:
    value = read_pcf8591()
    timestamp = time.time()
    values.append(value)
    timestamps.append(timestamp)
    time.sleep(0.05)

# Save the data to a CSV file
with open('data.csv', 'w') as f:
    writer = csv.writer(f)
    writer.writerow(['timestamp', 'value'])
    for i in range(len(values)):
        writer.writerow([timestamps[i], values[i]])

