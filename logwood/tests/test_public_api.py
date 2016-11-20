import gc
import pytest
import unittest.mock

import logwood.testing

import logwood
import logwood.state
import logwood.global_config



def test_basic_config():
	'''
	Test basic logging setup.
	'''
	handler1, handler2 = unittest.mock.Mock(), unittest.mock.Mock()

	msg_format = 'MSG: %(message)s'
	logwood.basic_config(
		format = msg_format,
		level = logwood.DEBUG,
		handlers = [handler1, handler2]
	)

	assert handler1 in logwood.global_config.default_handlers
	assert handler2 in logwood.global_config.default_handlers

	assert logwood.global_config.default_format == msg_format
	assert logwood.global_config.default_log_level == logwood.DEBUG


def test_get_logger():
	'''
	get_logger returns a logger with configured handlers.
	'''
	handler1, handler2, handler3 = unittest.mock.Mock(), unittest.mock.Mock(), unittest.mock.Mock()
	logwood.basic_config(
		level = logwood.DEBUG,
		handlers = [handler1, handler2]
	)

	logger = logwood.get_logger('Test')
	logger.add_handler(handler3)

	assert handler1 not in logger.handlers
	assert handler2 not in logger.handlers
	assert handler3 in logger.handlers

	logger.error('Error')

	assert handler1.handle.call_count == 1
	assert handler2.handle.call_count == 1
	assert handler3.handle.call_count == 1


def test_get_logger_before_basic_config():
	'''
	A Logger instance cannot be created before a call to basic_config.
	'''
	with pytest.raises(AssertionError):
		logwood.get_logger('Test')



def test_calling_basic_config_multiple_times():
	'''
	After first logger is created a call to basic_config should raise an exception.
	'''
	handler1, handler2 = unittest.mock.Mock(), unittest.mock.Mock()
	logwood.basic_config(
		level = logwood.DEBUG,
		handlers = [handler1, handler2]
	)
	assert logwood.state.config_called

	# But until the first logger is created it can be called multiple times
	logwood.basic_config(handlers = [])
	logwood.basic_config(handlers = [])

	# now create some loggers
	logwood.get_logger('A')
	logwood.get_logger('B')
	logwood.get_logger('C')

	# Created loggers should be defined in state
	assert len(logwood.state.defined_loggers) == 3

	# After loggers are created it is impossible to change logging settings
	with pytest.raises(AssertionError):
		logwood.basic_config(handlers = [])


def test_logger_caching():
	'''
	Test that loggers are properly cached
	'''
	logwood.basic_config(handlers = [], level = logwood.DEBUG)

	logger = logwood.get_logger('A')
	logger2 = logwood.get_logger('A')

	# Those two loggers should be completely the same
	assert logger is logger2

	# Store logger id so we can compare it later
	logger_id = id(logger)

	# Try to send something
	logger.info('Test message')
	logger2.info('Test message')

	# Then delete both loggers
	del logger
	del logger2

	# Collect all removed instances
	gc.collect()

	logger3 = logwood.get_logger('A')
	assert logger_id != id(logger3)
