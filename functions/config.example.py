# Uncomment and specify to store to Azure cloud storage
#   AZURE_STORAGE_ACCOUNT = 'storageaccountname'
#   AZURE_STORAGE_KEY = '***'
#   AZURE_STORAGE_CONTAINER = 'containername'

# Uncomment and specify to store to Google cloud storage
#   GOOGLE_STORAGE_BUCKET = 'storagebucketname'

# Base path of blobs stored
BASE_PATH = 'base/path'

# Uncomment to activate incoming data filtering
# PI_FILTER = []

# Uncomment to activate timer download function from specified url
#    URL_COLLECTIONS = {
#        'url1': {
#            'method': 'GET',
#            'url': 'https://get.from/url1'
#        },
#        'urencnt': {
#            'method': 'POST',
#            'url': 'https://ometaframework-test.vwtelecom.com:50556/api/ADMrecord/GetAllMultiRecord',
#            'authorization': {
#                'type': 'Basic',
#                'credentials': '<base64encoded>' # bas64 encoded
#            },
#           'headers': {},
#            'body': {
#                'type': 'application/json',
#                'content': {
#                   "server": "swvwtv021",
#                   "view": "vwListGeplandeUrenregelsCount_L2V35_NS",
#                   "port": "2005",
#                   "Object": "VWTUren",
#                   "Context": {
#                        "AantalUrenAchteruit": "40"
#                    }
#                }
#            }
#        },
#        'urenover': {
#            'method': 'POST',
#            'url': 'https://ometaframework-test.vwtelecom.com:50556/api/ADMrecord/GetAllMultiRecord',
#            'authorization': {
#                'type': 'Basic',
#                'credentials': '<base64encoded>'  # bas64 encoded
#            },
#            'headers': {},
#            'body': {
#                'type': 'application/json',
#                'content': {
#                    "server": "swvwtv021",
#                    "view": "vwListGeplandeUrenregels_L2V35_NS",
#                    "port": "2005",
#                    "Object": "VWTUren",
#                    "Context": {
#                        "AantalUrenAchteruit": "10000",
#                        "Skip": "0",
#                        "Take": "100"
#                    }
#                }
#            }
#        },
#        'urendesc': {
#            'method': 'POST',
#            'url': 'https://ometaframework-test.vwtelecom.com:50556/api/ADMrecord/GetAllMultiRecord',
#            'authorization': {
#                'type': 'Basic',
#                'credentials': '<base64encoded>'  # bas64 encoded
#            },
#            'headers': {},
#            'body': {
#                'type': 'application/json',
#                'content': {
#                    "server": "swvwtv021",
#                    "view": "vwListUrenCategorien_L2V35_NS",
#                    "port": "2005",
#                    "Object": "VWTUren",
#                }
#            }
#        }
#    }
