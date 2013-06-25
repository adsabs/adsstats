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
    """flatten(sequence) -> list

    Returns a single, flat list which contains all elements retrieved
    from the sequence and all recursively contained sub-sequences
    (iterables).

    Examples:
    >>> [1, 2, [3,4], (5,6)]
    [1, 2, [3, 4], (5, 6)]
    >>> flatten([[[1,2,3], (42,None)], [4,5], [6], 7, MyVector(8, 9, 10)])
    [1, 2, 3, 42, None, 4, 5, 6, 7, 8, 9, 10]"""

    result = []
    for item in items:
        if hasattr(item, '__iter__'):
            result.extend(flatten(item))
        else:
            result.append(item)
    return result

def get_timespan(biblist):
    """
    Returns the time span (years) for a list of bibcodes
    """
    years = map(lambda a: int(a[:4]), biblist)
    minYr = min(years)
    maxYr = max(years)
    span  = maxYr - minYr + 1
    return max(span,1)

def get_subset(mlist,year):
    newlist = []
    for entry in mlist:
        if int(entry[0][:4]) > int(year):
            continue
        newvec = entry[:9]
        citations = entry[-1]
        citations = filter(lambda a: int(a[:4]) <= int(year), citations)
#        ref_citations = filter(lambda a: is_refereed(a), citations)
        newvec.append(citations)
        newvec[2]  = len(citations)
#        newvec[3]  = len(ref_citations)
        newlist.append(newvec)
    return newlist