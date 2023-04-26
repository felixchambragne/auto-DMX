import pandas as pd
import matplotlib.pyplot as plt

# Read the CSV file
df = pd.read_csv('data.csv')

# Extract the data from the DataFrame
timestamps = df['timestamp']
values = df['value']

# Plot the data
plt.plot(timestamps, values)
plt.xlabel('Time')
plt.ylabel('Value')
plt.savefig('plot.png')
