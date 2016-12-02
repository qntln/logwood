Logwood
=======

This is a simple, but fast logging library. We traded features for speed.

Logwood is only tested with Python 3.5. There are no plans to support older versions.

.. code-block:: python

	import logwood
	from logwood.handlers.stderr import ColoredStderrHandler

	logwood.basic_config(
		level = logwood.INFO,
		handlers = [ColoredStderrHandler()]
	)

	logger = logwood.get_logger('LoggerName')
	logger.info('Just FYI')
	logger.warning('Six times seven is {:d}.', 42)


Features
--------

While logwood is very lightweight (see the Compatibility section below) it still gives you a few nice features
out of the box:

- Chunked syslog handler. Splits long messages and writes them to syslog piece by piece. Useful e.g. to work
  around maximum UDP packet size (:code:`logwood.handlers.chunked.ChunkedSysLogHandler`).
- Alternative syslog handler that uses the `standard syslog module <https://docs.python.org/3/library/syslog.html>`_
  to emit logs to local syslog. Benchmarks show this to be faster than connecting and writing to a :code:`socket`
  directly (:code:`logwood.handlers.syslog.SysLogLibHandler`).
- Threaded handler: executes any underlying handler in a separate thread to avoid blocking the main thread
  (:code:`logwood.handlers.threaded.ThreadedHandler`).
- Colored logs on stderr (:code:`logwood.handlers.stderr.ColoredStderrHandler`).


Compatibility with :code:`logging`
----------------------------------

Logwood API is somewhat similar to the standard :code:`logging`, but we've made a few opinionated design decisions
that do not make this a drop-in replacement:

- Loggers do not form a tree hierarchy. There are no child loggers and no handler or configuration inheritance.
  We found that such features make the :code:`logging` module very slow.
- Logging config cannot be changed after loggers are created, and conversely no loggers may be created until
  logging is configured. Again, this is to make loggers as simple as possible.
- While %-style formatting is supported for historical reasons, logwood prefers the more powerful :code:`str.format`.
  It tries to guess which formatting style you're using but defaults to :code:`str.format` (curly braces).
  This feature will be removed in a future major release and only :code:`str.format` will be supported going forward.

:code:`logging` -> :code:`logwood` bridge
.........................................

Call :code:`logwood.compat.redirect_standard_logging()` to configure the standard :code:`logging` module to send
all messages to :code:`logwood` for handling. You can use this to run a :code:`logwood`-based application that
nevertheless works with any 3rd-party libraries using :code:`logging`.


py.test fixtures
----------------
For testing convenience there are two fixtures prepared: :code:`configure_and_reset_logwood` and :code:`logwood_handler_mock`.
:code:`configure_and_reset_logwood` is an autouse fixture, i.e. it is run before every test in projects that use logwood.
It calls :code:`logwood.basic_config` to set a stderr handler so you don't have to care about logwood configuration
in tests, and you can see logs when your test fails.
The :code:`logwood_handler_mock` fixture is a mock handler. This is useful for testing how your code uses logwood.
It stores all messages in a dict of lists so you can easily find your messages. To identify the level you can use
either strings (upper/lowercase) or constants from logging or logwood:

.. code-block:: python

	import logwood

	def some_func():
		logger = logwood.get_logger('test_logger')
		logger.warning('Something is wrong with id {}', 42)


	def test_logwood(logwood_handler_mock):
		some_func()
		assert 'Something is wrong with id 42' in logwood_handler_mock['WARNING']
		assert not logwood_handler_mock['error']
		assert any(m.startswith('Something') for m in logwood_handler_mock[logwood.WARNING])
