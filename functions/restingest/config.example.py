# Uncomment and specify to store to Azure cloud storage
#   AZURE_STORAGE_ACCOUNT = 'storageaccountname'
#   AZURE_STORAGE_KEY = '***'
#   AZURE_STORAGE_CONTAINER = 'containername'

# Uncomment and specify to store to Google cloud storage
#   GOOGLE_STORAGE_BUCKET = 'storagebucketname'

# Base path of blobs stored
BASE_PATH = "base/path"

# Use brotli compression
# COMPRESSION = True

# Uncomment and specify to add authentication using OAuth2
# OAUTH_EXPECTED_AUDIENCE = 'https://expected.audience'
# OAUTH_EXPECTED_ISSUER = 'https://expected.issuer/'
# OAUTH_JWKS_URL = 'https://publickeyurl/'
# OAUTH_APPID = [{'appid': 'actual_appid', 'scopes': ['scope1', 'scope2']}]


# Uncomment to activate timer download function from specified url
#    URL_COLLECTIONS = {
#        'url1': {
#            'method': 'GET',
#            'url': 'https://get.from/url1'
#        },
#        'url2': {
#            'method': 'POST',
#            'url': 'https://post.from/url',
#            'authorization': {
#                'type': 'Basic',
#                'credentials': '<base64encoded>' # bas64 encoded
#            },
#            'headers': {},
#            'body': {
#                'type': 'application/json',
#                'content': {
#                }
#            }
#        }
#    }


# Uncomment if you want validation errors to show up as info logging and not error logging
# DEBUG_LOGGING = True
