from typing import Dict, Any
import syslog

from logwood.base_handler import Handler



class SysLogLibHandler(Handler):
	'''
	A logging handler that emits messages to syslog.syslog.
	'''

	priority_map = {
		10: syslog.LOG_NOTICE,
		20: syslog.LOG_NOTICE,
		30: syslog.LOG_WARNING,
		40: syslog.LOG_ERR,
		50: syslog.LOG_CRIT,
		0: syslog.LOG_NOTICE,
	}


	def __init__(self, level: int = None, format: str = None, facility = syslog.LOG_LOCAL0):
		super().__init__(level, format)
		self.facility = facility


	def emit(self, record: Dict[str, Any]) -> None:
		syslog.syslog(self.facility | self.priority_map[record['level_number']], self.format_message(record))
