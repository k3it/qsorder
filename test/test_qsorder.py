import sys
import logging
import unittest

import cProfile, pstats

from Qsorder import qsorder

class ModTest(unittest.TestCase):

	def testTest(self):
		self.assertEqual(2, 2)

	def testCheckExit(self):
		argslist = ['-h']
		with self.assertRaises(SystemExit):
			qsorder.main(argslist=argslist)


if __name__ == '__main__':    
	unittest.main()