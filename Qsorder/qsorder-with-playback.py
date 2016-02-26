#!/usr/bin/python

##################################################
# qsorder - A contest QSO recorder
# Title: qsorder.py
# Author: k3it
# Generated: Thu Jan 20 2013
# Version: 2.6b-replay
##################################################

# qsorder is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# qsorder is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import subprocess
import re
import pyaudio
import wave
import time
import sys
import struct
import threading
import string
import binascii
import pyhk
import copy

import datetime
import dateutil.parser

from optparse import OptionParser
from collections import deque
from socket import *
from xml.dom.minidom import parse, parseString

#CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
#RATE = 8000
BASENAME = "QSO"
#LO = 14000
#dqlength = 360 # number of chunks to store in the buffer
#DELAY = 20.0
#MYPORT=12060

usage = "usage: %prog [OPTION]..."
parser = OptionParser()
parser.add_option("-l", "--buffer-length", type="int", default=45,
                  help="Audio buffer length in secs [default=%default]")
parser.add_option("-d", "--delay", type="int", default=20, 
                  help="Capture x seconds after QSO log entry [default=%default]")
parser.add_option("-p", "--path", type="string", default=None,
                  help="Base directory for audio files [default=%default]")
parser.add_option("-P", "--port", type="int", default=12060,
                  help="UDP Port [default=%default]")
parser.add_option("-s", "--station-nr", type="int", default=None,
                  help="Network Station Number [default=%default]")
parser.add_option("-k", "--hot-key", type="string", default="O",
                  help="Hotkey for manual recording Ctrl-Alt-<hot_key> [default=%default]")
parser.add_option("-S", "--so2r", action="store_true", default=False,
		help="SO2R mode, downmix to mono: Left Ch - Radio1 QSOs, Right Ch - Radio2 QSOs [default=%default]")

parser.add_option("-C", "--chunk", type="int", default=1024,
                  help="Audio buffer chunk size [default=%default]")
parser.add_option("-R", "--sample-rate", type="int", default=8000,
                  help="Audio buffer chunk size [default=%default]")

(options,args) = parser.parse_args()

DELAY = options.delay
MYPORT = options.port
CHUNK = options.chunk
RATE = options.sample_rate
dqlength =  int (options.buffer_length * RATE / CHUNK) + 1

if (options.path):
	os.chdir(options.path)

if (len(options.hot_key) == 1):
	HOTKEY=options.hot_key.upper()
else:
	print "Hotkey should be a single character"
	parser.print_help()
	exit(-1)


class wave_file:
        """
        class definition for the WAV file object
        """
        def __init__(self,samp_rate,LO,BASENAME,qso_time,contest_dir):
                #starttime/endtime
                self.create_time=time.time()
                #now=datetime.datetime.utcnow()
                now=qso_time
                #finish=now + datetime.timedelta(seconds=duration)

                self.wavfile = BASENAME + "_"
                self.wavfile += str(now.year)
                self.wavfile += str(now.month).zfill(2)
                self.wavfile += str(now.day).zfill(2)
                self.wavfile += "_"
                self.wavfile += str(now.hour).zfill(2)
                self.wavfile += str(now.minute).zfill(2)
                self.wavfile += str(now.second).zfill(2)
                self.wavfile += "Z_"
                #self.wavfile += str(int(LO/1000))
                self.wavfile += str(LO)
                self.wavfile += "MHz.wav"

		#contest directory
		self.contest_dir = contest_dir
		self.contest_dir += "_" + str(now.year) 

		#fix slash in the file/directory name
		self.wavfile = self.wavfile.replace('/','-')
		self.contest_dir = self.contest_dir.replace('/','-')

		self.wavfile = self.contest_dir + "/" + self.wavfile

                # get ready to write wave file
                try:
			if not os.path.exists(self.contest_dir):
    				os.makedirs(self.contest_dir)
			self.w = wave.open(self.wavfile, 'wb')
                except:
                        print "unable to open WAV file for writing"
                        sys.exit()

        

                #16 bit complex samples 
                #self.w.setparams((2, 2, samp_rate, 1, 'NONE', 'not compressed'))
		self.w.setnchannels(CHANNELS)
		self.w.setsampwidth(p.get_sample_size(FORMAT))
		self.w.setframerate(RATE)
                #self.w.close()
                

        def write(self,data):
                self.w.writeframes(data)

        def close_wave(self,nextfilename=''):
                self.w.close()


