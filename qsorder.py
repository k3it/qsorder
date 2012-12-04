import pyaudio
import wave
import time
import sys
import struct
import datetime
import threading
#import Queue
import string
#import math
import binascii

from collections import deque
from socket import *
from xml.dom.minidom import parse, parseString

class wave_file:
        """
        class definition for the WAV file object
        """
        def __init__(self,samp_rate,LO,BASENAME,qso_time):
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

		#fix slash in the file name
		self.wav.file.replace("/","-")

                # get ready to write wave file
                try:
                        #self.f = open(self.wavfile,'wb')
                        #self.w = wave.open(self.f,"wb")
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


def dump_audio(call,mode,freq,qso_time):
	#create the wave file
	BASENAME = call + "_" + mode 
	w=wave_file(RATE,freq,BASENAME,qso_time)
	__data = (b''.join(frames))
	bytes_written=w.write(__data)
	print "WAV:", datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"), w.wavfile
	w.close_wave()

        


CHUNK = 1024

FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 8000
BASENAME = "QSO"
LO = 14000
duration = 30
dqlength = 240 # number of chunks to store in the buffer

MYPORT=12060

print("\t--------------------------------")
print "v2.1a QSO Recorder for N1MM, 2012 K3IT\n"
print("\t--------------------------------")
print "Listening on UDP port", MYPORT

p = pyaudio.PyAudio()


try:
    def_index = p.get_default_input_device_info()
    print "Input Device :", def_index['name']
except IOError as e:
    print("No Input devices: %s" % e[0])


#frames = []
frames = deque('',dqlength)



# define callback
def callback(in_data, frame_count, time_info, status):
    frames.append(in_data)
    return (None, pyaudio.paContinue)


stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK,
		stream_callback=callback)

# start the stream
stream.start_stream()


print "* recording", CHANNELS, "ch,", dqlength * CHUNK / RATE, "secs audio buffer"
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


seen={}

while stream.is_active():
	try:
		udp_data=s.recv(2048)
		check_sum = binascii.crc32(udp_data)
		dom = parseString(udp_data)

		if check_sum in seen:
			seen[check_sum] += 1
		else:
			seen[check_sum] = 1
			try:
				dom = parseString(udp_data)
				call = dom.getElementsByTagName("call")[0].firstChild.nodeValue
				mycall = dom.getElementsByTagName("mycall")[0].firstChild.nodeValue
				mode = dom.getElementsByTagName("mode")[0].firstChild.nodeValue
				freq = dom.getElementsByTagName("band")[0].firstChild.nodeValue
				contest = dom.getElementsByTagName("contestname")[0].firstChild.nodeValue

				calls = call + "_de_" + mycall
				modes = contest + "_" + mode

				t = threading.Timer( 15.0, dump_audio,[calls,modes,freq,datetime.datetime.utcnow()] )
				print "QSO:", datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"), call, freq
				t.start()
			except:
				pass # ignore, probably some other udp packet

	except (KeyboardInterrupt):
		print "73! k3it"
		raise


stream.stop_stream()
stream.close()
p.terminate()

