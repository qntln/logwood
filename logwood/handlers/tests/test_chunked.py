import unittest.mock

import logwood
from logwood.handlers.chunked import ChunkedSysLogHandler



@unittest.mock.patch('socket.socket')
def test_chunk_short_message(socket):
	message = 'Short message'

	handler = ChunkedSysLogHandler(address = '/not/existing', chunk_size = len(message))
	logwood.basic_config(format = '%(message)s', handlers = [handler])

	logger = logwood.get_logger('Test')
	logger.error(message)

	# Do not call parent emit more then once for a short message
	assert handler.socket.send.call_count == 1

	# It was called just once (first zero) and we read the record (second zero)
	assert message in str(handler.socket.send.call_args[0][0])


@unittest.mock.patch('socket.socket')
def test_chunk_long_message(socket):
	message = '1234567890' * 100

	handler = ChunkedSysLogHandler(address = '/not/existing', chunk_size = 10)
	logwood.basic_config(format = '%(message)s', handlers = [handler])

	logger = logwood.get_logger('Test')
	logger.error(message)

	# We have chunk size 10 so emit should be called 100 times
	assert handler.socket.send.call_count == 100