def dump_audio(call,contest,mode,freq,qso_time,radio_nr):
	#create the wave file
	BASENAME = call + "_" + contest + "_" + mode 
	BASENAME = BASENAME.replace('/','-')
	w=wave_file(RATE,freq,BASENAME,qso_time,contest)
	__data = (b''.join(frames))
	bytes_written=w.write(__data)
	w.close_wave()

	#try to convert to mp3
	lame_path = os.path.dirname(os.path.realpath(__file__))
	lame_path += "\\lame.exe"

	if (options.so2r and radio_nr == "1"):
		command = [lame_path]
		arguments = ["-m","m", "--scale-l", "2", "--scale-r", "0", w.wavfile]
		command.extend(arguments)
	elif (options.so2r and radio_nr == "2"):
		command = [lame_path]
		arguments = ["-m","m", "--scale-l", "0", "--scale-r", "2", w.wavfile]
		command.extend(arguments)
	else:
		command = [lame_path,w.wavfile]

	try:
		output=subprocess.Popen(command, \
				stderr=subprocess.STDOUT, stdout=subprocess.PIPE).communicate()[0]
		gain = re.search('\S*Replay.+',output)
		print "WAV:", datetime.datetime.utcnow().strftime("%m-%d %H:%M:%S"), BASENAME[:20] + ".." + str(freq) + "Mhz.mp3", \
			gain.group(0)
		os.remove(w.wavfile)
	except:
		print "could not convert wav to mp3", w.wavfile

        

def manual_dump():
	print "QSO:", datetime.datetime.utcnow().strftime("%m-%d %H:%M:%S"), "HOTKEY pressed"
	dump_audio("HOTKEY","AUDIO","RF",0,datetime.datetime.utcnow(),73)

 
def hotkey():
	#create pyhk class instance
	hot = pyhk.pyhk()
 
	#add hotkey
	hot.addHotkey(['Ctrl', 'Alt',HOTKEY],manual_dump,isThread=False)
	hot.start()

t = threading.Thread(target=hotkey)
t.start()
 



print("\t--------------------------------")
print "v2.6b-replay QSO Recorder for N1MM, 2012 K3IT\n"
print("\t--------------------------------")
print "Listening on UDP port", MYPORT

p = pyaudio.PyAudio()


try:
    def_index = p.get_default_input_device_info()
    print "Input Device :", def_index['name']
except IOError as e:
    print("No Input devices: %s" % e[0])


frames = deque('',dqlength)
replay_frames = deque('',dqlength)



# define callback
def callback(in_data, frame_count, time_info, status):
    frames.append(in_data)
    replay_frames.append(in_data)
    return (None, pyaudio.paContinue)


stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK,
		stream_callback=callback)

# start the stream
stream.start_stream()

playback = pyaudio.PyAudio()

def replay_callback(in_data, frame_count, time_info, status):
    if (len(replay_frames) > 0):
      data = replay_frames.popleft()
    else:
      while (len(replay_frames) == 0):
      	#time.sleep(float(CHUNK)/RATE)
	time.sleep(0.001)
      data = replay_frames.popleft()
    return (data, pyaudio.paContinue)


pb_stream = playback.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                output=True,
                stream_callback=replay_callback)

pb_stream.stop_stream()

print "* recording", CHANNELS, "ch,", dqlength * CHUNK / RATE, "secs audio buffer, Delay:", DELAY, "secs" 
print "Input latency:", stream.get_input_latency()
print "Output latency:", pb_stream.get_output_latency()
print "Output directory", os.getcwd() + "\\<contest_YEAR>"
print "Hotkey: CTRL+ALT+" + HOTKEY
if (options.station_nr >= 0):
	print "Recording only station", options.station_nr, "QSOs"
print("\t--------------------------------")


