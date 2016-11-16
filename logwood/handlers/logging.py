'''
This module contains old handlers copied from the standard logging module.
These handlers were simply refactored to work with logwood.
'''

from typing import Dict, Any
import sys
import os
import socket

from logwood.base_handler import Handler



class StreamHandler(Handler):
	"""
	A handler class which writes logging records, appropriately formatted,
	to a stream. Note that this class does not close the stream, as
	sys.stdout or sys.stderr may be used.
	"""

	terminator = '\n'

	def __init__(self, level: int = None, format: str = None, stream=None) -> None:
		"""
		Initialize the handler.

		If stream is not specified, sys.stderr is used.
		"""
		super().__init__(level, format)
		if stream is None:
			stream = sys.stderr
		self.stream = stream


	def flush(self) -> None:
		"""
		Flushes the stream.
		"""
		if self.stream and hasattr(self.stream, "flush"):
			self.stream.flush()


	def emit(self, record: Dict[str, Any]):
		"""
		Emit a record.

		If a formatter is specified, it is used to format the record.
		The record is then written to the stream with a trailing newline.  If
		exception information is present, it is formatted using
		traceback.print_exception and appended to the stream.  If the stream
		has an 'encoding' attribute, it is used to determine how to do the
		output to the stream.
		"""
		msg = self.format_message(record)
		stream = self.stream
		stream.write(msg)
		stream.write(self.terminator)
		self.flush()


class FileHandler(StreamHandler):
	"""
	A handler class which writes formatted logging records to disk files.
	"""
	def __init__(self, level: int = None, format: str = None, filename = None, mode='a', encoding=None, delay=False):
		"""
		Open the specified file and use it as the stream for logging.
		"""
		#keep the absolute path, otherwise derived classes which use this
		#may come a cropper when the current directory changes
		self.base_filename = os.path.abspath(filename)
		self.mode = mode
		self.encoding = encoding
		self.delay = delay
		if delay:
			#We don't open the stream, but we still need to call the
			#Handler constructor to set level and format
			super().__init__(level = level, format = format)
			self.stream = None
		else:
			super().__init__(level, format, self._open())


	def close(self):
		"""
		Closes the stream.
		"""
		super().close()
		if self.stream:
			self.flush()
			if hasattr(self.stream, "close"):
				self.stream.close()
			self.stream = None


	def _open(self):
		"""
		Open the current base file with the (original) mode and encoding.
		Return the resulting stream.
		"""
		return open(self.base_filename, self.mode, encoding=self.encoding)


	def emit(self, record):
		"""
		Emit a record.

		If the stream was not opened because 'delay' was specified in the
		constructor, open it before calling the superclass's emit.
		"""
		if self.stream is None:
			self.stream = self._open()
		StreamHandler.emit(self, record)


class StderrHandler(StreamHandler):
	"""
	This class is like a StreamHandler using sys.stderr, but always uses
	whatever sys.stderr is currently set to rather than the value of
	sys.stderr at handler construction time.
	"""
	def __init__(self, level: int = None, format: str = None):
		"""
		Initialize the handler.
		"""
		super().__init__(level = level, format = format, stream = sys.stderr)


