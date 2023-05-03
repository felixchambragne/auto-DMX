import pandas as pd
import matplotlib.pyplot as plt

# Read the CSV file
df = pd.read_csv('test_raspi/data2.csv')

# Extract the data from the DataFrame
timestamps = df['timestamp']
values = df['value']

# Plot the data
#plt.bar(timestamps, values)
plt.stem(timestamps, values, markerfmt=' ')
plt.xlabel('Time')
plt.ylabel('Value')
plt.savefig('plot2.png')

# Tracer le spectrogramme
fig, ax = plt.subplots(figsize=(8, 4))
spec = ax.specgram(values, Fs=1000, NFFT=1024, noverlap=512, mode='magnitude', scale='dB')

# Ajuster l'échelle logarithmique pour l'axe des fréquences
ax.set_yscale('log')

# Ajouter une étiquette pour l'axe des fréquences
ax.set_ylabel('Frequency [Hz]')

# Afficher le spectrogramme
plt.show()