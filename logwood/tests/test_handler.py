from typing import Dict
import pytest
import unittest.mock

import logwood



@pytest.fixture
def handler():
	class TestHandlerImplementation(logwood.Handler):
		''' Test implementation of handler with mocked emit '''
		emit = None # overwrite the abstract method

		def __init__(self) -> None:
			super().__init__()
			self.emit = unittest.mock.Mock()

		def get_emit_record(self) -> Dict[str, str]:
			''' Return first record '''
			return self.emit.call_args_list[0][0][0]

	return TestHandlerImplementation()


@pytest.fixture
def logger(handler):
	logwood.basic_config(
		level = logwood.WARNING,
		handlers = [handler,]
	)
	return logwood.get_logger('TestLogger')


def test_handle_and_emit_called(handler, logger):
	'''
	Handle, and then emit are called.
	'''
	logger.warning('Warning message')
	# Test that emit was called
	assert handler.emit.called
	assert handler.get_emit_record()['message'] == 'Warning message'


def test_level_filter(handler, logger):
	'''
	When the level is below the threshold emit is not called.
	'''
	logger.info('Debug message')
	assert not handler.emit.called


def test_format_massage(handler, logger):
	'''
	Test argument replacements.
	'''
	# Log with variables
	variable1 = 123456789
	variable2 = 'Message'
	logger.warning('Something with id %d went wrong: %s', variable1, variable2)

	assert handler.emit.called
	record = handler.get_emit_record()

	# Variables should be in args
	assert variable1 in record['args']
	assert variable2 in record['args']

	# Get formated message
	message = handler.format_message(record)
	assert '[WARNING] Something with id 123456789 went wrong: Message' in message

	# Args must be removed after message is formatted
	assert 'args' not in record


def test_format_message_str_format(handler, logger):
	'''
	Test argument replacement with ``str.format()`` instead of %-format.
	'''
	# Log with variables
	variable1 = 123456789
	variable2 = 'Message'
	logger.warning('Something with id {:d} went wrong: {}', variable1, variable2)

	assert handler.emit.called
	record = handler.get_emit_record()

	# Variables should be in args
	assert variable1 in record['args']
	assert variable2 in record['args']

	# Get formated message
	message = handler.format_message(record)
	assert '[WARNING] Something with id 123456789 went wrong: Message' in message

	# Args must be removed after message is formatted
	assert 'args' not in record


def test_format_message_prefers_str_format(handler, logger):
	'''
	Test that in case of indecision ``str.format()`` is used for formatting.
	'''
	logger.warning('Either {} or %s', 'THIS')
	record = handler.get_emit_record()
	message = handler.format_message(record)
	assert '[WARNING] Either THIS or %s' in message


def test_handler_message_str_format(handler, logger):
	'''
	Test that ``handler.format()`` may be formatted with ``str.format()``.
	'''
	handler.format = "[{timestamp}][{hostname}][{system_identifier}][{level:*^11}] {message}"
	logger.warning('Message with no meaning at all.')
	record = handler.get_emit_record()
	message = handler.format_message(record)
	assert '[**WARNING**] Message with no meaning at all.' in message


def test_exception_with_percent_arg(handler, logger):
	'''
	Test that a raised exception log can have a percent style argument.
	'''
	try:
		raise ValueError('My value error')
	except ValueError as e:
		logger.exception('Raised exception %s', 123)
	record = handler.get_emit_record()
	message = handler.format_message(record)
	assert '[ERROR] Raised exception 123' in message


def test_exception_with_str_format_arg(handler, logger):
	'''
	Test that a raised exception log can have ``str.format`` style argument.
	'''
	try:
		raise ValueError('My value error')
	except ValueError as e:
		logger.exception('Raised exception {}', 123)
	record = handler.get_emit_record()
	message = handler.format_message(record)
	assert '[ERROR] Raised exception 123' in message
