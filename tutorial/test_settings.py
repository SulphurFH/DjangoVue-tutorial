#!/usr/bin/env python
from .settings import *
DISABLE_SIGN_CHECK = True


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'tutorial',
        "TEST": {
            'CHARSET': 'utf8',
            'COLLATION': 'utf8_general_ci',
        }
    },
}

# Log
for key, handler in LOGGING['handlers'].items():
    if handler.get('filename', None):
        handler['filename'] = os.path.join(LOG_ROOT, "logs", os.path.basename(handler['filename']))
