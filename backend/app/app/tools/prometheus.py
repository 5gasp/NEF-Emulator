import json 
class Prometheus :
    
    def __init__(self):
        with open('app/core/config/prometheusQueries.json') as json_file:
            data = json.load(json_file)        
            self._queries = data
            self._queryAliases = data.keys()

    def getMetrics(self): 
        return  {"metrics" : list(self._queryAliases)}
    
    def query(self, metric:str):
        if(metric.name in self._queryAliases):
            return self._queries[metric.name]
        return None

    def response(self, result, metric:str):
      
        if hasattr(self,metric) and callable(func := getattr(self, metric)):
            ret = func(result)
            return ret
        else:
            try:
                return  {"timestamp" : result['data']['result'][0]['value'][0], "value" : result['data']['result'][0]['value'][1]}
            except:
                return  None
    

    def TX_kilobits_persec_average(self, result):
        return  {"timestamp" : result['data']['result'][1]['value'][0], "value" : abs(float(result['data']['result'][1]['value'][1]))}
    
    def RX_kilobits_persec_average(self, result):
        return  {"timestamp" : result['data']['result'][0]['value'][0], "value" : result['data']['result'][0]['value'][1]}