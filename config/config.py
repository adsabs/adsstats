import os

_basedir = os.path.abspath(os.path.dirname(__file__))

class AppConfig(object):

#    LOG_DIR = os.path.exists(_basedir + "/logs") and _basedir + "/logs" or "."
    MONGO_DATABASE = 'adsdata'
    MONGO_HOST = "localhost"
    MONGO_PORT = 27017
    MONGO_SAFE = True
    MONGO_USER = 'adsdata'
    MONGO_PASSWORD = ''
    MONGO_DOCS_COLLECTION = 'docs'
    MONGO_DOCS_DEREF_FIELDS = [('docs','full'), ('docs','ack')]
    
    MONGO_DATA_COLLECTIONS = {
        'bibstems': '/proj/ads_abstracts/config/bibstems.dat',
        'fulltext_links': '/proj/ads_abstracts/config/links/fulltext/all.links',
        'refereed': '/proj/ads_abstracts/config/links/refereed/all.links',
        'readers': '/proj/ads_abstracts/config/links/alsoread_bib/all.links',
        'references': '/proj/ads_abstracts/config/links/reference/all.links',
        'citations': '/proj/ads_abstracts/config/links/citation/all.links',
        'accnos': '/proj/ads_abstracts/config/bib2accno.dat',
        'docmetrics': '/proj/ads_abstracts/config/links/relevance/docmetrics.tab',
        'eprint_matches':'/proj/ads_abstracts/config/links/preprint/arxiv2pub.list',
        'eprint_mapping':'/proj/ads_abstracts/config/links/preprint/arxiv.dat',
        'reads':'/proj/ads_abstracts/config/links/reads/all.links',
        'downloads':'/proj/ads_abstracts/config/links/reads/downloads.links',
        'grants':'/proj/ads_abstracts/config/links/grants/all.links'
        }
    
    MONGO_DATA_LOAD_BATCH_SIZE = 100000

    SOLR_URL = 'http://adswhy:9000/solr/collection1/select'
try:
    from local_config import LocalConfig
except ImportError:
    LocalConfig = type('LocalConfig', (object,), dict())

for attr in filter(lambda x: not x.startswith('__'), dir(LocalConfig)):
    setattr(AppConfig, attr, LocalConfig.__dict__[attr])

config = AppConfig
