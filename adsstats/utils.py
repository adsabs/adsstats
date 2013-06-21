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

def get_timespan(biblist):
    """
    Returns the time span (years) for a list of bibcodes
    """
    years = map(lambda a: int(a[:4]), biblist)
    minYr = min(years)
    maxYr = max(years)
    span  = maxYr - minYr + 1
    return max(span,1)