#listen on UDP port
# Receive UDP packets transmitted by a broadcasting service

s = socket(AF_INET, SOCK_DGRAM)
s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
try:
        s.bind(('', MYPORT))
except:
        print "Error connecting to the UDP stream."



def set_replay_delay(delay):
	global replay_frames
	#buff_length = int ((delay * RATE / CHUNK)/1000) + 1
	buff_length = (delay/1000 - pb_stream.get_output_latency()) * RATE / CHUNK
	print "buf length =", buff_length
	if buff_length < 0:
		buff_length = 0
	replay_frames.clear()
	replay_frames = copy.copy(frames)
	while len(replay_frames) > buff_length:
		replay_frames.popleft()	
	#print "deque len:", buff_length
	#print "main deque len:", len(frames)
	print "replay deque len:", len(replay_frames)
	return len(replay_frames)*float(CHUNK)/RATE + pb_stream.get_output_latency()

	



seen={}

while stream.is_active():
	try:
		udp_data=s.recv(2048)
		check_sum = binascii.crc32(udp_data)

		#check if this is a play back control packet
		if "QSOREPLAY" in udp_data:
			replay_command = udp_data.split(':')[1].rstrip()
			if replay_command.isdigit():
				#pb_stream.stop_stream()
				print "---: Set replay delay to:", set_replay_delay(float(replay_command)),"s"
				pb_stream.start_stream()
				continue
			elif replay_command == "STOP":
				print "---: Stop replay"
				pb_stream.stop_stream()
				continue
			else:
				pass


		# skip packet if duplicate
		if check_sum in seen:
			seen[check_sum] += 1
		else:
			seen[check_sum] = 1
			try:
				dom = parseString(udp_data)
				now =  datetime.datetime.utcnow()

				#read UDP fields
				dom = parseString(udp_data)
				call = dom.getElementsByTagName("call")[0].firstChild.nodeValue
				mycall = dom.getElementsByTagName("mycall")[0].firstChild.nodeValue
				mode = dom.getElementsByTagName("mode")[0].firstChild.nodeValue
				freq = dom.getElementsByTagName("band")[0].firstChild.nodeValue
				contest = dom.getElementsByTagName("contestname")[0].firstChild.nodeValue
				station = dom.getElementsByTagName("NetworkedCompNr")[0].firstChild.nodeValue
				qso_timestamp = dom.getElementsByTagName("timestamp")[0].firstChild.nodeValue
				radio_nr = dom.getElementsByTagName("radionr")[0].firstChild.nodeValue
				
				#convert qso_timestamp to datetime object
				timestamp = dateutil.parser.parse(qso_timestamp)

				#verify that month matches, if not, give DD-MM-YY format precendense
				if (timestamp.strftime("%m") != now.strftime("%m")):
					timestamp = dateutil.parser.parse(qso_timestamp,dayfirst=True)	
				
				# skip packet if not matching network station number specified in the command line
				if (options.station_nr >= 0):
					if (options.station_nr != station):
						print "QSO:", timestamp.strftime("%m-%d %H:%M:%S"), call, freq, "--- ignoring from stn", station
						continue


				# skip packet if QSO was more than DELAY seconds ago
				t_delta = (now - timestamp).total_seconds()
				if ( t_delta > DELAY ):
						print "---:", timestamp.strftime("%m-%d %H:%M:%S"), call, freq, "--- ignoring ", t_delta, "sec old QSO" 
						continue

				calls = call + "_de_" + mycall

				#if (mode == "USB" or mode == "LSB"):
				#	mode="SSB"

				#t = threading.Timer( DELAY, dump_audio,[calls,contest,mode,freq,datetime.datetime.utcnow()] )
				t = threading.Timer( DELAY, dump_audio,[calls,contest,mode,freq,timestamp,radio_nr] )
				print "QSO:", timestamp.strftime("%m-%d %H:%M:%S"), call, freq
				t.start()
			except:
				pass # ignore, probably some other udp packet

	except (KeyboardInterrupt):
		print "73! k3it"
		stream.stop_stream()
		stream.close()
		p.terminate()
		raise


#
stream.close()
p.terminate()

