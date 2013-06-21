import os
from datetime import datetime
import site
site.addsitedir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# get modules for math operations
from numpy import mean
from numpy import median
from numpy import vdot as vector_product
from numpy import sqrt
from numpy import histogram
import math
# get access to local helper functions
from adsstats import utils
from config import config
# JSON functionality
import simplejson as json

#### Abstract data models:
#
class Statistics():
    """
    Statistics class calculates statistics for a list of numbers and 
    associated weights.
    Input data consists of Python list: 
        L = [..., (number, weight), ...], 
    so that the frequency for item k is L[k][0], and the weight for 
    item k is l[k][1]  (k=0,...,N).
    Provides results in form of JSON structure
    """
    @classmethod
    def generate_data(cls):
        """
        get statistics for a list of values and associated weights:
            mean, median, normalized values
        """
        cls.pre_process()
        #
        values = map(lambda a: a[0], cls.data)
        weights= map(lambda a: a[1], cls.data)
        refereed_values = map(lambda a: a[0], cls.refereed_data)
        refereed_weights= map(lambda a: a[1], cls.refereed_data)
        # get number of entries
        cls.number_of_entries = len(values)
        # get number of refereed entries
        cls.number_of_refereed_entries = len(refereed_values)
        # get normalized value
        cls.normalized_value = vector_product(values,weights)
        # get refereed normalized value
        cls.refereed_normalized_value = vector_product(refereed_values,refereed_weights)
        # get mean value of values
        cls.mean_value = mean(values)
        # get mean value of refereed values
        cls.refereed_mean_value = mean(refereed_values)
        # get median value of values
        cls.median_value = median(values)
        # get median value of refereed values
        cls.refereed_median_value = median(refereed_values)
        # get total of values
        cls.total_value = sum(values)
        # get total of refereed values
        cls.refereed_total_value = sum(refereed_values)
        # record results
        cls.post_process()

    @classmethod
    def pre_process(cls, *args, **kwargs):
        """
        this method gets called immediately before the data load.
        subclasses should override
        """
        pass
    @classmethod
    def post_process(cls, *args, **kwargs):
        """
        this method gets called immediately following the data load.
        subclasses should override
        """
        pass

# Metrics class

# to calculate tori:
#    tori_list = [item for sublist in cit_dict.values() for item in sublist]
#    print sum(map(lambda c: 1.0/float(c), map(lambda b: max(b[1],config.MIN_BIBLIO_LENGTH)*b[2],filter(lambda a: len(a) > 0, tori_list))))

class Metrics():

    @classmethod
    def generate_data(cls):
        cls.pre_process()
        # array with citations, descending order
        citations = cls.citations
        citations.sort()
        citations.reverse()
        # first calclate the Hirsch and g indices
        rank = 1
        N = 0
        h = 0
        for cite in citations:
            N += cite
            r2 = rank*rank
            if r2 <= N:
                g = rank
            h += min(1, cite/rank)
            rank += 1
        # the e-index
        try:
            e = sqrt(sum(citations[:h]) - h*h)
        except:
            e = 'NA'
        # get the Tori index
        if cls.refereed:
            tori_list = [item for sublist in cls.refereed_citation_dictionary.values() for item in sublist]
        else:
            tori_list = [item for sublist in cls.citation_dictionary.values() for item in sublist]
        tori = sum(map(lambda c: 1.0/float(c), 
                   map(lambda b: max(b[1],config.MIN_BIBLIO_LENGTH)*b[2],
                   filter(lambda a: len(a) > 0, tori_list))))
        try:
            riq = int(1000.0*sqrt(float(tori))/float(cls.time_span))
        except:
            riq = "NA"
        cls.h_index = h
        cls.g_index = g
        cls.m_index = float(h)/float(cls.time_span)
        cls.i10_index = len(filter(lambda a: a >= 10, citations))
        cls.e_index = e
        cls.tori = tori
        cls.riq  = riq

        cls.post_process()

    @classmethod
    def pre_process(cls, *args, **kwargs):
        """
        this method gets called immediately before the data load.
        subclasses should override
        """
        pass
    @classmethod
    def post_process(cls, *args, **kwargs):
        """
        this method gets called immediately following the data load.
        subclasses should override
        """
        pass

