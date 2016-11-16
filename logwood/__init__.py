from typing import List, Dict, Any
import socket, sys
import weakref

import logwood.state
from logwood import global_config
from logwood.base_handler import Handler
from logwood.logger import Logger

from logwood.constants import CRITICAL, FATAL, ERROR, WARNING, WARN, INFO, DEBUG, NOTSET # noqa



def basic_config(format: str = global_config.default_format, level: int = global_config.default_log_level,
handlers: List[Handler] = None, record_variables: Dict[str, Any] = None) -> None:
	'''
	Setup default values for handlers
	'''
	assert not logwood.state.defined_loggers, 'Some Logger instance was already created. Cannot call basic_config.'

	logwood.state.config_called = True

	# Setup default value types
	handlers = handlers or []
	record_variables = record_variables or {}

	# Set default record_variables and update with given record_variables
	default_record_variables = {
		'hostname': socket.gethostname(),
		'system_identifier': sys.argv[0]
	}
	default_record_variables.update(record_variables)

	global_config.default_format = format
	global_config.default_log_level = level
	global_config.default_record_variables.update(default_record_variables)

	global_config.default_handlers.clear()
	global_config.default_handlers.extend(handlers)


def get_logger(name: str) -> Logger:
	'''
	Get new logger instance configured from global configuration
	'''
	try:
		logger_weak_ref = logwood.state.defined_loggers[name]
	except KeyError:
		return _create_logger_instance(name)
	else:
		# This check is thread safe, so no locking is required here
		logger_instance = logger_weak_ref()
		if logger_instance is None:
			# Logger instance in cache is already dead so we have to create a new one
			return _create_logger_instance(name)

		return logger_instance


def _create_logger_instance(name: str) -> Logger:
	'''
	Creates new logger instance and register it to the cache under `name`
	Do not call this method directly - it won't try to check if logger with given name already exists
	'''
	logger_instance = Logger(name)
	# Register instance in state as weakref so it can be GC when needed.
	logwood.state.defined_loggers[name] = weakref.ref(logger_instance)
	return logger_instance


def shutdown() -> None:
	'''
	Shutdown logging, this will shut down all defined handlers
	'''
	for handler in logwood.state.defined_handlers:
		handler.close()
