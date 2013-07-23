# general modules
import os
import time
import sys
import site
import urllib
import requests
import simplejson as json
from multiprocessing import Pool, current_process
from multiprocessing import Manager
# module for retrieving data from MongoDB
site.addsitedir('/proj/adsx/adsdata')
import adsdata
# metrics specific modules
from config import config
from adsstats import utils
import models
# initiate MongoDB session
session = adsdata.get_session()
# memory mapped data
manager = Manager()
publicationlist = manager.list()
publication_data= manager.list([])
ads_data = manager.dict()
pub_dict = manager.dict()
glob_data= manager.list([])
# for citation dictionary function
cit_dict = manager.dict()
ref_cit_dict = manager.dict()
non_ref_cit_dict = manager.dict()
# some global variables
global citation_dictionary
citation_dictionary = {}
global refereed_citation_dictionary
refereed_citation_dictionary = {}
global non_refereed_citation_dictionary
non_refereed_citation_dictionary = {}
# Definition of functions for data retrieval and processing
# A. Functions for re-arranging data structures
#    we data key'ed on bibcode
def merge_publications(dict):
    pub_dict[dict['bibcode']] = dict
    publicationlist.append(dict['bibcode'])

def get_citation_dictionary(bibcode):
    fl = 'bibcode,property,reference'
    papers = []
    q = 'citations(bibcode:%s)' % bibcode
    rsp = req(config.SOLR_URL, q=q, fl=fl, rows=config.MAX_HITS)
    cit_dict[bibcode] = []
    ref_cit_dict[bibcode] = []
    non_ref_cit_dict[bibcode] = []
    cits = []
    ref_cits = []
    non_ref_cits = []
    try:
        Nauths = max(1,len(pub_dict[bibcode]['author_norm']))
    except:
        Nauths = 1
    pubyear = int(bibcode[:4])
    for doc in rsp['response']['docs']:
        try:
            Nrefs = len(doc['reference'])
        except:
            Nrefs = 0
        cits.append((doc['bibcode'],Nrefs,Nauths,pubyear))
        if 'REFEREED' in doc['property']:
            ref_cits.append((doc['bibcode'],Nrefs,Nauths,pubyear))
        else:
            non_ref_cits.append((doc['bibcode'],Nrefs,Nauths,pubyear))
    cit_dict[bibcode] = cits
    ref_cit_dict[bibcode] = ref_cits
    non_ref_cit_dict[bibcode] = non_ref_cits

# B. Data gathering functions
def req(url, **kwargs):
    kwargs['wt'] = 'json'
    query_params = urllib.urlencode(kwargs)
    r = requests.get(url, params=query_params)
    return r.json()

def get_mongo_data(bbc):
    doc = session.get_doc(bbc)
    try:
        doc.pop("full", None)
    except:
        pass
    try:
        ads_data[bbc] = doc
    except:
        pass

def get_publication_data(biblist):
    fl = 'bibcode,reference,author_norm,property,read_count'
#    fl = ''
    list = " OR ".join(map(lambda a: "bibcode:%s"%a, biblist))
    q = '%s' % list
    rsp = req(config.SOLR_URL, q=q, fl=fl, rows=config.MAX_HITS)
    publication_data.append(rsp['response']['docs'])

def get_bibcodes_from_private_library(id):
    sys.stderr.write('Private libraries are not yet implemented')
    return []
# C. Creation of data vectors for stats calculations
def make_vectors(**args):
    attr_list = []
    for bibcode in publicationlist:
        vector = [str(bibcode)]
        try:
            properties = pub_dict[bibcode]['property']
        except:
            properties = []
        if 'REFEREED' in properties:
            vector.append(1)
        else:
            vector.append(0)
        try:
            Ncits = len(cit_dict[bibcode])
        except:
            Ncits = 0
        vector.append(Ncits)
        try:
            Ncits_ref = len(ref_cit_dict[bibcode])
        except:
            Ncits_ref = 0
        vector.append(Ncits_ref)
        try:
            Nauthors = max(1,len(pub_dict[bibcode]['author_norm']))
        except:
            Nauthors = 1
        vector.append(Nauthors)
        try:
            vector.append(sum(ads_data[bibcode]['reads']))
        except:
            vector.append(0)
        try:
            vector.append(sum(ads_data[bibcode]['downloads']))
        except:
            vector.append(0)
        try:
            vector.append(ads_data[bibcode]['reads'])
        except:
            vector.append([])
        try:
            vector.append(cit_dict[bibcode])
        except:
            vector.append([])
        try:
            vector.append(ref_cit_dict[bibcode])
        except:
            vector.append([])
        try:
            vector.append(non_ref_cit_dict[bibcode])
        except:
            vector.append([])
        attr_list.append(vector)

    return attr_list