# Histogram class
class Histogram():

    @classmethod
    def generate_data(cls):
        """
        Get histogram for a list of values and associated weights
        The weights are used for a normalized histogram
        """
        cls.results = {}
        cls.pre_process()
        today = datetime.today()
        skip = None
        values = map(lambda a: a[0], cls.data)
        if len(values) == 0:
            skip = True
        weights= map(lambda a: a[1], cls.data)
        if cls.config_data_name == 'reads_histogram':
            bins = range(1996, today.year+2)
        else:
            try:
                bins = range(min(values),max(values)+2)
            except:
                skip = True
        if not skip:
            refereed_values = map(lambda a: a[0], cls.refereed_data)
            refereed_weights= map(lambda a: a[1], cls.refereed_data)
            # get the regular histogram
            cls.value_histogram = histogram(values,bins=bins)
            cls.refereed_value_histogram = histogram(refereed_values,bins=bins)
            # get the normalized histogram
            cls.normalized_value_histogram = histogram(values,bins=bins,weights=weights)
            cls.refereed_normalized_value_histogram = histogram(refereed_values,bins=bins,weights=refereed_weights)
        else:
            cls.value_histogram = False
            cls.results[today.year] = "0:0:0:0"
        cls.post_process()

    @classmethod
    def pre_process(cls, *args, **kwargs):
        """
        this method gets called immediately before the data load.
        subclasses should override
        """
        pass
    @classmethod
    def post_process(cls, *args, **kwargs):
        """
        this method gets called immediately following the data load.
        subclasses should override
        """
        pass

#### Classes specific to bibliographic data:
#
class PublicationStatistics(Statistics):
    config_data_name = 'publications'

    @classmethod
    def pre_process(cls):
        data = []
        refereed_data = []
        for vector in cls.attributes:
            weight = 1.0/float(vector[4])
            data.append((1,weight))
            if vector[1]:
                refereed_data.append((1,weight))
        cls.data = data
        cls.refereed_data = refereed_data

    @classmethod
    def post_process(cls):
        cls.results = {}
        cls.results['type'] = cls.config_data_name
        cls.results['Number of papers (Total)'] = cls.number_of_entries
        cls.results['Normalized paper count (Total)'] = cls.normalized_value
        cls.results['Number of papers (Refereed)'] = cls.number_of_refereed_entries
        cls.results['Normalized paper count (Refereed)'] = cls.refereed_normalized_value

class ReadsStatistics(Statistics):
    config_data_name = 'reads'

    @classmethod
    def pre_process(cls):
        data = []
        refereed_data = []
        for vector in cls.attributes:
            weight = 1.0/float(vector[4])
            Nreads = vector[5]
            data.append((Nreads,weight))
            if vector[1]:
                refereed_data.append((Nreads,weight))
        cls.data = data
        cls.refereed_data = refereed_data

    @classmethod
    def post_process(cls):
        cls.results = {}
        cls.results['type'] = cls.config_data_name
        cls.results['Total reads (Total)'] = cls.total_value
        cls.results['Average reads (Total)'] = cls.mean_value
        cls.results['Median reads (Total)'] = cls.median_value
        cls.results['Total reads (Refereed)'] = cls.refereed_total_value
        cls.results['Average reads (Refereed)'] = cls.refereed_mean_value
        cls.results['Median reads (Refereed)'] = cls.refereed_median_value

class DownloadsStatistics(Statistics):
    config_data_name = 'downloads'

    @classmethod
    def pre_process(cls):
        data = []
        refereed_data = []
        for vector in cls.attributes:
            bbc = vector[0]
            weight = 1.0/float(vector[4])
            Nreads = vector[6]
            data.append((Nreads,weight))
            if vector[1]:
                refereed_data.append((Nreads,weight))
        cls.data = data
        cls.refereed_data = refereed_data

    @classmethod
    def post_process(cls):
        cls.results = {}
        cls.results['type'] = cls.config_data_name
        cls.results['Total downloads (Total)'] = cls.total_value
        cls.results['Average downloads (Total)'] = cls.mean_value
        cls.results['Median downloads (Total)'] = cls.median_value
        cls.results['Total downloads (Refereed)'] = cls.refereed_total_value
        cls.results['Average downloads (Refereed)'] = cls.refereed_mean_value
        cls.results['Median downloads (Refereed)'] = cls.refereed_median_value

