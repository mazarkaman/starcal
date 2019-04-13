
log = None

def init():
	global log
	import os
	import warnings
	from io import StringIO
	from os.path import join, isdir
	from scal3.path import confDir, rootDir, APP_NAME
	from scal3.os_utils import makeDir

	if os.path.exists(confDir):
		if not isdir(confDir):
			os.rename(confDir, confDir + "-old")
			os.mkdir(confDir)
	else:
		os.mkdir(confDir)

	makeDir(join(confDir, "log"))

	try:
		import logging
		import logging.config

		with open(join(rootDir, "conf", "logging-user.conf")) as fp:
			logConfText = fp.read()
		for varName in ("confDir", "APP_NAME"):
			logConfText = logConfText.replace(varName, eval(varName))

		logging.config.fileConfig(StringIO(logConfText))
		log = logging.getLogger(APP_NAME)
	except Exception as e:
		print("failed to setup logger:", e)
		from scal3.utils import FallbackLogger
		log = FallbackLogger()

	# can set env var WARNINGS to: "error", "ignore", "always", "default", "module", "once"
	if os.getenv("WARNINGS"):
		warnings.filterwarnings(os.getenv("WARNINGS"))

def get():
	if log is None:
		init()
	return log
