#!/usr/bin/python
# -*- coding: utf-8 -*-

##################################################
# qsorder - A contest QSO recorder
# Title: qsorder.py
# Author: k3it
# Version: 3.0
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

__version__ = '3.0'

import os, sys, subprocess, threading, platform, ctypes
import argparse
import re, binascii
import wave, pyaudio
import time, datetime, dateutil.parser
import logging
import json

from collections import deque
from socket import *
from xml.dom.minidom import parseString
import xml.parsers.expat

from PyQt5.QtCore import * 
from PyQt5.QtGui import *
# from PyQt5.QtUiTools import *
from PyQt5 import QtXml

# from PyQt5 import *

from qgui import *

import dropbox

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
        def __init__(self, samp_rate, LO, BASENAME, qso_time, contest_dir, mode, sampwidth, path):
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
                self.contest_dir = path + "/" + self.contest_dir
                self.wavfile     =  self.contest_dir + "/" + self.wavfile

                # get ready to write wave file
                try:
                    if not os.path.exists(self.contest_dir):
                            os.makedirs(self.contest_dir)
                    self.w = wave.open(self.wavfile, 'wb')
                except:
                    print("unable to open WAV file for writing")
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
        parser.add_argument("-s", "--station-nr", type=int, default=0,
                                help="Network Station Number [default=%(default)s]")
        parser.add_argument("-u", "--drop-key", type=str, default=None,
                                help="Dropbox auth key for file upload [default=%(default)s]")


        # global self.options
        # arglist can be passed from another python script or at the command line
        self.options = parser.parse_args(argslist)

        #load parameters from json file, if no flags specified on the command line and config file exists 
        config_file = os.path.dirname(os.path.realpath(__file__)) + "/qsorder-config.txt"
        if (len(sys.argv[1:]) == 0 and os.path.isfile(config_file)):
            try:
                with open(config_file) as params_file:    
                     params = json.load(params_file)
                for key in params:
                    setattr(self.options, key, params[key])
            except:
                pass

        # global p
        self.p = pyaudio.PyAudio()

        max_devs = self.p.get_device_count()
        self.inputs = {}
        self.selected_input = None
        if (self.options.query_inputs):
            print("\nDevice index Description")
            print("------------ -----------")
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
                            print("\t", i, "\t", devinfo['name'].encode('unicode_escape'))
                        else:
                            self.inputs[devinfo['name']] = i
                            if (i == self.options.device_index):
                                self.selected_input = devinfo['name']
                except ValueError:
                    print("uknown chardets in sound input name.")
                    pass

        #find the default input 
        if not self.options.device_index:
            try:
                def_index = self.p.get_default_input_device_info()
                self.selected_input = def_index['name']
            except IOError as e:
                self.update_console.emit("No Default innput device: %s" % e[0])

        self.p.terminate()
        if (self.options.query_inputs):
            exit(0)


        
        app = QApplication(sys.argv)
        self.qsorder = qsorderApp(self.options)
        # self.qsorder = qgui.qsorderApp(self.options)
        
        #populate inputs comnbobox
        self.qsorder.ui.inputs.addItems(list(self.inputs.keys()))
        if (self.selected_input):
            idx = self.qsorder.ui.inputs.findText(self.selected_input)
            self.qsorder.ui.inputs.setCurrentIndex(idx)

        self.qsorder.ui.applyButton.clicked.connect(self._apply_settings)
        self.qsorder.ui.saveButton.clicked.connect(self._save_settings)
        
        self.qsorder.ui.quitButton.clicked.connect(self._stopQsorder)
        self.qsorder.ui.selectDir_btn.clicked.connect(self._selectPath)


        self.timer = QTimer()
        self.timer.timeout.connect(self._update_status)
        self.timer.start(1000)

        self.timer_dropbox = QTimer()
        self.timer_dropbox.timeout.connect(self._update_status_dropbox)
        self.timer_dropbox.start(60 * 1000)

        self._apply_settings()

        sys.exit(app.exec_())

    def _selectPath(self):
        self.qsorder.ui.path.setText(QFileDialog.getExistingDirectory(options=QFileDialog.DontUseNativeDialog))

    def _apply_settings(self):
        self.options.buffer_length = self.qsorder.ui.buffer.value()
        self.options.delay         = self.qsorder.ui.delay.value()
        self.options.port          = self.qsorder.ui.port.value()
        self.options.path          = self.qsorder.ui.path.text()
        
        self.options.hot_key       = self.qsorder.ui.hotkey.text()
        self.qsorder.ui.manual_dump_btn.setShortcut(QKeySequence("Ctrl+Alt+" + self.qsorder.ui.hotkey.text()))
        
        self.options.debug         = self.qsorder.ui.debug.isChecked()
        self.options.continuous    = self.qsorder.ui.continuous.isChecked()
        self.options.so2r          = self.qsorder.ui.so2r.isChecked()

        self.options.drop_key      = self.qsorder.ui.drop_key.text()
        self.client = None

        if self.options.drop_key:
            self.client = dropbox.Dropbox(self.options.drop_key)
            # force dropbox status update
            self.timer_dropbox.start() # restart the timer
            self.timer_dropbox.timeout.emit() # force an immediate update



        try:
            self.options.device_index  = self.inputs[self.qsorder.ui.inputs.currentText()]
        except KeyError as e:
            self._update_text("Invalid Input device index: %s" % self.options.device_index)
            return


        try:
            self._stopQsorder()
        except:
            pass

        self.thread = recording_loop(self.options)
        # self.thread = test_thread(self.options)
        self.thread.update_console.connect(self._update_text)
        self.thread.upload_to_dropbox.connect(self._upload_to_dropbox)
        self.qsorder.ui.manual_dump_btn.clicked.connect(self.thread._manual_dump)
        self.thread.start()
        self.thread.wait(500)


        self._update_status()

    def _save_settings(self):
        # apply and save
        self._apply_settings()
        with open('qsorder-config.txt','w') as outfile:
            json.dump(vars(self.options), outfile, sort_keys=True, indent=4)

    def _upload_to_dropbox(self,file):
        # skip upload if dropbox status is bad or for manual audio
        if ('%' in self.qsorder.ui.label_dropbox_status.text() and not "AUDIO" in file):
            file = re.sub('\.wav$', '.mp3', file)
            # file = file.replace(self.options.path, '')
            # file = file.replace('\\', '/')
            try:
                with open(file, "rb") as f:
                    self.client.files_upload(f.read(), file.replace(self.options.path, ''), mute=True)
                    self._update_text("WAV: Uploaded %s\n" % file.replace(self.options.path, ''))
            except Exception as err:
                self._update_text("ERR: Failed to upload %s\n%s" % (file.replace(self.options.path, ''), err))


    def _update_status(self):
        palette = QPalette()
        if self.thread.isRunning():
            palette.setColor(QPalette.Foreground,Qt.blue)
            self.qsorder.ui.label_status.setPalette(palette)
            freegb = self.thread._get_free_space_mb(self.options.path)/1024.0
            msg = "Running, %.2f GB free" % freegb
            self.qsorder.ui.label_status.setText(msg)
            self.qsorder.ui.label_input.setText(self.thread.input)
            self.qsorder.ui.label_port.setText(str(self.options.port))

            self.qsorder.ui.label_buffer.setText(str(self.options.buffer_length))
            self.qsorder.ui.label_delay.setText(str(self.options.delay))
            self.qsorder.ui.label_version.setText(__version__)
            self.qsorder.ui.label_queue.setText(str(self.thread.qsos_in_queue))
        else:
            palette.setColor(QPalette.Foreground,Qt.red)
            self.qsorder.ui.label_status.setPalette(palette)
            self.qsorder.ui.label_status.setText("Stopped")
            self.qsorder.ui.label_input.setText(None)
            self.qsorder.ui.label_port.setText(None)
            self.qsorder.ui.label_buffer.setText(None)
            self.qsorder.ui.label_delay.setText(None)
            self.qsorder.ui.label_queue.setText("0")

    def _update_status_dropbox(self):
        
        if self.client is None:
            msg = "Not configured"
            self.qsorder.ui.label_dropbox_status.setText(msg)
            return
        palette = QPalette()
        #check dropbox status
        try:
            usage = self.client.users_get_space_usage()
            palette.setColor(QPalette.Foreground,Qt.blue)
            self.qsorder.ui.label_dropbox_status.setPalette(palette)
            used_bytes = float(usage.used)
            total_bytes = float(usage.allocation.get_individual().allocated)
            msg = "%.1f%% of %.1fGB used" % (used_bytes*100/total_bytes, total_bytes/1024/1024/1024)
        except:
             msg = 'Error - check key'
        # msg = "Key: " + self.options.drop_key + datetime.datetime.utcnow().strftime('%H:%S')
        self.qsorder.ui.label_dropbox_status.setText(msg)


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
        udp_packet = 'qsorder_exit_loop_DEADBEEF'
        s.sendto(udp_packet.encode(), ('<broadcast>', MYPORT))
        s.close()
        if not self.thread.wait(2000):
            print("Tired of waiting, killing thread")
            self.thread.terminate()
            self.thread.wait(500)


