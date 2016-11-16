# This module is used for keeping runtime state.

# This flag indicates if basic_config has already been called.
config_called = False

# This is a dict of weakrefs to all loggers, keyed by name. The loggers might not exist already but still be counted in here.
# We use weakrefs instead of simple counts so we can see which loggers were created and also use it as a cache.
defined_loggers = {} # type: Dict[str, weakref]

# Keep references to created handlers, so they can be properly closed later.
defined_handlers = [] # type: List[logwood.base_handler.Handler]
