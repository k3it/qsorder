import sys
import logging
import unittest
from nose.tools import timed
from time import sleep


import cProfile, pstats

from Qsorder import qsorder

class ModTest(unittest.TestCase):

	def testTest(self):
		self.assertEqual(2, 2)

	def testCheckExit(self):
		argslist = ['-h']
		with self.assertRaises(SystemExit):
			qsorder.main(argslist=argslist)

	@timed(2)
	def test_a(self):
		sleep(3)


if __name__ == '__main__':    
	unittest.main()