class TotalCitationStatistics(Statistics):
    config_data_name = 'citations'

    @classmethod
    def pre_process(cls):
        data = []
        refereed_data = []
        citing_papers = []
        citing_papers_refereed = []
        for vector in cls.attributes:
            weight = 1.0/float(vector[4])
            Ncites = vector[2]
            data.append((Ncites,weight))
            if vector[1]:
                refereed_data.append((Ncites,weight))
        cls.data = data
        cls.refereed_data = refereed_data

    @classmethod
    def post_process(cls):
        cls.results = {}
        cls.results['type'] = cls.config_data_name
        cls.results['Number of citing papers (Total)'] = cls.num_citing
        cls.results['Total citations (Total)'] = cls.total_value
        cls.results['Average citations (Total)'] = cls.mean_value
        cls.results['Median citations (Total)'] = cls.median_value
        cls.results['Number of citing papers (Refereed)'] = cls.num_citing_ref
        cls.results['Total citations (Refereed)'] = cls.refereed_total_value
        cls.results['Average citations (Refereed)'] = cls.refereed_mean_value
        cls.results['Median citations (Refereed)'] = cls.refereed_median_value

class RefereedCitationStatistics(Statistics):
    config_data_name = 'refereed_citations'

    @classmethod
    def pre_process(cls):
        data = []
        refereed_data = []
        for vector in cls.attributes:
            weight = 1.0/float(vector[4])
            Ncites = vector[3]
            data.append((Ncites,weight))
            if vector[1]:
                refereed_data.append((Ncites,weight))
        cls.data = data
        cls.refereed_data = refereed_data

    @classmethod
    def post_process(cls):
        cls.results = {}
        cls.results['type'] = cls.config_data_name
        cls.results['Refereed citations (Total)'] = cls.total_value
        cls.results['Average refereed citations (Total)'] = cls.mean_value
        cls.results['Median refereed citations (Total)'] = cls.median_value
        cls.results['Normalized refereed citations (Total)'] = cls.normalized_value
        cls.results['Refereed citations (Refereed)'] = cls.refereed_total_value
        cls.results['Average refereed citations (Refereed)'] = cls.refereed_mean_value
        cls.results['Median refereed citations (Refereed)'] = cls.refereed_median_value
        cls.results['Normalized refereed citations (Refereed)'] = cls.refereed_normalized_value

class TotalMetrics(Metrics):
    config_data_name = 'metrics'

    @classmethod
    def pre_process(cls):
        biblist = map(lambda a: a[0], cls.attributes)
        cls.time_span = utils.get_timespan(biblist)
        cls.refereed = 0
        cls.citations = map(lambda a: a[2], cls.attributes)

    @classmethod
    def post_process(cls):
        cls.results = {}
        cls.results['type'] = cls.config_data_name
        cls.results['h-index (Total)'] = cls.h_index
        cls.results['g-index (Total)'] = cls.g_index
        cls.results['m-index (Total)'] = cls.m_index
        cls.results['i10-index (Total)'] = cls.i10_index
        cls.results['e_index (Total)'] = cls.e_index
        cls.results['tori index (Total)'] = cls.tori
        cls.results['riq index (Total)'] = cls.riq

class RefereedMetrics(Metrics):
    config_data_name = 'refereed_metrics'

    @classmethod
    def pre_process(cls):
        data = []
        cits = []
        biblist = map(lambda a: a[0], cls.attributes)
        cls.time_span = utils.get_timespan(biblist)
        cls.refereed = 1
        cls.citations = map(lambda b: b[2],
                           filter(lambda a: a[1] == 1, cls.attributes))

    @classmethod
    def post_process(cls):
        cls.results = {}
        cls.results['type'] = cls.config_data_name
        cls.results['h-index (Refereed)'] = cls.h_index
        cls.results['g-index (Refereed)'] = cls.g_index
        cls.results['m-index (Refereed)'] = cls.m_index
        cls.results['i10-index (Refereed)'] = cls.i10_index
        cls.results['e_index (Refereed)'] = cls.e_index
        cls.results['tori index (Refereed)'] = cls.tori
        cls.results['riq index (Refereed)'] = cls.riq

