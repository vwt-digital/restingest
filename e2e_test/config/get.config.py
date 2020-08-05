import os
GOOGLE_STORAGE_BUCKET = str(os.environ['STORAGE_BUCKET'])

# Base path of blobs stored
BASE_PATH = 'test/e2e'

# Uncomment to activate timer download functions from specified url
URL_COLLECTIONS = {
    'generics-json': {
        'method': 'GET',
        'url': 'http://httpbin.org/json'
    },
    'generics-xml': {
        'method': 'GET',
        'url': 'http://httpbin.org/xml'
    },
    'generics-html': {
        'method': 'GET',
        'url': 'http://httpbin.org/html'
    }
}
