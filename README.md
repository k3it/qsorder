[![Coverage Status](https://coveralls.io/repos/github/k3it/qsorder/badge.svg?branch=master)](https://coveralls.io/github/k3it/qsorder?branch=master)
[![Build Status](https://travis-ci.org/k3it/qsorder.svg?branch=master)](https://travis-ci.org/k3it/qsorder)
[![Documentation Status](https://readthedocs.org/projects/qsorder/badge/?version=latest)](http://qsorder.readthedocs.org/en/latest/?badge=latest)
                

qsorder - audio recordig app for N1MM and TR4W contest QSOs.
================================================================
Download stable windows executable under [Releases](https://github.com/k3it/qsorder/releases)


![screenshot](https://raw.githubusercontent.com/k3it/qsorder/master/qsorder.png)

qsorder.exe - a console app for audio recordimg of N1MM contest QSOs.

v2.13

this is an external "plug-in" for N1MM which adds a QSO audio recording function. qsorder maintains a buffer in memory and listens for "Contact" UDP broadcasts sent by the logging program. The broadcasts trigger a dump of the audio buffer to a file after a specified delay time (default is 20 secs). The delay helps with capturing a tail-end after a QSO was entered into the log.

# Basic usage

Download and unpack both the qsorder executable and lame.exe to the directory which will contain the contest audio (e.g. c:\contest-qsos\). If prefer to save uncompressed WAV files instead of mp3's then simply delete lame.exe. ('Lame' is a very fast, free MP3 encoder)

Find the [ExternalBroadcast] section in your N1MM Logger.ini and include the lines below. This enables local QSO info UDP broadcast. For more info see N1MM UDP documentation. Restart N1MM after making changes.

(alternative instructions here: http://n1mm.hamdocs.com/tiki-index.php?page=Third+Party+Software#QSOrder_by_Vasily_K3IT_ )


_N1MM+: files should be extracted to ..Documents\N1MM Logger+\QsoRecording in order to play correctly from the N1MM+ log window._


```
[ExternalBroadcast]
DestinationIPs=127.0.0.1
DestinationPort=12060
IsBroadcastContact=True
```
Alternate broadcast configuration example (N1MM v13 and up):
```
[ExternalBroadcast]
BroadcastContactAddr=127.0.0.1:12060
IsBroadcastContact=True
```

In recent versions of N1MM+ it is no longer necessary to edit the .ini file directly. All configuration can be done throught the GUI:

1) launch N1MM+
2) on the entry window, select Config, then Configure Ports, Mode Control, Audio, Other..
3) Click on the Broadcast Data tab.
4) Tic the box labeled Contact.  

_Addtl note from Victor WB0TEV_: There is also a box next to it labelled All QSOs, I'm not sure what that one does, but I notice that I checked it on the laptop I used in Belize.  I'm not sure if that was necessary or superfulous.  I don't seem to have that box checked on my desktop computer in my home ham shack.  I guess I need to read the N1MM+ documentation to learn more.  After checking that box QSOrder started working as intended.


Start qsorder.exe. If prompted by the Windows Firewall software make sure you allow local network communication. qsorder should tell you which audio input was selected. If it's not the right one, go to windows audio settings and change the "Default Recording Device" to the one you like. (note: rec input selection flag is not yet implemented)
Make QSOs in N1MM. 

Pressing a HOTKEY (CTRL+ALT+M or specified with --hot-key option) will save the current audio buffer to a file in AUDIO_YYYY directory.  The hotkey should be recognized even when qsorder window is not in focus. Use this key whenever you hear something interesting, outside of a normal QSO (even when N1MM is not running!)

the audio files are saved to a subdirectory `<contest>-<year>`. Note that only a parital file name is printed to save screen space.

ReplayGain indicates the perceived loudness of the recording as reported by lame. This info is also embedded to mp3 files.

to stop qsorder either close the command window or Ctrl-Break. (the window may not react to a Ctrl-C right away - this is normal;)
This is it. For any feedback please post a comment at the SF or email k3it
Advanced usage

qsorder supports optional command line flags:

# Advanced Usage: qsorder.py [options]

```
Options:

  -h, --help            show this help message and exit
  -D, --debug           Save debug info[default=False]
  -d DELAY, --delay=DELAY
                        Capture x seconds after QSO log entry [default=20]
  -i DEVICE_INDEX, --device-index=DEVICE_INDEX
                        Index of the recording input (use -q to list)
                        [default=none]
  -k HOT_KEY, --hot-key=HOT_KEY
                        Hotkey for manual recording Ctrl-Alt-<hot_key>
                        [default=O]
  -l BUFFER_LENGTH, --buffer-length=BUFFER_LENGTH
                        Audio buffer length in secs [default=45]
  -C, --continuous      Record continuous audio stream in addition to
                        individual QSOs[default=False]
  -P PORT, --port=PORT  UDP Port [default=12060]
  -p PATH, --path=PATH  Base directory for audio files [default=none]
  -q, --query-inputs    Query and print input devices [default=False]
  -S, --so2r            SO2R mode, downmix to mono: Left Ch - Radio1 QSOs,
                        Right Ch - Radio2 QSOs [default=False]
  -s STATION_NR, --station-nr=STATION_NR
                        Network Station Number [default=none]
  -R SAMPLE_RATE, --sample-rate SAMPLE_RATE
                        Audio sampling rate [default=11025]
```

Multi Multi Configuration Example N1MM Logger.ini file   
```
  Station 0 should be  DestinationPort=12060
 	Station 1 should be  DestinationPort=12061
 	Station 2 should be  DestinationPort=12062
 	And use --port option 

	Alternatively set staion NR  using --station-nr option
  	(tnx ve2ebk)
```   


# Additional info

written in python 2.7, using threading and pyaudio libraries:

Main Thread - listens for UDP broadcasts from N1MM on port 12060

Sound card I/O thread - maintains a double ended FIFO audio buffer of the specified length (default: 45 secs)

File I/O thread(s) - dump_audio function saves the buffer to a wav file and (optionally) converts to mp3 using lame encoder. This function uses threading.timer module for scheduling

python script is repackaged into a windows executable with pyinstaller.

Tips for audio input: when possible use an isolation transformer (salvage from an old modem). For Mic In recordings use an attenuator to prevent hiss and clipping.


# Hardware notes

WB0TEV:
> Also in regards to QSOrder, when I first tested it out here at home (just before going to Belize) I found that I was only getting the RX audio, but not the audio of me speaking into the microphone.  At home I'm using a TS-590SG and passing audio to/from my computer using the USB CODEC in the TS-590.  I wanted to know if there was a way to also get the audio from the TS-590SG's front panel microphone into the USB CODEC stream so that QSOrder would pick it up as well.  A post to the TS590 Yahoo group yielded the answer.  Its pretty obscure but the answer is to select Menu 75 (called Mixing Beep Tones for ACC2/USB Audio Output) and set it to ON.  That worked.  On the earlier TS590 models (not SG) its a different Menu # (68? I think).  

> When in Belize, the set up in the rental shack  had an IC-7300 and microHam interface into which I plug the microphone connector from my headset.   One of the audio feeds I found with qsorder -q  had both the RX and TX audio in it and so I used it.  I can't explain how it worked, it just did.  I think it was a USB CODEC stream to/from the microHam interface box.

# Change history
v2.13
  - include MSVC redistributable
  - rebuild with cx_freeze and make installable package (MSI)
  - Add Id tags to the MP3 files

v2.12
  - hotkey function is back
  - attempt to guess recording devices charset

v2.11
  - small fixes related to non-ascii character handling
  - convert code to python 3 format

v2.10
 - add radio_nr flag. records qso's only from a specified Radio NR

v2.9
 - minor bug fixes
 - restructured code in prep for the qtgui version
 - xml parsing exception handling

v2.8
 - uninterrupted recording mode (with the -C or "--continuous" flag), parrallel to recording of individual QSOs
   hourly audio files are saved in the AUDIO_YEAR directory, a new mp3 file is created at the top of each hour.
   Extra Disk space required for this option: ~360 MB per 24 hours
 - increased sampling rate from 8000 to 11025
 - pyaduio library updated to version 0.2.8 https://people.csail.mit.edu/hubert/pyaudio/
 - allow cp1251 character set in the recording device names (tnx ua9lif)
 
v2.7
 - pyinstaller updated to 2.1 https://github.com/pyinstaller/pyinstaller/wiki

v2.6b
input selection options, debug option, skip old qsos
	- new flags -q, -i, -D to allow sound input selection and the debug log.
	- skip udp packets for old QSO, for example ignore QSO edits

v2.5b
 - fixes for N1MM integration issues. Play Contact now works for phone contests 
 - SO2R Mode (--so2r flag).  Connect Left Radio to Left audio channel, Right Radio to the Right channel.  
     In this mode QSORDER will downmix the "active" audio input to MP3 mono, and mute the "inactive" radio input. 
     In other words - Radio 1 QSOs will be recorded from the Left Ch, Radio 2 QSOs - from the Right Ch.
     without this flag both Left and Right channels are saved to a stereo file.
     HOT KEY - always saves in stereo
 - yet another change of the default global hot-key (to CTRL-ALT-O)
 - see BUGS.txt for known issues with qsorder


v2.4b
change to CTRL-ALT-M as the default hot-key. 
Bug fix in mp3 conversion routine

v2.3b
added a global hot-key (default CTRL+ALT+R).  
  pushing the hotkey immediately saves the current audio buffer to a file.  
  (qsorder window does not need to be in focus).  
improvement in file/directory naming


v2.2b
added UDP --port and --station-nr options for Multi-Multi setups

v2.1b
added optional -l (buffer length), -d (delay), -p (path), command line flags
added conversion to mp3 with (included) lame.exe encoder
fix handling of / in callsigns
add ReplayGain indicator to the output
save audio files into a <contest-year> directory
v2.1a

initial version (tnx n4zr,dk8nt,n2ic and others)

Future plans:
Audio input selection - DONE
Integration with N1MM log GUI (if N1MM team's time permits) - DONE
Integration with iTunes (just kidding)


73! Vasiliy K3IT
