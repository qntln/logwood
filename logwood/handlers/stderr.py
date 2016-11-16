from typing import Dict, Any

from logwood.handlers.logging import StderrHandler



class ColoredStderrHandler(StderrHandler):
	GRAY, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(30, 38)

	COLOR_SEQ = '\033[1;{color:d}m'
	RESET_SEQ = '\033[0m'

	COLORS = {
		'NOTSET': GRAY,
		'DEBUG': GRAY,
		'INFO': WHITE,
		'WARNING': YELLOW,
		'ERROR': RED,
		'CRITICAL': MAGENTA,
		'FATAL': MAGENTA,
	}

	def format_message(self, record: Dict[str, Any]) -> str:
		'''
		Add colors to stderr output.
		'''
		message = super().format_message(record)

		if record['level'] in self.COLORS:
			return self.COLOR_SEQ.format(color = self.COLORS[record['level']]) + message + self.RESET_SEQ

		return message
