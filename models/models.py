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