class SysLogHandler(Handler):
	"""
	A handler class which sends formatted logging records to a syslog
	server. Based on Sam Rushing's syslog module:
	http://www.nightmare.com/squirl/python-ext/misc/syslog.py
	Contributed by Nicolas Untz (after which minor refactoring changes
	have been made).
	"""

	# from <linux/sys/syslog.h>:
	# ======================================================================
	# priorities/facilities are encoded into a single 32-bit quantity, where
	# the bottom 3 bits are the priority (0-7) and the top 28 bits are the
	# facility (0-big number). Both the priorities and the facilities map
	# roughly one-to-one to strings in the syslogd(8) source code.  This
	# mapping is included in this file.
	#
	# priorities (these are ordered)

	LOG_EMERG     = 0       #  system is unusable
	LOG_ALERT     = 1       #  action must be taken immediately
	LOG_CRIT      = 2       #  critical conditions
	LOG_ERR       = 3       #  error conditions
	LOG_WARNING   = 4       #  warning conditions
	LOG_NOTICE    = 5       #  normal but significant condition
	LOG_INFO      = 6       #  informational
	LOG_DEBUG     = 7       #  debug-level messages

	#  facility codes
	LOG_KERN      = 0       #  kernel messages
	LOG_USER      = 1       #  random user-level messages
	LOG_MAIL      = 2       #  mail system
	LOG_DAEMON    = 3       #  system daemons
	LOG_AUTH      = 4       #  security/authorization messages
	LOG_SYSLOG    = 5       #  messages generated internally by syslogd
	LOG_LPR       = 6       #  line printer subsystem
	LOG_NEWS      = 7       #  network news subsystem
	LOG_UUCP      = 8       #  UUCP subsystem
	LOG_CRON      = 9       #  clock daemon
	LOG_AUTHPRIV  = 10      #  security/authorization messages (private)
	LOG_FTP       = 11      #  FTP daemon

	#  other codes through 15 reserved for system use
	LOG_LOCAL0    = 16      #  reserved for local use
	LOG_LOCAL1    = 17      #  reserved for local use
	LOG_LOCAL2    = 18      #  reserved for local use
	LOG_LOCAL3    = 19      #  reserved for local use
	LOG_LOCAL4    = 20      #  reserved for local use
	LOG_LOCAL5    = 21      #  reserved for local use
	LOG_LOCAL6    = 22      #  reserved for local use
	LOG_LOCAL7    = 23      #  reserved for local use

	priority_names = {
		"alert":    LOG_ALERT,
		"crit":     LOG_CRIT,
		"critical": LOG_CRIT,
		"debug":    LOG_DEBUG,
		"emerg":    LOG_EMERG,
		"err":      LOG_ERR,
		"error":    LOG_ERR,        #  DEPRECATED
		"info":     LOG_INFO,
		"notice":   LOG_NOTICE,
		"panic":    LOG_EMERG,      #  DEPRECATED
		"warn":     LOG_WARNING,    #  DEPRECATED
		"warning":  LOG_WARNING,
		}

	facility_names = {
		"auth":     LOG_AUTH,
		"authpriv": LOG_AUTHPRIV,
		"cron":     LOG_CRON,
		"daemon":   LOG_DAEMON,
		"ftp":      LOG_FTP,
		"kern":     LOG_KERN,
		"lpr":      LOG_LPR,
		"mail":     LOG_MAIL,
		"news":     LOG_NEWS,
		"security": LOG_AUTH,       #  DEPRECATED
		"syslog":   LOG_SYSLOG,
		"user":     LOG_USER,
		"uucp":     LOG_UUCP,
		"local0":   LOG_LOCAL0,
		"local1":   LOG_LOCAL1,
		"local2":   LOG_LOCAL2,
		"local3":   LOG_LOCAL3,
		"local4":   LOG_LOCAL4,
		"local5":   LOG_LOCAL5,
		"local6":   LOG_LOCAL6,
		"local7":   LOG_LOCAL7,
		}

	#The map below appears to be trivially lowercasing the key. However,
	#there's more to it than meets the eye - in some locales, lowercasing
	#gives unexpected results. See SF #1524081: in the Turkish locale,
	#"INFO".lower() != "info"
	priority_map = {
		"DEBUG" : "debug",
		"INFO" : "info",
		"WARNING" : "warning",
		"ERROR" : "error",
		"CRITICAL" : "critical"
	}

	def __init__(self, address=('localhost', 514),
				 facility=LOG_USER, socktype=None, level: int = None, format: str = None):
		"""
		Initialize a handler.

		If address is specified as a string, a UNIX socket is used. To log to a
		local syslogd, "SysLogHandler(address="/dev/log")" can be used.
		If facility is not specified, LOG_USER is used. If socktype is
		specified as socket.SOCK_DGRAM or socket.SOCK_STREAM, that specific
		socket type will be used. For Unix sockets, you can also specify a
		socktype of None, in which case socket.SOCK_DGRAM will be used, falling
		back to socket.SOCK_STREAM.
		"""
		super().__init__(level, format)

		self.address = address
		self.facility = facility
		self.socktype = socktype

		if isinstance(address, str):
			self.unixsocket = True
			self._connect_unixsocket(address)
		else:
			self.unixsocket = False
			if socktype is None:
				socktype = socket.SOCK_DGRAM
			self.socket = socket.socket(socket.AF_INET, socktype)
			if socktype == socket.SOCK_STREAM:
				self.socket.connect(address)
			self.socktype = socktype
		self.formatter = None

	def _connect_unixsocket(self, address):
		use_socktype = self.socktype
		if use_socktype is None:
			use_socktype = socket.SOCK_DGRAM
		self.socket = socket.socket(socket.AF_UNIX, use_socktype)
		try:
			self.socket.connect(address)
			# it worked, so set self.socktype to the used type
			self.socktype = use_socktype
		except OSError:
			self.socket.close()
			if self.socktype is not None:
				# user didn't specify falling back, so fail
				raise
			use_socktype = socket.SOCK_STREAM
			self.socket = socket.socket(socket.AF_UNIX, use_socktype)
			try:
				self.socket.connect(address)
				# it worked, so set self.socktype to the used type
				self.socktype = use_socktype
			except OSError:
				self.socket.close()
				raise

	def encode_priority(self, facility, priority):
		"""
		Encode the facility and priority. You can pass in strings or
		integers - if strings are passed, the facility_names and
		priority_names mapping dictionaries are used to convert them to
		integers.
		"""
		if isinstance(facility, str):
			facility = self.facility_names[facility]
		if isinstance(priority, str):
			priority = self.priority_names[priority]
		return (facility << 3) | priority

	def close(self):
		"""
		Closes the socket.
		"""
		super().close()
		self.socket.close()

	def map_priority(self, level_name):
		"""
		Map a logging level name to a key in the priority_names map.
		This is useful in two scenarios: when custom levels are being
		used, and in the case where you can't do a straightforward
		mapping by lowercasing the logging level name because of locale-
		specific issues (see SF #1524081).
		"""
		return self.priority_map.get(level_name, "warning")

	ident = ''          # prepended to all messages
	append_nul = True   # some old syslog daemons expect a NUL terminator

	def emit(self, record: Dict[str, Any]):
		"""
		Emit a record.

		The record is formatted, and then sent to the syslog server. If
		exception information is present, it is NOT sent to the server.
		"""
		msg = self.format_message(record)
		if self.ident:
			msg = self.ident + msg
		if self.append_nul:
			msg += '\000'

		# We need to convert record level to lowercase, maybe this will
		# change in the future.
		prio = '<%d>' % self.encode_priority(self.facility,
											self.map_priority(record['level']))
		prio = prio.encode('utf-8')
		# Message is a string. Convert to bytes as required by RFC 5424
		msg = msg.encode('utf-8')
		msg = prio + msg
		if self.unixsocket:
			try:
				self.socket.send(msg)
			except OSError:
				self.socket.close()
				self._connect_unixsocket(self.address)
				self.socket.send(msg)
		elif self.socktype == socket.SOCK_DGRAM:
			self.socket.sendto(msg, self.address)
		else:
			self.socket.sendall(msg)
