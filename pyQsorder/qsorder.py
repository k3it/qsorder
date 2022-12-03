# !/usr/bin/python
# -*- coding: utf-8 -*-

##################################################
# qsorder - A contest QSO recorder
# Title: qsorder.py
# Author: k3it
# Version: 20.30.31
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

__version__ = '3.2'

import argparse
import binascii
import ctypes
import datetime
import json
import logging
import os
import platform
import re
import subprocess
import sys
import threading
import time
import wave
import webbrowser
import xml.parsers.expat
from collections import deque
from socket import *
from xml.dom.minidom import parseString

import dateutil.parser
import dropbox
import sounddevice as sd
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtWidgets import QFileDialog

try:
    from winreg import *
except:
    # non-windows platform
    pass

# try:
#     from . import qsorder_ui
# except:


sys.path.insert(1, './pyQsorder/')
sys.path.insert(1, './')
import qsorder_ui

# try:
#     from .qgui import *
# except:
#     from qgui import *

# from PyQt5.QtUiTools import *
# from PyQt5 import *

CHUNK = 1024
FORMAT = 'int16'
CHANNELS = 2
BASENAME = "QSO"
LO = 14000
DEBUG_FILE = "qsorder-debug-log.txt"


class qsorderApp(QWidget):
    def __init__(self, options):
        super(qsorderApp, self).__init__()
        self.options = options
        self.initUI()

    def _register(self):
        webbrowser.open('https://qsorder.hamradiomap.com/register')

    def initUI(self):

        self.ui = qsorder_ui.Ui_Form()

        self.ui.setupUi(self)

        self.ui.quitButton.clicked.connect(QCoreApplication.instance().quit)
        self.ui.getDropbox_btn.clicked.connect(self._register)

        # process arguments
        self.ui.buffer.setValue(self.options.buffer_length)
        self.ui.delay.setValue(self.options.delay)
        self.ui.port.setValue(self.options.port)
        self.ui.drop_key.setText(self.options.drop_key)

        if self.options.path:
            self.ui.path.setText(self.options.path)
        else:
            try:
                aReg = ConnectRegistry(None, HKEY_CURRENT_USER)
                key = OpenKey(aReg, r"Software\N1MM Logger+")
                path = QueryValueEx(key, 'userdir')[0] + "\\QsoRecording"
                self.ui.path.setText(path)
            except:
                self.ui.path.setText(os.getcwd())

        self.ui.hotkey.setText(self.options.hot_key.upper())
        self.ui.debug.setChecked(self.options.debug)
        self.ui.continuous.setChecked(self.options.continuous)
        self.ui.so2r.setChecked(self.options.so2r)
        self.ui.station_nr.setValue(self.options.station_nr)

        self.show()


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
        self.wavfile = self.wavfile.replace('/', '-')
        self.contest_dir = self.contest_dir.replace('/', '-')
        self.contest_dir = path + "/" + self.contest_dir
        self.wavfile = self.contest_dir + "/" + self.wavfile

        # get ready to write wave file
        try:
            if not os.path.exists(self.contest_dir):
                os.makedirs(self.contest_dir)
            self.w = wave.open(self.wavfile, 'wb')
        except:

            msg = "unable to open WAV file for writing"
            print_and_log(msg)
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


