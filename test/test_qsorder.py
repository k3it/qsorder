import sys
import logging
import unittest
from nose.tools import timed
from time import sleep
import time

import cProfile, pstats

from Qsorder import qsorder

import mock
from socket import *
import threading

import xml.etree.cElementTree as ET
import datetime


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
		sleep(1)

		# data = repr(time.time()) + '\n'
		s.sendto(udp_packet, ('<broadcast>', MYPORT))
		sleep(delay_before_exit)
		udp_packet = "qsorder_exit_loop_DEADBEEF"
		s.sendto(udp_packet, ('<broadcast>', MYPORT))



class checkUDPparsing(object):
	def __init__(self,udp_packet,delay_before_exit=1,argslist=None):
		t = threading.Thread(target=simpleUDPBcast, args=(udp_packet,delay_before_exit))
		t.setDaemon(True)
		t.start()
		if argslist:
			argslist.append('-P ' + str(MYPORT))
		else:
			argslist = ['-P ' + str(MYPORT)]

		qsorder.main(argslist)
		 
	def get_output(self):
		return sys.stdout.getvalue()



class ModTest(unittest.TestCase):

	def testCheckExit(self):
		argslist = ['-h']
		with self.assertRaises(SystemExit):
			qsorder.main(argslist=argslist)
		verification_output = "show this help message and exit"
		self.assertIn(verification_output, sys.stdout.getvalue())


	def testIndex(self):
		with self.assertRaises(SystemExit):
			argslist = ['-q']
			qsorder.main(argslist)
		verification_output = "Device index Description"
		self.assertIn(verification_output, sys.stdout.getvalue())

	def testDelay(self):
		# with self.assertRaises(SystemExit):
		argslist = ['-d 2', '-i 0', '-D']
		output = checkUDPparsing("None",argslist=argslist).get_output()
		verification_output = "Delay: 2 secs"
		self.assertIn(verification_output, sys.stdout.getvalue())


	def test_corrupted_udp(self):
		data = ET.parse("test/udp-test-packet.xml").getroot()
		data.find('timestamp').text = "blah"
		udp_packet = ET.tostring(data)
		output = checkUDPparsing(udp_packet).get_output()
		verification_output = "Exit"
		self.assertIn(verification_output, output)

	
	def test_old_qso(self):
		'''
		Should ignore QSOs in the "past"
		'''
		data = ET.parse("test/udp-test-packet.xml").getroot()
		udp_packet = ET.tostring(data)
		output = checkUDPparsing(udp_packet).get_output()
		verification_output = "ignoring"
		self.assertIn(verification_output, output)

	def test_future_qso(self):
		'''
		Should ignore QSOs in the "future"
		'''
		data = ET.parse("test/udp-test-packet.xml").getroot()
		now = datetime.datetime.utcnow()
		now += datetime.timedelta(1)
		argslist = ['-d 3']

		data.find('timestamp').text = now.strftime("%Y-%m-%d %H:%M:%S")
		udp_packet = ET.tostring(data)
		output = checkUDPparsing(udp_packet,argslist=argslist).get_output()
		verification_output = "ignoring"
		self.assertIn(verification_output, output)

	def test_qso(self):
		'''
		save a basic QSO
		'''
		data = ET.parse("test/udp-test-packet.xml").getroot()
		now = datetime.datetime.utcnow()
		now += datetime.timedelta(0,3)

		argslist = ['-d 2']

		data.find('timestamp').text = now.strftime("%Y-%m-%d %H:%M:%S")
		udp_packet = ET.tostring(data)
		output = checkUDPparsing(udp_packet,argslist=argslist,delay_before_exit=3).get_output()
		verification_output = "WAV:"
		self.assertIn(verification_output, output)
		# check for mp3 conversion also
		verification_output = "ReplayGain:"
		self.assertIn(verification_output, output)

	def testContinous(self):
		# with self.assertRaises(SystemExit):
		argslist = ['-C']
		output = checkUDPparsing("None",argslist=argslist).get_output()
		verification_output = "started new .mp3 file:"
		self.assertIn(verification_output, sys.stdout.getvalue())
		verification_output = "Disk free space:"
		self.assertIn(verification_output, sys.stdout.getvalue())





if __name__ == '__main__':    
	unittest.main()