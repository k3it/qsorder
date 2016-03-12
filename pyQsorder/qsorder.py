#!/usr/bin/python

##################################################
# qsorder - A contest QSO recorder
# Title: qsorder.py
# Author: k3it
# Generated: Tue, May 26 2015
# Version: 2.8
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
import threading
import binascii

try:
    import pyhk
    nopyhk = False
except:
    nopyhk = True


import platform
import ctypes

import datetime
import dateutil.parser

import argparse
from collections import deque
from socket import *
from xml.dom.minidom import parseString
import xml.parsers.expat


import logging


from PySide.QtCore import * 
from PySide.QtGui import *
from PySide.QtUiTools import *
from qgui import *



CHUNK      = 1024
FORMAT     = pyaudio.paInt16
CHANNELS   = 2
RATE       = 11025
BASENAME   = "QSO"
LO         = 14000
dqlength   = 360  # number of chunks to store in the buffer
DELAY      = 20.0
MYPORT     = 12060
DEBUG_FILE = "qsorder-debug-log.txt"


class wave_file:
        """
        class definition for the WAV file object
        """
        def __init__(self, samp_rate, LO, BASENAME, qso_time, contest_dir, mode, sampwidth):
                now = qso_time

                self.wavfile = BASENAME + "_"
                self.wavfile += str(now.year)
                self.wavfile += str(now.month).zfill(2)
                self.wavfile += str(now.day).zfill(2)
                self.wavfile += "_"
                self.wavfile += str(now.hour).zfill(2)
                self.wavfile += str(now.minute).zfill(2)
                self.wavfile += str(now.second).zfill(2)
                self.wavfile += "Z_"
                self.wavfile += str(LO)
                self.wavfile += "MHz.wav"
                
                # contest directory
                self.contest_dir = contest_dir
                self.contest_dir += "_" + str(now.year)
                
                # fix slash in the file/directory name
                self.wavfile     = self.wavfile.replace('/', '-')
                self.contest_dir = self.contest_dir.replace('/', '-')
                
                self.wavfile     = self.contest_dir + "/" + self.wavfile
                
                # get ready to write wave file
                try:
                    if not os.path.exists(self.contest_dir):
                            os.makedirs(self.contest_dir)
                    self.w = wave.open(self.wavfile, 'wb')
                except:
                    print "unable to open WAV file for writing"
                    sys.exit()
                # 16 bit complex samples
                # self.w.setparams((2, 2, samp_rate, 1, 'NONE', 'not compressed'))
                self.w.setnchannels(CHANNELS)
                self.w.setsampwidth(sampwidth)
                self.w.setframerate(RATE)
                # self.w.close()

        def write(self, data):
                self.w.writeframes(data)

        def close_wave(self, nextfilename=''):
                self.w.close()


