import os
from distutils.core import setup



def read(relpath: str) -> str:
	with open(os.path.join(os.path.dirname(__file__), relpath)) as f:
		return f.read()


setup(
	name = 'logwood',
	version = read('version.txt').strip(),
	description = 'Simple, but fast logging library for Python 3.5+',
	long_description = read('README.rst'),
	author = 'Quantlane',
	author_email = 'code@quantlane.com',
	url = 'https://github.com/qntln/logwood',
	license = 'Apache 2.0',
	packages = [
		'logwood',
		'logwood.handlers',
	],
	classifiers = [
		'Development Status :: 4 - Beta',
		'License :: OSI Approved :: Apache Software License',
		'Natural Language :: English',
		'Programming Language :: Python :: 3 :: Only',
		'Programming Language :: Python :: 3.5',
	]
)
