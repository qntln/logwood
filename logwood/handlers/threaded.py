from typing import Dict, Any
import concurrent.futures

from logwood.base_handler import Handler



class ThreadedHandler(Handler):
	'''
	This handler calls an underlying handler in a different thread to avoid blocking the logging thread.
	'''

	def __init__(self, level: int = None, format: str = None, underlying_handler: Handler = None) -> None:
		super().__init__(level, format)
		self.underlying_handler = underlying_handler
		# We do not need more then one worker to emit messages
		self.executor = concurrent.futures.ThreadPoolExecutor(max_workers = 1)


	def emit(self, record: Dict[str, Any]) -> None:
		''' Call underlying handler in a worker thread. '''
		self.executor.submit(self.underlying_handler.emit, record)


	def close(self) -> None:
		''' End thread pool executor and wait for it to finish. '''
		super().close()
		# Stop thread executor and wait until it completes
		self.executor.shutdown(wait = True)
		# cleanup underlying handler too
		self.underlying_handler.close()
