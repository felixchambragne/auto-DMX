from __future__ import print_function
import array
import sys
from ola.ClientWrapper import ClientWrapper

wrapper = None

def DmxSent(status):
  if status.Succeeded():
    print('Success!')
  else:
    print('Error: %s' % status.message, file=sys.stderr)

  global wrapper
  if wrapper:
    wrapper.Stop()

def main():
  universe = 1
  data = array.array('B')
  # append first dmx-value
  data.append(10)
  # append second dmx-value
  data.append(50)
  # append third dmx-value
  data.append(255)

  global wrapper
  wrapper = ClientWrapper()
  client = wrapper.Client()
  # send 1 dmx frame with values for channels 1-3
  client.SendDmx(universe, data, DmxSent)
  wrapper.Run()


if __name__ == '__main__':
  main()