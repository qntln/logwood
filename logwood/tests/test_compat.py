import logging
import pytest
import unittest.mock
import uuid

import logwood
import logwood.compat



@pytest.fixture
def logwood_handler():
	return unittest.mock.Mock()


@pytest.fixture
def logging_logger(logwood_handler):
	logwood.basic_config(handlers = [logwood_handler])
	logwood.compat.redirect_standard_logging()
	return logging.getLogger(str(uuid.uuid4()))


def test_log(logwood_handler, logging_logger):
	'''
	logging.error gets logged by a logwood handler.
	'''
	logging_logger.error('This is error message %s, %d', 'abc', 123)
	assert logwood_handler.handle.called
	args = logwood_handler.handle.call_args_list[0][0][0]
	args['message'] == 'This is error message abc, 123'
	args['level'] == 'ERROR'


def test_log_with_object_args(logwood_handler, logging_logger):
	logging_logger.error('This is error message %r', {'a': 5, 'b': 6})
	assert logwood_handler.handle.called
	args = logwood_handler.handle.call_args_list[0][0][0]
	assert 'This is error message' in args['message']
	assert "'a': 5" in args['message']
	assert "'b': 6" in args['message']
	assert args['level'] == 'ERROR'
