from typing import Iterator, Dict, Any
import math

import logwood.handlers.logging



class ChunkedSysLogHandler(logwood.handlers.logging.SysLogHandler):
	'''
	Syslog handler derived from Python's logging syslog handler.
	This handler chunks messages by X characters (defaults to 4,000) and sends those chunks to syslog as separate messages.
	'''

	def __init__(self, level: int = None, format: str = None, address = ('localhost', 514),
	facility = logwood.handlers.logging.SysLogHandler.LOG_USER, socktype = None, *, chunk_size = 4000):
		super().__init__(level = level, format = format, address = address, facility = facility, socktype = socktype)
		self.chunk_size = chunk_size


	def emit(self, record: Dict[str, Any]) -> None:
		'''
		Emit a record via parent implementation. Long records are chunked and each chunk is emitted separately.
		'''
		# Let formatter format message in record
		self.format_message(record)
		# Extract this message from record
		message = record['message']
		for chunk in self._chunk_records(message, record):
			super().emit(chunk)


	def _chunk_records(self, message: str, record: Dict[str, Any]) -> Iterator[Dict[str, Any]]:
		'''
		Create message chunks from the given record, preserving other record attributes in each chunk.
		'''
		msg_len = len(message)
		number_of_chunks = math.ceil(msg_len / self.chunk_size)

		for chunk in range(number_of_chunks):
			msg = message[(chunk * self.chunk_size):((chunk + 1) * self.chunk_size)]
			if number_of_chunks > 1:
				msg = '({}/{}) '.format(chunk + 1, number_of_chunks) + msg
			record_chunk = record.copy()
			record_chunk['message'] = msg
			yield record_chunk
