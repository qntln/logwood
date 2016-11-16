import unittest.mock

import logwood
import logwood.handlers.syslog



@unittest.mock.patch('syslog.syslog')
def test_emit(syslog_mock):
	'''
	emit on libsyslog will call syslog.syslog
	'''
	logwood.basic_config(handlers = [
		logwood.handlers.syslog.SysLogLibHandler()
	])
	logger = logwood.get_logger('Test')
	logger.warning('Warning')
	logwood.shutdown()
	assert syslog_mock.called
