from models import *

import sys
import inspect

#model_map = {'metrics':Metrics,
#             'statistics':Statistics,
#             'histograms':Histogram,
#             'series':TimeSeries,
#            }
model_map = {'statistics':Statistics}

def data_models(models = []):
    models = filter(lambda a: a in model_map.keys(), models)
    dc = []
    for name, obj in inspect.getmembers(sys.modules[__name__]):
        for model_type in models:
         if inspect.isclass(obj) and model_map[model_type] in obj.__bases__:
            dc.append(obj)
    return dc