class qsorder_class(object):
    def __init__(self, argslist=None):
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
        parser.add_argument("-r", "--radio-nr", type=int, default=None,
                            help="Radio Number [default=%(default)s]")
        parser.add_argument("-R", "--sample-rate", type=int, default=11025,
                            help="Audio sampling rate [default=%(default)s]")

        # global self.options
        # arglist can be passed from another python script or at the command line
        self.options = parser.parse_args(argslist)

        global RATE
        RATE = self.options.sample_rate

        dqlength = int(self.options.buffer_length * RATE / CHUNK) + 1
        DELAY = self.options.delay
        MYPORT = self.options.port

        # load parameters from json file, if no flags specified on the command line and config file exists
        if getattr(sys, 'frozen', False):
            config_file = os.path.dirname(os.path.realpath(sys.executable)) + "/qsorder-config.txt"
        else:
            config_file = os.path.dirname(os.path.realpath(__file__)) + "/qsorder-config.txt"
        if len(sys.argv[1:]) == 0 and os.path.isfile(config_file):
            try:
                with open(config_file) as params_file:
                    params = json.load(params_file)
                for key in params:
                    setattr(self.options, key, params[key])
            except:
                pass

        # max_devs = sd.DeviceList.count()
        self.inputs = {}
        self.selected_input = None
        if self.options.query_inputs:
            print_and_log("\nDevice index Description")
            print_and_log("------------ -----------")

        devs = sd.query_devices()

        for i in range(len(devs)):
            if devs[i]['max_input_channels'] > 0:
                try:
                    sd.check_input_settings(device=i, channels=CHANNELS, dtype=FORMAT)
                    dev_name = devs[i]['name'] + " - " + sd.query_hostapis(devs[i]['hostapi'])['name']
                    if self.options.query_inputs:
                        msg = "\t" + str(i) + "\t" + dev_name
                        print_and_log(msg)
                    else:
                        self.inputs[dev_name] = i
                        if i == self.options.device_index:
                            self.selected_input = dev_name
                except:
                    pass
        if self.options.query_inputs:
            exit(0)

        app = QApplication(sys.argv)
        self.qsorder = qsorderApp(self.options)
        # self.qsorder = qgui.qsorderApp(self.options)

        # find the default input
        if not self.options.device_index:
            try:
                def_index = sd.query_devices(device=sd.default.device, kind='input')
                self.selected_input = def_index['name'] + " - " + sd.query_hostapis(def_index['hostapi'])['name']
            except IOError as e:
                self._update_text(e.strerror)

        # populate inputs comnbobox
        self.qsorder.ui.inputs.addItems(list(self.inputs.keys()))
        if self.selected_input:
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
        self.qsorder.ui.path.setText(QFileDialog.getExistingDirectory())

    def _apply_settings(self):
        self.options.buffer_length = self.qsorder.ui.buffer.value()
        self.options.delay = self.qsorder.ui.delay.value()
        self.options.port = self.qsorder.ui.port.value()
        self.options.path = self.qsorder.ui.path.text()

        self.options.hot_key = self.qsorder.ui.hotkey.text()
        self.qsorder.ui.manual_dump_btn.setShortcut(QKeySequence("Ctrl+Alt+" + self.qsorder.ui.hotkey.text()))

        self.options.debug = self.qsorder.ui.debug.isChecked()
        self.options.continuous = self.qsorder.ui.continuous.isChecked()
        self.options.so2r = self.qsorder.ui.so2r.isChecked()

        self.options.drop_key = self.qsorder.ui.drop_key.text()
        self.client = None

        if self.options.drop_key:
            self.client = dropbox.Dropbox(self.options.drop_key)
            # force dropbox status update
            self.timer_dropbox.start()  # restart the timer
            self.timer_dropbox.timeout.emit()  # force an immediate update

        try:
            self.options.device_index = self.inputs[self.qsorder.ui.inputs.currentText()]
        except KeyError as e:
            msg = ("Invalid Input device index: %s" % self.options.device_index)
            self._update_text(msg)
            print_and_log(msg)
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
        with open('qsorder-config.txt', 'w') as outfile:
            json.dump(vars(self.options), outfile, sort_keys=True, indent=4)

    def _upload_to_dropbox(self, file):
        # skip upload if dropbox status is bad or for manual audio
        if '%' in self.qsorder.ui.label_dropbox_status.text() and not "AUDIO" in file:
            file = re.sub('\.wav$', '.mp3', file)
            # file = file.replace(self.options.path, '')
            # file = file.replace('\\', '/')
            try:
                with open(file, "rb") as f:
                    self.client.files_upload(f.read(), file.replace(self.options.path, ''), mute=True)
                    msg = ("WAV: Uploaded %s\n" % file.replace(self.options.path, ''))
                    self._update_text(msg)
                    print_and_log(msg)
            except Exception as err:
                msg = ("ERR: Failed to upload %s\n%s" % (file.replace(self.options.path, ''), err))
                self._update_text(msg)
                print_and_log(msg)

    def _update_status(self):
        palette = QPalette()
        if hasattr(self, 'thread') and self.thread.isRunning():
            palette.setColor(QPalette.Foreground, Qt.blue)
            self.qsorder.ui.label_status.setPalette(palette)
            freegb = self.thread._get_free_space_mb(self.options.path) / 1024.0
            msg = "Running, %.2f GB free" % freegb
            self.qsorder.ui.label_status.setText(msg)
            self.qsorder.ui.label_input.setText(self.thread.input)
            self.qsorder.ui.label_port.setText(str(self.options.port))

            self.qsorder.ui.label_buffer.setText(str(self.options.buffer_length))
            self.qsorder.ui.label_delay.setText(str(self.options.delay))
            self.qsorder.ui.label_version.setText(__version__)
            self.qsorder.ui.label_queue.setText(str(self.thread.qsos_in_queue))
        else:
            palette.setColor(QPalette.Foreground, Qt.red)
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
        # check dropbox status
        try:
            usage = self.client.users_get_space_usage()
            palette.setColor(QPalette.Foreground, Qt.blue)
            self.qsorder.ui.label_dropbox_status.setPalette(palette)
            used_bytes = float(usage.used)
            total_bytes = float(usage.allocation.get_individual().allocated)
            msg = "%.1f%% of %.1fGB used" % (used_bytes * 100 / total_bytes, total_bytes / 1024 / 1024 / 1024)
        except:
            msg = 'Error - check key'
        # msg = "Key: " + self.options.drop_key + datetime.datetime.utcnow().strftime('%H:%S')
        self.qsorder.ui.label_dropbox_status.setText(msg)

    def _update_text(self, txt):
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
        if hasattr(self, 'thread') and not self.thread.wait(2000):
            msg = "Tired of waiting, killing thread"
            print_and_log(msg)
            self.thread.terminate()
            self.thread.wait(500)