class PublicationHistogram(Histogram):
    config_data_name = 'publication_histogram'

    @classmethod
    def pre_process(cls):
        data = []
        refereed_data = []
        for vector in cls.attributes:
            year = int(vector[0][:4])
            weight = 1.0/float(vector[4])
            if vector[1]:
                refereed_data.append((year,weight))
            data.append((year,weight))
        cls.data = data
        cls.refereed_data = refereed_data

    @classmethod
    def post_process(cls):
        cls.results['type'] = cls.config_data_name
        if cls.value_histogram:
            Nentries = len(cls.value_histogram[0])
            for i in range(Nentries):
                year = cls.value_histogram[1][i]
                res = "%s:%s:%s:%s" % (cls.value_histogram[0][i],cls.refereed_value_histogram[0][i],cls.normalized_value_histogram[0][i],cls.refereed_normalized_value_histogram[0][i])
                cls.results[str(year)] = res

class ReadsHistogram(Histogram):
    config_data_name = 'reads_histogram'

    @classmethod
    def pre_process(cls):
        data = []
        refereed_data = []
        print "preparing reads histogram data...."
        for vec in cls.attributes:
            Nreads = len(vec[7])
            for i in range(Nreads):
                for j in range(vec[7][i]):
                    data.append((1996+i,1.0/float(vec[4])))
                    if vec[1]:
                        refereed_data.append((1996+i,1.0/float(vec[4])))
        cls.data = data
        cls.refereed_data = refereed_data

    @classmethod
    def post_process(cls):
        cls.results['type'] = cls.config_data_name
        if cls.value_histogram:
            Nentries = len(cls.value_histogram[0])
            for i in range(Nentries):
                year = cls.value_histogram[1][i]
                res = "%s:%s:%s:%s" % (cls.value_histogram[0][i],cls.refereed_value_histogram[0][i],cls.normalized_value_histogram[0][i],cls.refereed_normalized_value_histogram[0][i])
                cls.results[str(year)] = res

class RefereedCitationsHistogram(Histogram):
    '''
    This part of the citations histogram contains
    the refereed citations to both refereed and
    non-refereed papers
    '''
    config_data_name = 'refereed_citation_histogram'

    @classmethod
    def pre_process(cls):
        data = []
        refereed_data = []
        for vec in cls.attributes:
            for citation in vec[9]:
                if not vec[1]:
                    data.append((int(citation[0][:4]), 1.0/float(vec[4])))
                else:
                    refereed_data.append((int(citation[0][:4]), 1.0/float(vec[4])))
        cls.data = data
        cls.refereed_data = refereed_data

    @classmethod
    def post_process(cls):
        cls.results['type'] = cls.config_data_name
        if cls.value_histogram:
            Nentries = len(cls.value_histogram[0])
            for i in range(Nentries):
                year = cls.value_histogram[1][i]
                res = "%s:%s:%s:%s" % (cls.value_histogram[0][i],cls.refereed_value_histogram[0][i],cls.normalized_value_histogram[0][i],cls.refereed_normalized_value_histogram[0][i])
                cls.results[str(year)] = res

class NonRefereedCitationsHistogram(Histogram):
    '''
    This part of the citations histogram contains
    the non-refereed citations to both refereed and
    non-refereed papers
    '''
    config_data_name = 'non_refereed_citation_histogram'

    @classmethod
    def pre_process(cls):
        data = []
        refereed_data = []
        for vec in cls.attributes:
            for citation in vec[10]:
                if not vec[1]:
                    data.append((int(citation[0][:4]), 1.0/float(vec[4])))
                else:
                    refereed_data.append((int(citation[0][:4]), 1.0/float(vec[4])))
        cls.data = data
        cls.refereed_data = refereed_data

    @classmethod
    def post_process(cls):
        cls.results['type'] = cls.config_data_name
        if cls.value_histogram:
            Nentries = len(cls.value_histogram[0])
            for i in range(Nentries):
                year = cls.value_histogram[1][i]
                res = "%s:%s:%s:%s" % (cls.value_histogram[0][i],cls.refereed_value_histogram[0][i],cls.normalized_value_histogram[0][i],cls.refereed_normalized_value_histogram[0][i])
                cls.results[str(year)] = res