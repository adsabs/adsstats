import operator
import site
#from config import config

def sort_list_of_lists(L, index, rvrs=True):
    return sorted(L, key=operator.itemgetter(index), reverse=rvrs)

def chunks(l, n):
    """ Yield successive n-sized chunks from l.
        """
    for i in xrange(0, len(l), n):
        yield l[i:i+n]

def flatten(items):
    result = []
    for item in items:
        if hasattr(item, '__iter__'):
            result.extend(flatten(item))
        else:
            result.append(item)
    return result
