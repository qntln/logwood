import pytest
import unittest.mock

import logwood.testing

import logwood
from logwood.logger import Logger



@pytest.fixture
def handler():
	return unittest.mock.Mock()


@pytest.fixture
def logger(handler):
	logwood.basic_config(handlers = [])
	return Logger('TestLogger', [handler])


@pytest.mark.parametrize('method,level', [
	('debug', 'DEBUG'),
	('info', 'INFO'),
	('warning', 'WARNING'),
	('error', 'ERROR'),
	('fatal', 'FATAL'),
	('critical', 'FATAL'),
])
def test_logging_all_levels(handler, logger, method, level):
	getattr(logger, method)('Test message', 1, 2, 3)
	assert handler.handle.called
	args = handler.handle.call_args_list[0][0][0]
	assert args['message'] == 'Test message'
	assert args['args'] == (1, 2, 3,)
	assert args['level'] == level
	assert args['level_number'] == getattr(logwood, level)


def test_additional_handler(handler, logger):
	handler = unittest.mock.Mock()
	logger.add_handler(handler)
	logger.error('Test Message')
	assert handler.handle.called


def test_exception(handler, logger):
	try:
		raise ValueError('My value error')
	except ValueError as e:
		logger.exception('Raised exception')
		assert handler.handle.called
		message = handler.handle.call_args_list[0][0][0]['args'][0]
		assert 'Traceback' in message
		assert 'My value error' in message
		assert 'ValueError' in message
