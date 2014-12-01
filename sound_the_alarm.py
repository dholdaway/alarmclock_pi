#!/bin/python
# -*- coding: utf-8 -*-
import ConfigParser
import subprocess
import time
import textwrap
import better_spoken_numbers as bsn

Config=ConfigParser.ConfigParser()
try:
  Config.read('alarm.config')
except:
  raise Exception('Sorry, Failed reading alarm.config file.')

wadparts=[]

for section in Config.sections():
  if section != 'main' and Config.get(section,'enabled')==str(1):
    try:
      wadparts.append(getattr(__import__('get_'+section, fromlist=[section]),section))
    except ImportError:
      raise ImportError('Failed to load '+section)

count = 1



# key to getting text to speech
head = Config.get('main','head')+" "
tail = Config.get('main','tail')

day_of_month=str(bsn.d2w(int(time.strftime("%d"))))

now = time.strftime("%A %B ") + day_of_month + ',' + time.strftime(" %I %M %p")
# print now


if int(time.strftime("%H")) < 12:
  period = 'morning'
if int(time.strftime("%H")) >= 12:
  period = 'afternoon'
if int(time.strftime("%H")) >= 17:
  period = 'evening'

#print time.strftime("%H")
#print period

# reads out good morning + my name
gmt = 'Good ' + period + ', '

# reads date and time (sorry for the no apostrophe in it's)
day = ' its ' + now + '.  '

# Turn all of the parts into a single string
wad = (gmt + Config.get('main','name') + day + ''.join(str(x) for x in wadparts) + Config.get('main','end'))

if Config.get('main','debug') == str(1):
  print wad

if Config.get('main','readaloud') == str(1):
  # strip any quotation marks
  wad = wad.replace('"', '').replace("'",'').strip()

  if Config.get('main','trygoogle') == str(1):
    # Google voice only accepts 100 characters or less, so split into chunks
    shorts = []
    for chunk in wad.split('.  '):
      shorts.extend(textwrap.wrap(chunk, 100))


    # Send shorts to Google and return mp3s
    try:
      for sentence in shorts:
        sendthis = sentence.join(['"http://translate.google.com/translate_tts?tl=en&q=', '" -O /mnt/ram/'])
        print(head + sendthis + str(count).zfill(2) + str(tail))
        print subprocess.check_output (head + sendthis + str(count).zfill(2) + str(tail), shell=True)
        count = count + 1

      # Play the mp3s returned
      print subprocess.call ('mpg123 -h 10 -d 11 /mnt/ram/*.mp3', shell=True)

    # festival is now called in case of error reaching Google
    except subprocess.CalledProcessError:
      print subprocess.check_output("echo " + wad + " | festival --tts ", shell=True)
  
    # Cleanup any mp3 files created in this directory.
    print 'cleaning up now'
    print subprocess.call ('rm /mnt/ram/*.mp3', shell=True)
  else:
    print subprocess.check_output("echo " + wad + " | festival --tts ", shell=True)
else:
  print wad
