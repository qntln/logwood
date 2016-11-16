import unittest.mock

import logwood
import logwood.handlers.logging



def test_SysLogHandler_emit():
	'''
	Test that the refactored syslog handler's emit is working.
	'''
	with unittest.mock.patch('socket.socket'):
		handler = logwood.handlers.logging.SysLogHandler()
		logwood.basic_config(handlers = [handler])
		logger = logwood.get_logger('Test')

	logger.warning('Warning')
	assert handler.socket.sendto.called
