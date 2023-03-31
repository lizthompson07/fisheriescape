from default_conf import *

# Everything set here will override the default config

CACHES = {
    'default': {
        # 'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        # Don't use cache on local environment.
        # Uncommented previous line and comment the next one if you want to test the cache locally
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        'LOCATION': 'cache',
    }
}
