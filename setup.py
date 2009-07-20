from distutils.core import setup
import py2exe, sys, os

if 'py2exe' in sys.argv:
	setup(
		options = {'py2exe': {'bundle_files': 1}},
		console = [{'script': 'reckoning.py'}],
		zipfile = None,
		data_files = [('.', 'config.py')],
		)
