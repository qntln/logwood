import logging
import logwood



def redirect_standard_logging():
	'''
	Configure original logging module to send all messages to BridgeHandler.
	This function does not reset logging module if it was already configured.
	'''
	logging.basicConfig(
		level = logging.DEBUG,
		format = '%(message)s',
		handlers = [
			BridgeHandler()
		]
	)



class BridgeHandler(logging.Handler):
	'''
	Bridge between original logging module and logwood.
	'''

	def __init__(self, level = logging.NOTSET):
		super().__init__(level)
		self._loggers = {}
		self._base_formatter = logging.Formatter()


	def emit(self, record):
		''' Pass logs to logwood with logger name equal to original logger name. '''
		name = record.name
		level = record.levelno
		# Format message using the original logging formatter so we keep the stack trace.
		message = self._base_formatter.format(record)
		try:
			# Cache logger reference so we do not call get_logger for every message.
			logger = self._loggers[name]
		except KeyError:
			self._loggers[name] = logger = logwood.get_logger(name)

		logger.log(level, message)