# D. General data accumulation
def get_attributes(args):
    solr_url = config.SOLR_URL
    max_hits = config.MAX_HITS
    threads  = config.THREADS
    chunk_size = config.CHUNK_SIZE
    if 'query' in args:
        fl = 'bibcode,reference,author_norm,property,read_count'
        try:
            rsp = req(solr_url, q=args['query'], fl=fl, rows=max_hits)
            pubdata = rsp['response']['docs']
        except:
            sys.stderr.write('Solr pubdata query failed\n')
            pass
        bibcodes = map(lambda a: a['bibcode'], pubdata)
    elif 'bibcodes' in args:
        pubdata = []
        citdata = []
        bibcodes = map(lambda a: a.strip(), args['bibcodes'])
        print "Found %s bibcodes. Splitting in batches of: %s" % (len(bibcodes),chunk_size)
        biblists = list(utils.chunks(bibcodes,chunk_size))
        print "Getting publication data"
        stime = time.time()
        result=Pool(threads).map(get_publication_data,biblists)
        etime = time.time()
        duration = etime-stime
        print "duration: %s sec" % duration
        for adata in publication_data:
            pubdata += adata
    elif 'libid' in args:
        bibcodes = get_bibcodes_from_private_library(args['libid'])

    print "Merging publication data"
    stime = time.time()
    result = Pool(threads).map(merge_publications,pubdata)
    duration = time.time() - stime
    print "  duration: %s sec" % duration
    print "Getting citations (alternative) for %s bibcodes" % len(bibcodes)
    print "  # threads: %s" % threads
    stime = time.time()
    result=Pool(threads).map(get_citation_dictionary,bibcodes)
    duration = time.time() - stime
    print "  duration: %s sec" % duration
    Nciting = len(utils.flatten(cit_dict.values()))/2
    Nciting_ref = len(utils.flatten(ref_cit_dict.values()))/2
    print "  total: %s citations (%s refereed citations)" % (Nciting, Nciting_ref)
    print "Getting data from MongoDB"
    stime = time.time()
    result = Pool(threads).map(get_mongo_data,publicationlist)
    duration = time.time() - stime
    print "  duration: %s sec" % duration
    # Generate the list of document attribute vectors and then
    # sort this list by citations (descending).
    # The attribute vectors will be used to calculate the metrics
    print "Creating attribute vectors"
    stime = time.time()
    attr_list = make_vectors()
    duration = time.time() - stime
    print "  duration: %s sec" % duration
    print "Sorting attribute vectors"
    stime = time.time()
    attr_list = utils.sort_list_of_lists(attr_list,2)
    duration = time.time() - stime
    print "  duration: %s sec" % duration
    print "Ready for creating metrics"
    return attr_list,Nciting,Nciting_ref

# E. Function to call individual model data generation functions
#    in parallel
def generate_data(model_class):
    model_class.generate_data()
    glob_data.append(model_class.results)

# F. Format and export the end results
# Default: 'JSON' structure of metrics 'documents'

def format_results(**args):
# for now 'json' is the only output format offered
    try:
        format = args['format']
    except:
        format = 'json'

    doc = {}
    for entry in glob_data:
        data_dict = dict(entry)
        del data_dict['type']
        doc[entry['type']] = data_dict
    return json.dumps(doc)

# General metrics engine
def generate(**args):
    attr_list,num_cit,num_cit_ref = get_attributes(args)
    stats_models = []
    try:
        model_types = args['types'].split(',')
    except:
        model_types = config.DEFAULT_MODELS
    # Instantiate the metrics classes, defined in the 'models' module
    for model_class in models.data_models(models=model_types):
        model_class.attributes = attr_list
        model_class.num_citing = num_cit
        model_class.num_citing_ref = num_cit_ref
        model_class.results = {}
        stats_models.append(model_class)

    rez=Pool(config.THREADS).map(generate_data, stats_models)

#    results = format_results()
    return results
