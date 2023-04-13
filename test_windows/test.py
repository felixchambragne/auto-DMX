from test_windows.DMXClient import DMXClient
import time

dmxClient = DMXClient("PODU")
dmxClient.connect()
for i in range(200):
    dmxClient.write({'2':i})
    print(i)
    time.sleep(1)

dmxClient.close()