#!/usr/bin/env python3
from gi.repository import GObject


def registerType(cls):
	GObject.type_register(cls)
	return cls


def registerSignals(cls):
	GObject.type_register(cls)
	for name, args in cls.signals:
		try:
			GObject.signal_new(
				name,
				cls,
				GObject.SignalFlags.RUN_LAST,
				None,
				args,
			)
		except RuntimeError as e:
			raise RuntimeError(
				f"Failed to create signal {name} " +
				f"for class {cls.__name__} in {cls.__module__}",
			)
	return cls
