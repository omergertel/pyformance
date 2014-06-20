__import__('pkg_resources').declare_namespace(__name__)

def HostedGraphiteReporter(*args, **kwargs):
	# lazy import because HostedGraphiteReporter requires twisted
	from .hosted_graphite_reporter import HostedGraphiteReporter as cls
	return cls(*args, **kwargs)
