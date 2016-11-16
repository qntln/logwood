from logwood import constants



default_log_level = constants.INFO

default_handlers = [] # type: List[logwood.base_handler.Handler]

default_format = "[%(timestamp)s][%(hostname)s][%(system_identifier)s][%(name)s][%(level)s] %(message)s"

default_record_variables = {
	'hostname': '-',
	'system_identifier': '-'
}
