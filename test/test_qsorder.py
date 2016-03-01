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


MYPORT = 50000


class simpleUDPBcast(object):
	'''
	Send a udp packet to qsorder port, followed by a magic exit packet
	'''
	def __init__(self,udp_packet):
		# Send UDP broadcast packets

		s = socket(AF_INET, SOCK_DGRAM)
		s.bind(('', 0))
		s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

		sleep(1)
		# data = repr(time.time()) + '\n'
		s.sendto(udp_packet, ('<broadcast>', MYPORT))
		udp_packet = "qsorder_exit_loop_DEADBEEF"
		s.sendto(udp_packet, ('<broadcast>', MYPORT))



class checkUDPparsing(object):
	def __init__(self,udp_packet):
		t = threading.Thread(target=simpleUDPBcast, args=(udp_packet,))
		t.setDaemon(True)
		t.start()
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


	def test_corrupted_udp(self):
		data = ET.parse("test/udp-test-packet.xml").getroot()
		data.find('timestamp').text = "blah"
		udp_packet = ET.tostring(data)
		output = checkUDPparsing(udp_packet).get_output()
		verification_output = "Exit"
		self.assertIn(verification_output, output)

	
	def test_old_qso(self):
		data = ET.parse("test/udp-test-packet.xml").getroot()
		udp_packet = ET.tostring(data)
		output = checkUDPparsing(udp_packet).get_output()
		verification_output = "ignoring"
		self.assertIn(verification_output, output)




if __name__ == '__main__':    
	unittest.main()