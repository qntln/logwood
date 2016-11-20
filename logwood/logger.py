from typing import List, Optional
import logging
import time
import sys

import logwood.state
import logwood.base_handler
from logwood import global_config
from logwood import constants
from logwood.base_handler import Handler



_logging_formatter = logging.Formatter()



class Logger:
	'''
	Base logger class.
	Logger sends log records to all its handlers, but also to all default handlers defined with :func:`logwood.basic_config`.

	This behavior is unchangeable, so even a logger with no handlers set will still log to all default handlers.

	This class must not be instantiated directly. Use `logwood.get_logger` instead.
	'''

	def __init__(self, name: str, handlers: Optional[List[Handler]] = None) -> None:
		assert logwood.state.config_called, 'logwood.basic_config() was not called. Call basic_config first before getting Logger instances.'
		self.name = name
		self.handlers = handlers or []


	def add_handler(self, handler: Handler) -> None:
		'''
		Add handler to list of extra handlers where log records are sent.
		'''
		self.handlers.append(handler)


	def debug(self, message: str, *args) -> None:
		'''
		Log message with DEBUG level
		'''
		self.log(constants.DEBUG, message, *args)


	def info(self, message: str, *args) -> None:
		'''
		Log message with INFO level
		'''
		self.log(constants.INFO, message, *args)


	def warning(self, message: str, *args) -> None:
		'''
		Log message with WARNING level
		'''
		self.log(constants.WARNING, message, *args)


	def error(self, message: str, *args) -> None:
		'''
		Log message with ERROR level
		'''
		self.log(constants.ERROR, message, *args)


	def fatal(self, message: str, *args) -> None:
		'''
		Log message with FATAL level
		'''
		self.log(constants.FATAL, message, *args)


	def critical(self, message: str, *args) -> None:
		'''
		Log message with CRITICAL level
		'''
		self.log(constants.CRITICAL, message, *args)


	def exception(self, message: str, *args) -> None:
		'''
		Log message with ERROR level and add traceback to message
		'''
		# We have to add traceback as argument because it can contain some % characters
		traceback = _logging_formatter.formatException(sys.exc_info())
		if '{' in message and '}' in message:
			placeholder = '{}'
		else:
			placeholder = '%s'
		self.error((message + '\n' + placeholder).strip(), *(args + (traceback,)))


	def log(self, level: int, message: str, *args) -> None:
		'''
		Log message with level and send to all handlers
		'''
		# Beware this is a shallow copy. But from now onwards the record should not be updated.
		# The only place where it changes is Handler.format_message, but that function expects the changes.
		record = global_config.default_record_variables.copy()
		record.update({
			'timestamp': time.time(),
			'name': self.name,
			'level_number': level,
			'level': constants.LOG_LEVEL_NAMES[level],
			'message': message,
			'args': args
		})
		for handler in global_config.default_handlers + self.handlers:
			try:
				handler.handle(record)
			except:
				global_config.last_resort_handler(record)
