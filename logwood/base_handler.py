from typing import Dict, Any

import abc
import logwood.state
from logwood import global_config



class Handler(abc.ABC):
	'''
	Base handler which only implements filtering records by log level and formats messages.
	'''

	def __init__(self, level: int = None, format: str = None) -> None:
		self.level = level
		self.format = format
		self.is_shutdown = False
		logwood.state.defined_handlers.append(self)


	def format_message(self, record: Dict[str, Any]) -> str:
		'''
		We format our message if args are present and contain data.
		NOTE that if multiple handlers handle this record, only the first one performs this block.
		All subsequent handlers share the already-formatted record dict.
		'''
		if 'args' in record and record['args']:
			# Apply message arguments
			if '{' in record['message'] and '}' in record['message']:
				# assume that string can be formatted by ``str.format()``
				record['message'] = record['message'].format(*record['args'])
			else:
				# fall back solution, format by %-formatting
				record['message'] %= record['args']
			# Remove already used args
			del record['args']

		# Use default format if format is not set
		format = global_config.default_format if self.format is None else self.format
		# Return formatted message
		if '{' in format and '}' in format:
			return format.format(**record)
		else:
			return format % record


	def handle(self, record: Dict[str, Any]) -> None:
		'''
		This is the handler's standard entrypoint. This method filters records by handler's log level.
		'''
		level = global_config.default_log_level if self.level is None else self.level
		if record['level_number'] >= level:
			self.emit(record)


	def close(self) -> None:
		'''
		The handler can clean up its resources here.
		This method removes the handler from logwood's internal list of handlers.
		Subclasses overriding this method must ensure that this gets called.
		'''
		logwood.state.defined_handlers.remove(self)


	@abc.abstractmethod
	def emit(self, record: Dict[str, Any]) -> None: # pragma: no cover
		'''
		Emit message, implemented in subclasses.
		'''