class qsorder(object):
    def __init__(self,argslist=None):
        self._parse_args(argslist)

    def _parse_args(self, argslist):
        usage = "usage: %prog [OPTION]..."
        parser = argparse.ArgumentParser()
        parser.add_argument("-D", "--debug", action="store_true", default=False,
                                help="Save debug info[default=%(default)s]")
        parser.add_argument("-d", "--delay", type=int, default=20,
                                help="Capture x seconds after QSO log entry [default=%(default)s]")
        parser.add_argument("-i", "--device-index", type=int, default=None,
                                help="Index of the recording input (use -q to list) [default=%(default)s]")
        parser.add_argument("-k", "--hot-key", type=str, default="O",
                                help="Hotkey for manual recording Ctrl-Alt-<hot_key> [default=%(default)s]")
        parser.add_argument("-l", "--buffer-length", type=int, default=45,
                                help="Audio buffer length in secs [default=%(default)s]")
        parser.add_argument("-C", "--continuous", action="store_true", default=False,
                                help="Record continuous audio stream in addition to individual QSOs[default=%(default)s]")
        parser.add_argument("-P", "--port", type=int, default=12060,
                                help="UDP Port [default=%(default)s]")
        parser.add_argument("-p", "--path", type=str, default=None,
                                help="Base directory for audio files [default=%(default)s]")
        parser.add_argument("-q", "--query-inputs", action="store_true", default=False,
                                help="Query and print input devices [default=%(default)s]")
        parser.add_argument("-S", "--so2r", action="store_true", default=False,
                                help="SO2R mode, downmix to mono: Left Ch - Radio1 QSOs, Right Ch - Radio2 QSOs [default=%(default)s]")
        parser.add_argument("-s", "--station-nr", type=int, default=None,
                                help="Network Station Number [default=%(default)s]")


        # global self.options
        # arglist can be passed from another python script or at the command line
        self.options = parser.parse_args(argslist)

        # global p
        self.p = pyaudio.PyAudio()

        max_devs = self.p.get_device_count()
        inputs = {}
        if (self.options.query_inputs):
            print "Detected", max_devs, "devices\n"       ################################
            print "Device index Description"
            print "------------ -----------"
        for i in range(max_devs):
            p = pyaudio.PyAudio()
            devinfo = self.p.get_device_info_by_index(i)

            if devinfo['maxInputChannels'] > 0:
                try:
                    if self.p.is_format_supported(int(RATE),
                                             input_device=devinfo['index'],
                                             input_channels=devinfo['maxInputChannels'],
                                             input_format=pyaudio.paInt16):
                        if (self.options.query_inputs):
                            print "\t", i, "\t", devinfo['name']
                        else:
                            inputs[i] = devinfo['name']
                except ValueError:
                    pass
        self.p.terminate()
        if (self.options.query_inputs):
            exit(0)


        
        app = QApplication(sys.argv)
        self.qsorder = qsorderApp(self.options)
        self.qsorder.ui.inputs.addItems(inputs.values())

        self.qsorder.ui.applyButton.clicked.connect(self._apply_settings)
        
        self.qsorder.ui.quitButton.clicked.connect(self._stopQsorder)


        sys.exit(app.exec_())

    def _apply_settings(self):
        self.options.buffer_length = self.qsorder.ui.buffer.value()
        self.options.delay         = self.qsorder.ui.delay.value()
        self.options.port          = self.qsorder.ui.port.value()
        self.options.path          = self.qsorder.ui.path.text()
        self.options.hot_key       = self.qsorder.ui.hotkey.text()
        self.options.debug         = self.qsorder.ui.debug.isChecked()
        self.options.continuous    = self.qsorder.ui.continuous.isChecked()
        self.options.so2r          = self.qsorder.ui.so2r.isChecked()


        try:
            self._stopQsorder()
        except:
            pass

        self.thread = recording_loop(self.options)
        # self.thread = test_thread(self.options)
        self.thread.update_console.connect(self._update_text)
        self.thread.start()

    def _update_text(self,txt):
        self.qsorder.ui.console.appendPlainText(txt)
        # self.qsorder.ui.console.verticalScrollBar().setValue(self.qsorder.ui.console.verticalScrollBar().maximum())
        self.qsorder.ui.console.moveCursor(QTextCursor.End)
        self.qsorder.ui.console.ensureCursorVisible()

    def _stopQsorder(self):
        # MYPORT = self.options.port
        s = socket(AF_INET, SOCK_DGRAM)
        s.bind(('', 0))
        s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        udp_packet = "qsorder_exit_loop_DEADBEEF"
        s.sendto(udp_packet, ('<broadcast>', MYPORT))
        s.close()
        if not self.thread.wait(2000):
            print "Tired of waiting, killing thread"
            self.thread.terminate()
            self.thread.wait(500)

class test_thread(QThread):
    
    update_console = Signal(str)

    def __init__(self,options):
        super(test_thread, self).__init__()
        self.options = options
        self._isRunning = True

    def run(self):
        while self._isRunning:
            self.update_console.emit("thread running")
            time.sleep(1)
        print "Quiting thread.."

    def quit(self):
        self._isRunning = False
       


