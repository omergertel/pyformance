# -*- coding: utf-8 -*-

def HostedGraphiteReporter(*args, **kwargs):
	# lazy import because HostedGraphiteReporter
	from .hosted_graphite_reporter import HostedGraphiteReporter as cls
	return cls(*args, **kwargs)
