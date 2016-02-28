import sys
import logging
import unittest
from nose.tools import timed
from time import sleep
import time

import cProfile, pstats

from Qsorder import qsorder

# import mock
from socket import *
import threading


MYPORT = 50000


class simpleUDPBcast(object):
	def __init__(self):
		# Send UDP broadcast packets


		s = socket(AF_INET, SOCK_DGRAM)
		s.bind(('', 0))
		s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

		while True:
		    data = repr(time.time()) + '\n'
		    s.sendto(data, ('<broadcast>', MYPORT))
		    sleep(2)
		    data = "qsorder_exit_loop_DEADBEEF"
		    s.sendto(data, ('<broadcast>', MYPORT))



class ModTest(unittest.TestCase):

	def testTest(self):
		self.assertEqual(2, 2)

	def testCheckExit(self):
		argslist = ['-h']
		with self.assertRaises(SystemExit):
			qsorder.main(argslist=argslist)


	def testIndex(self):
		argslist = ['-q']
		qsorder.main(argslist)

	t = threading.Thread(target=simpleUDPBcast)
	t.setDaemon(True)
	t.start()

	def test_a(self):
		argslist = ['-P ' + str(MYPORT)]
		qsorder.main(argslist)

	

if __name__ == '__main__':    
	unittest.main()