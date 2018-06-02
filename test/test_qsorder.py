import sys
import logging
import unittest
from nose.tools import timed
from time import sleep
import time

import cProfile, pstats

from pyQsorder import qsorder

import mock
from socket import *
import threading

import xml.etree.cElementTree as ET
import datetime, os


MYPORT = 50000


class simpleUDPBcast(object):
	'''
	Send a udp packet to qsorder port, followed by a magic exit packet
	'''
	def __init__(self,udp_packet,delay_before_exit):
		# Send UDP broadcast packets

		s = socket(AF_INET, SOCK_DGRAM)
		s.bind(('', 0))
		s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

		# wait for qsorder to start
		sleep(3)

		# data = repr(time.time()) + '\n'
		try:
			udp_packet = udp_packet.encode()
		except:
			pass
		s.sendto(udp_packet, ('<broadcast>', MYPORT))

		sleep(delay_before_exit)
		udp_packet = "test_qsorder_exit_loop_DEADBEEF"
		s.sendto(udp_packet.encode(), ('<broadcast>', MYPORT))



class checkUDPparsing(object):
	def __init__(self,udp_packet,delay_before_exit=1,argslist=None):
		t = threading.Thread(target=simpleUDPBcast, args=(udp_packet,delay_before_exit))
		t.setDaemon(True)
		t.start()
		if argslist:
			argslist.append('-P ' + str(MYPORT))
		else:
			argslist = ['-P ' + str(MYPORT)]
		qsorder.qsorder(argslist)

	def get_output(self):
		return sys.stdout.getvalue()

class ModTest(unittest.TestCase):
	

	def testDropboxConnect(self):
		drop_key = os.environ['DROP_KEY']
		logging.debug("drop key: " + drop_key[-3:])

		with self.assertRaises(SystemExit):
			argslist = ['-u' + drop_key, '-d 2']
			now = datetime.datetime.utcnow()
			now += datetime.timedelta(0,3)
			data = ET.parse("test/udp-test-packet.xml").getroot()
			data.find('timestamp').text = now.strftime("%Y-%m-%d %H:%M:%S")
			data.find('call').text = "TE5T"
			udp_packet = ET.tostring(data)
			output = checkUDPparsing(udp_packet,argslist=argslist,delay_before_exit=7).get_output()
		verification_output = "WAV: Uploaded"
		self.assertIn(verification_output, sys.stdout.getvalue())

	def testCheckExit(self):
		argslist = ['-h']
		with self.assertRaises(SystemExit):
			qsorder.qsorder(argslist=argslist)
		verification_output = "show this help message and exit"
		self.assertIn(verification_output, sys.stdout.getvalue())


	def testIndex(self):
		with self.assertRaises(SystemExit):
			argslist = ['-q']
			qsorder.qsorder(argslist)
		verification_output = "Device index Description"
		self.assertIn(verification_output, sys.stdout.getvalue())

	def testDelay(self):
		with self.assertRaises(SystemExit):
			argslist = ['-d 2', '-i 0', '-D']
			output = checkUDPparsing("None",argslist=argslist).get_output()
		verification_output = "Delay: 2 secs"
		self.assertIn(verification_output, sys.stdout.getvalue())
		# with self.assertLogs(level='DEBUG') as cm:
		# 	self.assertIn(verification_output, cm.output)


	def test_corrupted_udp(self):
		with self.assertRaises(SystemExit):
			data = ET.parse("test/udp-test-packet.xml").getroot()
			data.find('timestamp').text = "blah"
			udp_packet = ET.tostring(data)
			output = checkUDPparsing(udp_packet).get_output()
		verification_output = "Exit"
		self.assertIn(verification_output, sys.stdout.getvalue())

	
	def test_old_qso(self):
		'''
		Should ignore QSOs in the "past"
		'''
		with self.assertRaises(SystemExit):
			data = ET.parse("test/udp-test-packet.xml").getroot()
			udp_packet = ET.tostring(data)
			output = checkUDPparsing(udp_packet).get_output()
		verification_output = "ignoring"
		self.assertIn(verification_output, sys.stdout.getvalue())

	def test_future_qso(self):
		'''
		Should ignore QSOs in the "future"
		'''
		with self.assertRaises(SystemExit):
			data = ET.parse("test/udp-test-packet.xml").getroot()
			now = datetime.datetime.utcnow()
			now += datetime.timedelta(1)
			argslist = ['-d 3', '-S', '-D']

			data.find('timestamp').text = now.strftime("%Y-%m-%d %H:%M:%S")
			udp_packet = ET.tostring(data)
			output = checkUDPparsing(udp_packet,argslist=argslist).get_output()
		verification_output = "ignoring"
		self.assertIn(verification_output, sys.stdout.getvalue())

	def test_qso(self):
		'''
		save a basic QSO
		'''
		with self.assertRaises(SystemExit):
			data = ET.parse("test/udp-test-packet.xml").getroot()
			now = datetime.datetime.utcnow()
			now += datetime.timedelta(0,3)

			argslist = ['-d 2', '-p tmp']

			data.find('timestamp').text = now.strftime("%Y-%m-%d %H:%M:%S")
			udp_packet = ET.tostring(data)
			output = checkUDPparsing(udp_packet,argslist=argslist,delay_before_exit=5).get_output()
		verification_output = "WAV:"
		self.assertIn(verification_output, sys.stdout.getvalue())
		# check for mp3 conversion also
		verification_output = "ReplayGain:"
		self.assertIn(verification_output, sys.stdout.getvalue())

	def testContinous(self):
		# with self.assertRaises(SystemExit):
		with self.assertRaises(SystemExit):
			argslist = ['-C']
			output = checkUDPparsing("None",argslist=argslist).get_output()
		verification_output = "started new .mp3 file:"
		self.assertIn(verification_output, sys.stdout.getvalue())
		verification_output = "Disk free space:"
		self.assertIn(verification_output, sys.stdout.getvalue())





if __name__ == '__main__':    
	unittest.main()