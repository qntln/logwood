import logwood
import timeit

import logwood.testing

from logwood.handlers.logging import FileHandler, SysLogHandler
from logwood.handlers.syslog import SysLogLibHandler
from logwood.handlers.stderr import ColoredStderrHandler
from logwood.handlers.threaded import ThreadedHandler



def original_logging_std_err():
	'''
	Orignal logging module with stderr handler.
	'''
	import logging
	logwood.testing.reset_state()
	logging.basicConfig(format = '%(message)s', handlers = [
		logging._StderrHandler()
	])
	return logging.getLogger(__name__)


def original_logging_syslog():
	'''
	Orignal logging module with syslog handler.
	'''
	import logging, logging.handlers
	logwood.testing.reset_state()
	logging.basicConfig(format = '%(message)s', handlers = [
		logging.handlers.SysLogHandler()
	])
	return logging.getLogger(__name__)


def no_handler():
	'''
	Logwood with no handlers.
	'''
	logwood.basic_config(handlers = [])
	logger = logwood.get_logger(__name__)
	return logger


def std_err_handler():
	'''
	Logwood with stderr handler.
	'''
	logwood.testing.reset_state()
	logwood.basic_config(handlers = [
		ColoredStderrHandler(logwood.DEBUG)
	])
	logger = logwood.get_logger(__name__)
	return logger


def syslog_lib_handler():
	'''
	Logwood with syslog library handler.
	'''
	logwood.testing.reset_state()
	logwood.basic_config(handlers = [
		SysLogLibHandler()
	])
	logger = logwood.get_logger(__name__)
	return logger


def syslog_handler():
	'''
	Logwood with syslog handler.
	'''
	logwood.testing.reset_state()
	logwood.basic_config(handlers = [
		SysLogHandler()
	])
	logger = logwood.get_logger(__name__)
	return logger


def syslog_threaded_handler():
	'''
	Logwood with syslog handler run via ThreadedHandler.
	'''
	logwood.testing.reset_state()
	logwood.basic_config(handlers = [
		ThreadedHandler(underlying_handler = SysLogHandler())
	])
	logger = logwood.get_logger(__name__)
	return logger


def file_handler():
	'''
	Logwood with FileHandler.
	'''
	logwood.testing.reset_state()
	logwood.basic_config(handlers = [
		FileHandler(filename = 'example.log')
	])
	logger = logwood.get_logger(__name__)
	return logger



if __name__ == '__main__':
	methods = (
		original_logging_std_err,
		original_logging_syslog,
		no_handler,
		syslog_lib_handler,
		syslog_handler,
		syslog_threaded_handler,
		file_handler,
		std_err_handler,
	)

	for test in methods:
		t = timeit.timeit('logger.error("Error message")', 'from __main__ import {name}; logger = {name}()'.format(name = test.__name__))
		print('Time for 1000000 calls of \t{: <25}: {}'.format(test.__name__, t))

	logwood.shutdown()
