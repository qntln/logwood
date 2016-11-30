import unittest
import pytest

import logwood
import logwood.handlers.stderr
import logwood.state
import logwood.logger
import logwood.base_handler
import logwood.constants



def reset_state() -> None:
	'''
	Reset logwood's state. Beware, unexpected logger configuration may show up after this call.
	'''
	logwood.state.config_called = False
	logwood.state.defined_loggers.clear()
	logwood.shutdown()
	logwood.state.defined_handlers.clear()



class LogwoodTestCase(unittest.TestCase):
	'''
	Base test case for testing logwood features.
	'''

	def setUp(self):
		'''
		We want to reset logwood state before every test so any previous configuration is forgotten.
		'''
		reset_state()



class MockLogwoodHandler(logwood.base_handler.Handler):
	'''
	This handler stores all messages instead of emitting for later asserting.
	'''

	def __init__(self, *args, **kwargs):
		self._messages = {level: [] for level in logwood.constants.LOG_LEVEL_NAMES.values()}
		super().__init__(*args, **kwargs)


	def emit(self, record):
		self._messages[record['level']].append(self.format_message(record))


	def __getitem__(self, item):
		try:
			# item is uppercase string, e.g. 'ERROR'
			return self._messages[item]
		except KeyError:
			try:
				# item is logging level number, e.g. logwood.ERROR
				return self._messages[logwood.constants.LOG_LEVEL_NAMES[item]]
			except KeyError:
				# item is string but not uppercase, e.g. 'error'
				return self._messages[item.upper()]



@pytest.fixture
def logwood_handler_mock():
	# we want to store every level and only message, no metadata
	return MockLogwoodHandler(level = logwood.DEBUG, format = '%(message)s')



@pytest.fixture(autouse = True)
def configure_and_reset_logwood(logwood_handler_mock):
	'''
	Make sure Logwood is always configured, otherwise no loggers can be instantiated.
	This fixture automatically runs around each testcase in pytests that import logwood.
	All messages are sent to stderr and saved to `logwood_handler_mock`.
	'''
	logwood.basic_config(handlers = [logwood.handlers.stderr.ColoredStderrHandler(), logwood_handler_mock])
	yield
	reset_state()