class test_thread(QThread):
    
    update_console = pyqtSignal(str)

    def __init__(self,options):
        super(test_thread, self).__init__()
        self.options = options
        self._isRunning = True

    def run(self):
        while self._isRunning:
            self.update_console.emit("thread running")
            time.sleep(1)
        print("Quiting thread..")

    def quit(self):
        self._isRunning = False
       


class recording_loop(QThread):
    '''
    main recording class
    '''
    update_console = pyqtSignal(str)
    upload_to_dropbox = pyqtSignal(str)

    def __init__(self, options):
        super(recording_loop, self).__init__()
        self.options = options
        self.p = pyaudio.PyAudio()
        self._isRunning = True
        self.input = None
        self.qsos_in_queue = 0


    def quit(self):
        self._isRunning = False

    def _dump_audio(self, call, contest, mode, freq, qso_time, radio_nr, sampwidth):
        # create the wave file
        BASENAME = call + "_" + contest + "_" + mode
        BASENAME = BASENAME.replace('/', '-')
        w = wave_file(RATE, freq, BASENAME, qso_time, contest, mode, sampwidth, self.options.path)
        __data = (b''.join(frames))
        bytes_written = w.write(__data)
        w.close_wave()

        # try to convert to mp3
        # lame_path = os.path.dirname(os.path.realpath(__file__))
        # lame_path += "\\lame.exe"

        # if not os.path.isfile(lame_path):
        #     #try to use one in the system path
        #     lame_path = 'lame.exe'

        lame_path = self.lame_path

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

            startupinfo = None
            if platform.system() == 'Windows':
                # import _subprocess  # @bug with python 2.7 ?
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE

            output = subprocess.Popen(command, stderr=subprocess.STDOUT, stdout=subprocess.PIPE, startupinfo=startupinfo).communicate()[0]
            gain = re.search('\S*Replay.+', output.decode())

            msg =  "WAV: " + datetime.datetime.utcnow().strftime("%m-%d %H:%M:%S") + " " + BASENAME[:20] \
                + ".." + str(freq) + "Mhz.mp3 " + gain.group(0)
            self.update_console.emit(msg.rstrip())    
            os.remove(w.wavfile)

            # send notification that the file is ready for dropbox upload
            self.upload_to_dropbox.emit(w.wavfile)

        except:
            self.update_console.emit("could not convert wav to mp3 " + str(sys.exc_info()))


        if (call != "HOTKEY"):
            self.qsos_in_queue -= 1

    def _manual_dump(self):
        self.update_console.emit("QSO: " + datetime.datetime.utcnow().strftime("%m-%d %H:%M:%S")
                + " Ctrl+Alt+" + HOTKEY + " HOTKEY pressed")
        self._dump_audio("HOTKEY", "AUDIO", "RF", 0, datetime.datetime.utcnow(), 73, self.sampwidth)

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
        # lame_path = os.path.dirname(os.path.realpath(__file__))
        # lame_path += "\\lame.exe"

        # if not os.path.isfile(lame_path):
        #     #try to use one in the system path
        #     lame_path = 'lame'

        lame_path = self.lame_path

        now = datetime.datetime.utcnow()
        contest_dir = self.options.path + "/" + "AUDIO_" + str(now.year)
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
            startupinfo = None
            if platform.system() == 'Windows':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE

            mp3handle = subprocess.Popen(command, stderr=subprocess.STDOUT, stdout=subprocess.PIPE, startupinfo=startupinfo, stdin=subprocess.PIPE)
        except:
            self.update_console.emit("CTL: error starting continous mp3 recording.")
            exit(-1)

        self.update_console.emit("CTL: " + str(now.hour).zfill(2) + ":" + str(now.minute).zfill(2) + "Z started new .mp3 file: " + filename)
        freegb = self._get_free_space_mb(contest_dir)/1024.0
        self.update_console.emit("CTL: Disk free space: %.2f GB" % freegb )
        if self._get_free_space_mb(contest_dir) < 100:
            self.update_console.emit("CTL: WARNING: Low Disk space")
        return mp3handle,filename
        #write continious mp3 stream to disk in a separate worker thread

    def _writer(self, stop_event):
        # start new lame recording
        now = datetime.datetime.utcnow()
        utchr = now.hour
        utcmin = now.minute
        (lame, filename) = self._start_new_lame_stream()
        start = time.clock() * 1000
        bytes_written = 0
        avg_rate = 0
        
        while (not stop_event.is_set()) :
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

        #stop signal received
        lame.terminate()

    def _which(self,program):
        #find executable in path. from http://stackoverflow.com/questions/377017/test-if-executable-exists-in-python
        def is_exe(fpath):
            return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

        fpath, fname = os.path.split(program)
        if fpath:
            if is_exe(program):
                return program
        else:
            pathlist = [os.path.dirname(os.path.realpath(__file__)), os.getcwd()]
            pathlist.extend(os.environ["PATH"].split(os.pathsep))
            for path in pathlist:
                path = path.strip('"')
                exe_file = os.path.join(path, program)
                if is_exe(exe_file):
                    return exe_file

        return None

    def run(self):
        dqlength = int(self.options.buffer_length * RATE / CHUNK) + 1
        DELAY = self.options.delay
        global MYPORT
        MYPORT = self.options.port


        self.update_console.emit("--------------------------------------")
        self.update_console.emit("QSO Recorder for N1MM v" + __version__ + ", 2017 K3IT")
        self.update_console.emit("--------------------------------------")

        if platform.system() == 'Windows':
            self.lame_path = self._which('lame.exe')
        else:
            self.lame_path = self._which('lame')

        if (not self.lame_path):
            self.update_console.emit("CTL: Cannot find lame encoder executable")
        else:
            self.update_console.emit("mp3 encoder: " + self.lame_path)

        if (self.options.path):
            try:
                os.path.isdir(self.options.path)
            except:
                self.update_console.emit("Invalid directory specified: " + self.options.path )
                return

        if (len(self.options.hot_key) == 1):
            global HOTKEY
            HOTKEY = self.options.hot_key.upper()
        else:
            self.update_console.emit("Hotkey should be a single character")
            return

        if (self.options.debug):
            logging.basicConfig(filename=DEBUG_FILE, level=logging.DEBUG, format='%(asctime)s %(message)s')
            logging.debug('debug log started')
            logging.debug('qsorder self.options:')
            logging.debug(self.options)


        if (self.options.device_index):
            try:
                def_index = self.p.get_device_info_by_index(self.options.device_index)
                self.update_console.emit("Input Device: " + def_index['name'])
                self.input = def_index['name']
                DEVINDEX = self.options.device_index
            except IOError as e:
                self.update_console.emit("Invalid Input device: %s" % e[0])
                self.p.terminate()
                os._exit(-1)

        else:
            try:
                def_index = self.p.get_default_input_device_info()
                # msg = "Input Device: " +  str(def_index['index']) + " " + str(def_index['name'])
                msg = "Input Device: " +  str(def_index['index']) + " " + def_index['name'].encode('utf-8')
                self.update_console.emit(msg)
                self.input = def_index['name']
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
            # rms = audioop.rms(in_data,2)
            # decibel = 20 * log10(rms)
            # print "Volume: ", decibel
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

        self.sampwidth = self.p.get_sample_size(FORMAT)


        self.update_console.emit("* recording " + str(CHANNELS) + "ch, " 
            + str(dqlength * CHUNK / RATE) + " secs audio buffer, Delay:" + str(DELAY) + " secs")
        self.update_console.emit("Output directory: " + self.options.path + "\\<contest...>")
        self.update_console.emit("Hotkey: CTRL+ALT+" + HOTKEY)
        if (self.options.station_nr > 0):
            self.update_console.emit("Recording only station " + str(self.options.station_nr) + "QSOs")
        if (self.options.continuous):
            self.update_console.emit("Full contest recording enabled.")
        self.update_console.emit("--------------------------------------\n")


        #start continious mp3 writer thread
        if (self.options.continuous):
            mp3_stop = threading.Event()
            mp3 = threading.Thread(target=self._writer, args=(mp3_stop,))
            mp3.setDaemon(True)
            mp3.start()


        # listen on UDP port
        # Receive UDP packets transmitted by a broadcasting service

        s = socket(AF_INET, SOCK_DGRAM)
        s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        s.setsockopt(SOL_SOCKET, SO_RCVBUF, 1)
        try:
                s.bind(('', MYPORT))
        except:
                self.update_console.emit("Error connecting to the UDP stream.")

        seen = {}
        while stream.is_active():
            try:
                udp_data = s.recv(2048)
                check_sum = binascii.crc32(udp_data)
                udp_data = udp_data.decode()
                try:
                    dom = parseString(udp_data)
                except xml.parsers.expat.ExpatError as e:
                    pass

                if (udp_data == "qsorder_exit_loop_DEADBEEF" or self._isRunning == False):
                    logging.debug("Received Exit magic signal")
                    if 'mp3' in locals():
                        mp3_stop.set()
                        time.sleep(0.2)
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

                        # skip packet if QSO was more than options.buffer_length-DELAY seconds ago
                        t_delta = (now - timestamp).total_seconds()
                        if (t_delta > self.options.buffer_length - DELAY):
                            self.update_console.emit("---: " +  timestamp.strftime("%m-%d %H:%M:%S") + call + " " 
                                + freq + " --- ignoring " + str(t_delta) + " sec old QSO. Check clock settings?")
                            continue
                        elif (t_delta < -DELAY):
                            self.update_console.emit("---: " + timestamp.strftime("%m-%d %H:%M:%S") + call + " " 
                                + freq + " --- ignoring " + str(-t_delta) + "sec QSO in the 'future'. Check clock settings?")
                            continue


                        calls = call + "_de_" + mycall


                        # take into account UDP buffer delay
                        if (t_delta > DELAY):
                            t_delta = DELAY

                        t = threading.Timer(DELAY - t_delta, self._dump_audio, [calls, contest, mode, freq, timestamp, radio_nr, self.sampwidth])
                        self.update_console.emit("QSO: " + timestamp.strftime("%m-%d %H:%M:%S") + " " + call + " " + freq)
                        t.start()
                        self.qsos_in_queue += 1
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
