import os
GOOGLE_STORAGE_BUCKET = str(os.environ['STORAGE_BUCKET'])

# Base path of blobs stored
BASE_PATH = 'test/e2e'

# Uncomment to activate timer download functions from specified url
URL_COLLECTIONS = {
    'generics': {
        'method': 'GET',
        'url': 'https://jsonplaceholder.typicode.com/todos/1'
    }
}
