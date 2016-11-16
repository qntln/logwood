import unittest
import logwood



def reset_state() -> None:
	'''
	Reset logwood's state. Beware, unexpected logger configuration may show up after this call.
	'''
	logwood.state.config_called = False
	logwood.state.defined_loggers.clear()



class LogwoodTestCase(unittest.TestCase):
	'''
	Base test case for testing logwood features.
	'''

	def setUp(self):
		'''
		We want to reset logwood state before every test so any previous configuration is forgotten.
		'''
		reset_state()