class test_thread(QThread):
    update_console = pyqtSignal(str)

    def __init__(self, options):
        super(test_thread, self).__init__()
        self.options = options
        self._isRunning = True

    def run(self):
        while self._isRunning:
            self.update_console.emit("thread running")
            time.sleep(1)
        print_and_log("Quiting thread..")

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
#        __data = (b''.join(frames))
        w.write(b''.join(frames))
        w.close_wave()

        lame_path = self.lame_path

        artist = "QSO Audio"
        title = os.path.basename(w.wavfile).replace('.wav', '')
        year = str(qso_time.year)

        if self.options.so2r and radio_nr == "1":
            command = [lame_path]
            arguments = ["--tt", title, "--ta", artist, "--ty", year, "-h", "-m", "l", w.wavfile]
            command.extend(arguments)
        elif self.options.so2r and radio_nr == "2":
            command = [lame_path]
            arguments = ["--tt", title, "--ta", artist, "--ty", year, "-h", "-m", "r", w.wavfile]
            command.extend(arguments)
        else:
            command = [lame_path]
            arguments = ["--tt", title, "--ta", artist, "--ty", year, "-h", w.wavfile]
            command.extend(arguments)

        try:
            if self.options.debug:
                logging.debug(command)

            startupinfo = None
            if platform.system() == 'Windows':
                # import _subprocess  # @bug with python 2.7 ?
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE

            output = subprocess.Popen(command, stderr=subprocess.STDOUT, stdout=subprocess.PIPE,
                                      startupinfo=startupinfo).communicate()[0]
            gain = re.search('\S*Replay.+', output.decode())

            msg = "WAV: " + datetime.datetime.utcnow().strftime("%m-%d %H:%M:%S") + " " + BASENAME[:20] \
                  + ".." + str(freq) + "Mhz.mp3 " + gain.group(0)
            msg = msg.rstrip()
            self.update_console.emit(msg)
            print_and_log(msg)

            os.remove(w.wavfile)

            # send notification that the file is ready for dropbox upload
            self.upload_to_dropbox.emit(w.wavfile)

        except:
            msg = ("could not convert wav to mp3 " + str(sys.exc_info()))
            self.update_console.emit(msg)
            print_and_log(msg)

        if call != "HOTKEY":
            self.qsos_in_queue -= 1

    def _manual_dump(self):
        msg = ("QSO: " + datetime.datetime.utcnow().strftime("%m-%d %H:%M:%S")
               + " Ctrl+Alt+" + HOTKEY + " HOTKEY pressed")
        self.update_console.emit(msg)
        print_and_log(msg)
        self._dump_audio("HOTKEY", "AUDIO", "RF", 0, datetime.datetime.utcnow(), 73, self.sampwidth)

    def _get_free_space_mb(self, folder):
        """ Return folder/drive free space (in bytes)
        """
        if platform.system() == 'Windows':
            free_bytes = ctypes.c_ulonglong(0)
            ctypes.windll.kernel32.GetDiskFreeSpaceExW(ctypes.c_wchar_p(folder), None, None, ctypes.pointer(free_bytes))
            return free_bytes.value / 1024 / 1024
        else:
            st = os.statvfs(folder)
            return st.f_bavail * st.f_frsize / 1024 / 1024

    def _start_new_lame_stream(self):

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
        arguments = ["-r", "-s", str(RATE), "-h", "--flush", "--quiet", "--tt", "Qsorder Contest Recording", "--ty",
                     str(now.year), "--tc", os.path.basename(filename), "-", filename]
        command.extend(arguments)
        try:
            startupinfo = None
            if platform.system() == 'Windows':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE

            mp3handle = subprocess.Popen(command, stderr=subprocess.STDOUT, stdout=subprocess.PIPE,
                                         startupinfo=startupinfo, stdin=subprocess.PIPE)
        except:
            msg = "CTL: error starting continous mp3 recording."
            self.update_console.emit(msg)
            print_and_log(msg)
            exit(-1)

        msg = ("CTL: " + str(now.hour).zfill(2) + ":" + str(now.minute).zfill(
            2) + "Z started new .mp3 file: " + filename)
        self.update_console.emit(msg)
        print_and_log(msg)
        freegb = self._get_free_space_mb(contest_dir) / 1024.0
        msg = ("CTL: Disk free space: %.2f GB" % freegb)
        self.update_console.emit(msg)
        print_and_log(msg)
        if self._get_free_space_mb(contest_dir) < 100:
            msg = "CTL: WARNING: Low Disk space"
            self.update_console.emit(msg)
            print_and_log(msg)
        return mp3handle, filename
        # write continious mp3 stream to disk in a separate worker thread

    def _writer(self, stop_event):
        # start new lame recording
        now = datetime.datetime.utcnow()
        utchr = now.hour
        utcmin = now.minute
        (lame, filename) = self._start_new_lame_stream()
        start = time.process_time() * 1000
        bytes_written = 0
        avg_rate = 0

        while not stop_event.is_set():
            # open a new file on top of the hour
            now = datetime.datetime.utcnow()
            if utchr != now.hour:
                # sleep some to flush out buffers
                time.sleep(5)
                lame.terminate()
                utchr = now.hour
                (lame, filename) = self._start_new_lame_stream()
            if len(replay_frames) > 0:
                data = replay_frames.popleft()
                lame.stdin.write(data)
                bytes_written += sys.getsizeof(data)
            else:
                end = time.process_time() * 1000
                if end - start > 60000:
                    elapsed = end - start
                    sampling_rate = bytes_written / 4 / elapsed
                    # self.update_console.emit(str(bytes_written) + " bytes in " + str(elapsed) + "ms. Sampling rate: " 
                    #     +  str(sampling_rate) + "kHz")
                    start = end
                    bytes_written = 0
                time.sleep(1)
            if utcmin != now.minute and now.minute % 10 == 0 and now.minute != 0:
                msg = ("CTL: " + str(now.hour).zfill(2) + ":" + str(now.minute).zfill(2)
                       + "Z ...recording: " + filename)
                self.update_console.emit(msg)
                print_and_log(msg)
                contest_dir = "AUDIO_" + str(now.year)
                if self._get_free_space_mb(contest_dir) < 100:
                    msg = "CTL: WARNING: Low Disk space"
                    self.update_console.emit(msg)
                    print_and_log(msg)
                utcmin = now.minute

        # stop signal received
        lame.terminate()

    def _which(self, program):
        # find executable in path. from http://stackoverflow.com/questions/377017/test-if-executable-exists-in-python
        def is_exe(fpath):
            return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

        fpath, fname = os.path.split(program)
        if fpath:
            if is_exe(program):
                return program
        else:
            if getattr(sys, 'frozen', False):
                pathlist = [os.path.dirname(os.path.realpath(sys.executable)), os.getcwd()]
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

        msg = "--------------------------------------"
        self.update_console.emit(msg)
        print_and_log(msg)
        msg = ("QSO Recorder for N1MM v" + __version__ + ", 2022 K3IT")
        self.update_console.emit(msg)
        print_and_log(msg)
        msg = "--------------------------------------"
        self.update_console.emit(msg)
        print_and_log(msg)
        msg = (datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"))
        self.update_console.emit(msg)
        print_and_log(msg)

        if platform.system() == 'Windows':
            self.lame_path = self._which('lame.exe')
        else:
            self.lame_path = self._which('lame')

        if not self.lame_path:
            msg = "CTL: Cannot find lame encoder executable"
            self.update_console.emit(msg)
            print_and_log(msg)
        else:
            msg = ("mp3 encoder: " + self.lame_path)
            self.update_console.emit(msg)
            print_and_log(msg)

        if self.options.path:
            try:
                os.path.isdir(self.options.path)
            except:
                msg = ("Invalid directory specified: " + self.options.path)
                self.update_console.emit(msg)
                print_and_log(msg)
                return

        if len(self.options.hot_key) == 1:
            global HOTKEY
            HOTKEY = self.options.hot_key.upper()
        else:
            msg = "Hotkey should be a single character"
            self.update_console.emit(msg)
            print_and_log(msg)
            return

        if self.options.debug:
            logging.basicConfig(filename=DEBUG_FILE, level=logging.DEBUG, format='%(asctime)s %(message)s')
            logging.debug('debug log started')
            logging.debug('qsorder self.options:')
            logging.debug(self.options)

        if self.options.device_index:
            try:
                def_index = sd.query_devices(device=self.options.device_index, kind='input')
                msg = ("Input Device: " + def_index['name'])
                self.update_console.emit(msg)
                print_and_log(msg)
                self.input = def_index['name']
                DEVINDEX = self.options.device_index
            except IOError as e:
                msg = ("Invalid Input device: %s" % e[0])
                self.update_console.emit(msg)
                print_and_log(msg)
                os._exit(-1)

        else:
            try:
                def_index = sd.query_devices(device=sd.default.device, kind='input')
                dev_name = def_index['name']
                msg = "Input Device: " + dev_name
                self.update_console.emit(msg)
                self.input = def_index['name']
                DEVINDEX = sd.default.device
            except IOError as e:
                msg = ("No Input devices: %s" % e[0])
                self.update_console.emit(msg)
                print_and_log(msg)
                os._exit(-1)

                # queue for chunked recording
        global frames
        frames = deque('', dqlength)

        # queue for continous recording
        global replay_frames
        replay_frames = deque('', dqlength)

        msg = ("Listening on UDP port " + str(MYPORT))
        self.update_console.emit(msg)
        print_and_log(msg)

        # define callback
        def callback(in_data, frame_count, time_info, status):
            in_data = in_data[:] #Copy to byte string
            frames.append(in_data)
            # add code for continous recording here
            replay_frames.append(in_data)

        try:
            stream = sd.RawInputStream(dtype=FORMAT,
                                       channels=CHANNELS,
                                       device=DEVINDEX,
                                       samplerate=RATE,
                                       blocksize=CHUNK,
                                       callback=callback)

        except sd.PortAudioError:
            msg = "Failed to attach to device idx " + str(DEVINDEX) + ", " + def_index['name']
            self.update_console.emit(msg)
            print_and_log(msg)
            return
            # exit(255)

        # start the stream
        stream.start()
        self.sampwidth = stream.samplesize

        msg = ("* recording %d ch, %d secs audio buffer, Delay: %d secs" % (CHANNELS, dqlength * CHUNK / RATE, DELAY))
        self.update_console.emit(msg)
        print_and_log(msg)

        msg = ("Output directory: " + self.options.path.replace('\\', '/') + "/<contest...>")
        self.update_console.emit(msg)
        print_and_log(msg)
        msg = ("Hotkey: CTRL+ALT+" + HOTKEY)
        self.update_console.emit(msg)
        print_and_log(msg)

        if self.options.station_nr > 0:
            msg = ("Recording only station " + str(self.options.station_nr) + "QSOs")
            self.update_console.emit(msg)
            print_and_log(msg)
        if self.options.continuous:
            msg = "Full contest recording enabled."
            self.update_console.emit(msg)
            print_and_log(msg)
        msg = "--------------------------------------\n"
        self.update_console.emit(msg)
        print_and_log(msg)

        # start continious mp3 writer thread
        if self.options.continuous:
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
            msg = "Error connecting to the UDP stream."
            self.update_console.emit(msg)
            print_and_log(msg)

        seen = {}
        while stream.active:
            try:
                udp_data = s.recv(2048)
                check_sum = binascii.crc32(udp_data)
                udp_data = udp_data.decode()
                try:
                    dom = parseString(udp_data)
                except xml.parsers.expat.ExpatError as e:
                    pass

                if "qsorder_exit_loop_DEADBEEF" in udp_data or self._isRunning is False:
                    msg = "Received Exit magic signal"
                    self.update_console.emit(msg)
                    print_and_log(msg)
                    if 'mp3' in locals():
                        mp3_stop.set()
                        time.sleep(0.2)
                    if "test_qsorder_exit_loop_DEADBEEF" in udp_data:
                        # special case for automated tests
                        QApplication.quit()
                        logging.debug("Called QApplicationq.quit..")
                    break

                if self.options.debug:
                    logging.debug('UDP Packet Received:')
                    logging.debug(udp_data)

                # skip packet if duplicate
                if check_sum in seen:
                    seen[check_sum] += 1
                    if self.options.debug:
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
                        if timestamp.strftime("%m") != now.strftime("%m"):
                            timestamp = dateutil.parser.parse(qso_timestamp, dayfirst=True)

                        # skip packet if not matching network station number specified in the command line
                        if self.options.station_nr > 0:
                            if self.options.station_nr != station:
                                msg = ("QSO: " + timestamp.strftime("%m-%d %H:%M:%S") + call + " "
                                       + freq + " --- ignoring from stn" + str(station))
                                self.update_console.emit(msg)
                                print_and_log(msg)
                                continue

                        # skip packet if not matching radio number specified in the command line
                        if self.options.radio_nr and self.options.radio_nr >= 0:
                            if self.options.radio_nr != int(radio_nr):
                                msg = ("QSO:", timestamp.strftime("%m-%d %H:%M:%S"), call, freq,
                                       "--- ignoring from radio/VFO", radio_nr)
                                self.update_console.emit(msg)
                                continue

                        # skip packet if QSO was more than options.buffer_length-DELAY seconds ago
                        t_delta = (now - timestamp).total_seconds()
                        if t_delta > self.options.buffer_length - DELAY:
                            msg = ("---: " + timestamp.strftime("%m-%d %H:%M:%S") + call + " "
                                   + freq + " --- ignoring " + str(t_delta) + " sec old QSO. Check clock settings?")
                            self.update_console.emit(msg)
                            print_and_log(msg)
                            continue
                        elif t_delta < -DELAY:
                            msg = ("---: " + timestamp.strftime("%m-%d %H:%M:%S") + call + " "
                                   + freq + " --- ignoring " + str(
                                        -t_delta) + "sec QSO in the 'future'. Check clock settings?")
                            self.update_console.emit(msg)
                            print_and_log(msg)
                            continue

                        calls = call + "_de_" + mycall

                        # take into account UDP buffer delay
                        if t_delta > DELAY:
                            t_delta = DELAY

                        t = threading.Timer(DELAY - t_delta, self._dump_audio,
                                            [calls, contest, mode, freq, timestamp, radio_nr, self.sampwidth])
                        msg = ("QSO: " + timestamp.strftime("%m-%d %H:%M:%S") + " " + call + " " + freq)
                        self.update_console.emit(msg)
                        print_and_log(msg)
                        t.start()
                        self.qsos_in_queue += 1
                    except:
                        if self.options.debug:
                            logging.debug('Could not parse previous packet')
                            logging.debug(sys.exc_info())

                        pass  # ignore, probably some other udp packet

            except KeyboardInterrupt:
                msg = "73! K3IT"
                self.update_console.emit(msg)
                print_and_log(msg)
                stream.stop()
                stream.close()
                exit(0)

        stream.stop()
        stream.close()


def print_and_log(msg):
    print(msg)
    logging.debug(msg)


if __name__ == '__main__':
    qsorder = qsorder_class()
