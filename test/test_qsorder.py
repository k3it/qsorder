import sys
import logging
import unittest

import cProfile, pstats

from Qsorder import qsorder

class ModTest(unittest.TestCase):

	def testTest(self):
		self.assertEqual(2, 2)


if __name__ == '__main__':    
	unittest.main()