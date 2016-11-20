from typing import List, Dict, Any

import socket
import sys
import weakref

from logwood import global_config, state
from logwood.base_handler import Handler
from logwood.logger import Logger

from logwood.constants import CRITICAL, FATAL, ERROR, WARNING, WARN, INFO, DEBUG, NOTSET # noqa



def basic_config(handlers: List[Handler], format: str = global_config.default_format,
level: int = global_config.default_log_level, record_variables: Dict[str, Any] = None) -> None:
	'''
	:param record_variables: Additional variables that will be baked into each logged message.
	'''
	assert not state.defined_loggers, 'A Logger instance has already been created. Cannot call basic_config.'

	state.config_called = True
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
	Get a configured instance of :class:`Logger`. Instances are cached by name.
	'''
	try:
		logger_weak_ref = state.defined_loggers[name]
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
	''' Create a new logger instance and cache it. Do not call this method directly. '''
	logger_instance = Logger(name)
	# Register instance in state as weakref so it can be GC when needed.
	state.defined_loggers[name] = weakref.ref(logger_instance)
	return logger_instance


def shutdown() -> None:
	'''
	Shut down all defined logwood handlers and give them a chance to clean up their resources.
	'''
	for handler in state.defined_handlers:
		handler.close()
