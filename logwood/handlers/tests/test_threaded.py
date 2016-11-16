import unittest.mock
import time

import logwood
from logwood.handlers.threaded import ThreadedHandler



def test_underlying_handler_is_called():
	'''
	Assert that underlying handler got called in a thread.
	'''
	underlying_handler = unittest.mock.Mock()
	handler = ThreadedHandler(underlying_handler = underlying_handler)
	logwood.basic_config(level = logwood.DEBUG, handlers = [handler])
	logger = logwood.get_logger('Test')

	logger.error('Error message')
	# After the message we can safely close all handlers
	handler.close()
	# Wait for a while for the scheduler to run our thread
	time.sleep(0.1)
	assert underlying_handler.emit.called
	record = underlying_handler.emit.call_args[0][0]
	assert record['message'] == 'Error message'
	assert underlying_handler.close.called