class recording_loop(QThread):
    '''
    main recording class
    '''
    update_console = Signal(str)

    def __init__(self, options):
        super(recording_loop, self).__init__()
        self.options = options
        self.p = pyaudio.PyAudio()
        self._isRunning = True

    def quit(self):
        self._isRunning = False

    def _dump_audio(self, call, contest, mode, freq, qso_time, radio_nr, sampwidth):
        # create the wave file
        BASENAME = call + "_" + contest + "_" + mode
        BASENAME = BASENAME.replace('/', '-')
        w = wave_file(RATE, freq, BASENAME, qso_time, contest, mode, sampwidth)
        __data = (b''.join(frames))
        bytes_written = w.write(__data)
        w.close_wave()

        # try to convert to mp3
        lame_path = os.path.dirname(os.path.realpath(__file__))
        lame_path += "\\lame.exe"

        if not os.path.isfile(lame_path):
            #try to use one in the system path
            lame_path = 'lame'


        if (self.options.so2r and radio_nr == "1"):
            command = [lame_path]
            arguments = ["-h", "-m", "m", "--scale-l", "2", "--scale-r", "0", w.wavfile]
            command.extend(arguments)
        elif (self.options.so2r and radio_nr == "2"):
            command = [lame_path]
            arguments = ["-h", "-m", "m", "--scale-l", "0", "--scale-r", "2", w.wavfile]
            command.extend(arguments)
        else:
            command = [lame_path]
            arguments = ["-h", w.wavfile]
            command.extend(arguments)

        try:
            if (self.options.debug):
                logging.debug(command)

            output = subprocess.Popen(command, stderr=subprocess.STDOUT, stdout=subprocess.PIPE).communicate()[0]
            gain = re.search('\S*Replay.+', output)

            msg =  "WAV: " + datetime.datetime.utcnow().strftime("%m-%d %H:%M:%S") + " " + BASENAME[:20] \
                + ".." + str(freq) + "Mhz.mp3 " + gain.group(0)
            self.update_console.emit(msg.rstrip())    
            os.remove(w.wavfile)
        except:
            self.update_console.emit("could not convert wav to mp3 " + w.wavfile)

    def _manual_dump(self):
        self.update_console.emit("QSO: " + datetime.datetime.utcnow().strftime("%m-%d %H:%M:%S") + " HOTKEY pressed")
        self._dump_audio("HOTKEY", "AUDIO", "RF", 0, datetime.datetime.utcnow(), 73)

    def _hotkey(self):
        if nopyhk:
            return
        # create pyhk class instance
        hot = pyhk.pyhk()

        # add hotkey
        hot.addHotkey(['Ctrl', 'Alt', HOTKEY], self._manual_dump, isThread=False)
        hot.start()

    def _get_free_space_mb(self,folder):
        """ Return folder/drive free space (in bytes)
        """
        if platform.system() == 'Windows':
            free_bytes = ctypes.c_ulonglong(0)
            ctypes.windll.kernel32.GetDiskFreeSpaceExW(ctypes.c_wchar_p(folder), None, None, ctypes.pointer(free_bytes))
            return free_bytes.value/1024/1024
        else:
            st = os.statvfs(folder)
            return st.f_bavail * st.f_frsize/1024/1024

    def _start_new_lame_stream(self):
        lame_path = os.path.dirname(os.path.realpath(__file__))
        lame_path += "\\lame.exe"

        if not os.path.isfile(lame_path):
            #try to use one in the system path
            lame_path = 'lame'

        now = datetime.datetime.utcnow()
        contest_dir = "AUDIO_" + str(now.year)
        if not os.path.exists(contest_dir):
            os.makedirs(contest_dir)

        BASENAME = "CONTEST_AUDIO"
        filename = contest_dir + "/" + BASENAME + "_"
        filename += str(now.year)
        filename += str(now.month).zfill(2)
        filename += str(now.day).zfill(2)
        filename += "_"
        filename += str(now.hour).zfill(2)
        filename += str(now.minute).zfill(2)
        filename += "Z"
        # filename += str(int(LO/1000))
        filename += ".mp3"
        command = [lame_path]
        # arguments = ["-r", "-s", str(RATE), "-v", "--disptime 60", "-h", "--tt", BASENAME, "--ty", str(now.year), "--tg Ham Radio", "-", filename]
        # arguments = ["-r", "-s", str(RATE), "-v", "-h", "--quiet", "--tt", BASENAME, "--ty", str(now.year), "-", filename]
        arguments = ["-r", "-s", str(RATE), "-h", "--flush", "--quiet", "--tt", "Qsorder Contest Recording", "--ty", str(now.year), "--tc", os.path.basename(filename), "-", filename]
        command.extend(arguments)
        try:
            mp3handle = subprocess.Popen(command, stderr=subprocess.STDOUT, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
        except:
            self.update_console.emit("CTL error starting mp3 recording.  Exiting..")
            exit(-1)

        self.update_console.emit("CTL: " + str(now.hour).zfill(2) + ":" + str(now.minute).zfill(2) + "Z started new .mp3 file: " + filename)
        self.update_console.emit("CTL: Disk free space: " +  str(self._get_free_space_mb(contest_dir)/1024) +  "GB")
        if self._get_free_space_mb(contest_dir) < 100:
            self.update_console.emit("CTL: WARNING: Low Disk space")
        return mp3handle,filename
        #write continious mp3 stream to disk in a separate worker thread

    def _writer(self):
        # start new lame recording
        now = datetime.datetime.utcnow()
        utchr = now.hour
        utcmin = now.minute
        (lame, filename) = self._start_new_lame_stream()
        start = time.clock() * 1000
        bytes_written = 0
        avg_rate = 0
        
        while True:
            #open a new file on top of the hour
            now = datetime.datetime.utcnow()
            if utchr != now.hour:
                # sleep some to flush out buffers
                time.sleep(5)
                lame.terminate()
                utchr = now.hour
                (lame, filename) = self._start_new_lame_stream()
            if (len(replay_frames) > 0):
                data = replay_frames.popleft()
                lame.stdin.write(data)
                bytes_written += sys.getsizeof(data)
            else:
                end = time.clock()*1000
                if (end - start > 60000):
                    elapsed = end - start
                    sampling_rate = bytes_written/4/elapsed
                    # self.update_console.emit(str(bytes_written) + " bytes in " + str(elapsed) + "ms. Sampling rate: " 
                    #     +  str(sampling_rate) + "kHz")
                    start = end
                    bytes_written=0
                time.sleep(1)
            if (utcmin != now.minute and now.minute % 10 == 0 and now.minute != 0):
                self.update_console.emit("CTL: " + str(now.hour).zfill(2) + ":" + str(now.minute).zfill(2) 
                    + "Z ...recording: " + filename)
                contest_dir = "AUDIO_" + str(now.year)
                if self._get_free_space_mb(contest_dir) < 100:
                    self.update_console.emit("CTL: WARNING: Low Disk space")
                utcmin = now.minute

    def run(self):
        dqlength = int(self.options.buffer_length * RATE / CHUNK) + 1
        DELAY = self.options.delay
        global MYPORT
        MYPORT = self.options.port

        if (self.options.path):
            os.chdir(self.options.path)

        if (len(self.options.hot_key) == 1):
            global HOTKEY
            HOTKEY = self.options.hot_key.upper()
        else:
            self.update_console.emit("Hotkey should be a single character")
            parser.print_help()
            exit(-1)

        if (self.options.debug):
            logging.basicConfig(filename=DEBUG_FILE, level=logging.DEBUG, format='%(asctime)s %(message)s')
            logging.debug('debug log started')
            logging.debug('qsorder self.options:')
            logging.debug(self.options)


        # start hotkey monitoring thread
        if not nopyhk:
            t = threading.Thread(target=self._hotkey)
            t.setDaemon(True)
            t.start()


        self.update_console.emit("--------------------------------------")
        self.update_console.emit("v3.0 QSO Recorder for N1MM, 2016 K3IT")
        self.update_console.emit("--------------------------------------")


        if (self.options.device_index):
            try:
                def_index = self.p.get_device_info_by_index(self.options.device_index)
                self.update_console.emit("Input Device :" + def_index['name'])
                DEVINDEX = self.options.device_index
            except IOError as e:
                self.update_console.emit("Invalid Input device: %s" % e[0])
                self.p.terminate()
                os._exit(-1)

        else:
            try:
                def_index = self.p.get_default_input_device_info()
                msg = "Input Device: " +  str(def_index['index']) + " " + str(def_index['name'])
                self.update_console.emit(msg)
                DEVINDEX = def_index['index']
            except IOError as e:
                self.update_console.emit("No Input devices: %s" % e[0])
                self.p.terminate()
                os._exit(-1)

        # queue for chunked recording
        global frames
        frames = deque('', dqlength)

        # queue for continous recording
        global replay_frames
        replay_frames = deque('',dqlength)

        self.update_console.emit("Listening on UDP port " + str(MYPORT))

        # define callback
        def callback(in_data, frame_count, time_info, status):
            frames.append(in_data)
            # add code for continous recording here
            replay_frames.append(in_data)
            return (None, pyaudio.paContinue)


        stream = self.p.open(format=FORMAT,
                        channels=CHANNELS,
                        input_device_index=DEVINDEX,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK,
                        stream_callback=callback)

        # start the stream
        stream.start_stream()

        sampwidth = self.p.get_sample_size(FORMAT)


        self.update_console.emit("* recording " + str(CHANNELS) + "ch, " 
            + str(dqlength * CHUNK / RATE) + " secs audio buffer, Delay:" + str(DELAY) + " secs")
        self.update_console.emit("Output directory: " + os.getcwd() + "\\<contest...>")
        if nopyhk:
            self.update_console.emit("Hotkey functionality is disabled")
        else:
            self.update_console.emit("Hotkey: CTRL+ALT+" + HOTKEY)
        if (self.options.station_nr > 0):
            self.update_console.emit("Recording only station " + str(self.options.station_nr) + "QSOs")
        if (self.options.continuous):
            self.update_console.emit("Full contest recording enabled.")
        self.update_console.emit("--------------------------------\n")


        #start continious mp3 writer thread
        if (self.options.continuous):
            mp3 = threading.Thread(target=self._writer)
            mp3.setDaemon(True)
            mp3.start()


        # listen on UDP port
        # Receive UDP packets transmitted by a broadcasting service

        s = socket(AF_INET, SOCK_DGRAM)
        s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        try:
                s.bind(('', MYPORT))
        except:
                self.update_console.emit("Error connecting to the UDP stream.")

        seen = {}
        while stream.is_active():
            try:
                udp_data = s.recv(2048)
                check_sum = binascii.crc32(udp_data)
                try:
                    dom = parseString(udp_data)
                except xml.parsers.expat.ExpatError, e:
                    pass

                if (udp_data == "qsorder_exit_loop_DEADBEEF" or self._isRunning == False):
                    logging.debug("Received Exit magic signal")
                    break


                if (self.options.debug):
                    logging.debug('UDP Packet Received:')
                    logging.debug(udp_data)

                # skip packet if duplicate
                if check_sum in seen:
                    seen[check_sum] += 1
                    if (self.options.debug):
                        logging.debug('DUPE packet skipped')
                else:
                    seen[check_sum] = 1
                    try:
                        now = datetime.datetime.utcnow()

                        # read UDP fields
                        dom = parseString(udp_data)
                        call = dom.getElementsByTagName("call")[0].firstChild.nodeValue
                        mycall = dom.getElementsByTagName("mycall")[0].firstChild.nodeValue
                        mode = dom.getElementsByTagName("mode")[0].firstChild.nodeValue
                        freq = dom.getElementsByTagName("band")[0].firstChild.nodeValue
                        contest = dom.getElementsByTagName("contestname")[0].firstChild.nodeValue
                        station = dom.getElementsByTagName("NetworkedCompNr")[0].firstChild.nodeValue
                        qso_timestamp = dom.getElementsByTagName("timestamp")[0].firstChild.nodeValue
                        radio_nr = dom.getElementsByTagName("radionr")[0].firstChild.nodeValue

                        # convert qso_timestamp to datetime object
                        timestamp = dateutil.parser.parse(qso_timestamp)

                        # verify that month matches, if not, give DD-MM-YY format precendense
                        if (timestamp.strftime("%m") != now.strftime("%m")):
                            timestamp = dateutil.parser.parse(qso_timestamp, dayfirst=True)

                        # skip packet if not matching network station number specified in the command line
                        if (self.options.station_nr > 0):
                            if (self.options.station_nr != station):
                                self.update_console.emit("QSO: " + timestamp.strftime("%m-%d %H:%M:%S") + call + " " 
                                    + freq + " --- ignoring from stn" +  str(station))
                                continue

                        # skip packet if QSO was more than DELAY seconds ago
                        t_delta = (now - timestamp).total_seconds()
                        if (t_delta > DELAY):
                            self.update_console.emit("---: " +  timestamp.strftime("%m-%d %H:%M:%S") + call + " " 
                                + freq + " --- ignoring " + str(t_delta) + " sec old QSO. Check clock settings?")
                            continue
                        elif (t_delta < -DELAY):
                            self.update_console.emit("---: " + timestamp.strftime("%m-%d %H:%M:%S") + call + " " 
                                + freq + " --- ignoring " + str(-t_delta) + "sec QSO in the 'future'. Check clock settings?")
                            continue


                        calls = call + "_de_" + mycall

                        t = threading.Timer(DELAY, self._dump_audio, [calls, contest, mode, freq, timestamp, radio_nr, sampwidth])
                        self.update_console.emit("QSO: " + timestamp.strftime("%m-%d %H:%M:%S") + " " + call + " " + freq)
                        t.start()
                    except:
                        if (self.options.debug):
                            logging.debug('Could not parse previous packet')
                            logging.debug(sys.exc_info())

                        pass  # ignore, probably some other udp packet

            except (KeyboardInterrupt):
                self.update_console.emit("73! K3IT")
                stream.stop_stream()
                stream.close()
                self.p.terminate()
                exit(0)

        stream.stop_stream()
        stream.close()
        self.p.terminate()

if __name__ == '__main__':    
    
    qsorder = qsorder()
