import urllib2, base64
import time
from pyformance.meters import Counter, Histogram, Meter, Timer
from twisted.internet import reactor
from twisted.internet import task
from pyformance.registry import MetricsRegistry

class HostedGraphiteReporter:

    def __init__(self, registry, reportingInterval, hostedGraphiteApiKey, url="https://hostedgraphite.com/api/v1/sink" ):
		self.url = url
		self.api_key = hostedGraphiteApiKey
		l = task.LoopingCall(self.sendMetricsNow, registry)
		l.start(reportingInterval)
		return
  
    def sendMetricsNow(self, registry):
		metrics  = self.getMetrics(registry)
		if metrics:
			try:
				request = urllib2.Request(self.url, metrics)
				request.add_header("Authorization", "Basic %s" % base64.encodestring(self.api_key).strip())
				result = urllib2.urlopen(request)
			except Exception as e:
				print(e)

    
    def getMetrics(self, registry, timestamp=`int(round(time.time()))`):
        metrics = registry.dump_metrics()
        metricsData = []
        for key in metrics.keys(): 
            for valueKey in  metrics[key].keys():
            	metricLine = []
            	metricLine.append(key)
            	metricLine.append('.')
            	metricLine.append(valueKey)
            	metricLine.append(' ')
            	metricLine.append(`metrics[key][valueKey]`)
            	metricLine.append(' ')
            	metricLine.append(timestamp)
            	metricLine.append('\n')
            	metricsData.append(''.join(metricLine))
        return ''.join(metricsData)
