from typing import Any, Dict

import logging
import sys



def print_to_stderr(record: Dict[str, Any]) -> None:
	traceback = logging.Formatter().formatException(sys.exc_info())
	print('LOGWOOD ERROR - cannot log record {!r}\n{:s}'.format(record, traceback), file = sys.stderr)
