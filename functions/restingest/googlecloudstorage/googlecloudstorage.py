from retry import retry
from google.cloud import storage
from requests.exceptions import ConnectionError
from abstractcloudstorage import CloudStorageInterface


class GoogleCloudStorage(CloudStorageInterface):

    def __init__(self, bucket_name):
        self.storageClient = storage.Client()
        self.storageBucket = storage.Client().get_bucket(bucket_name)
        self.bucket_name = bucket_name

    @retry(ConnectionError, tries=3, delay=2)
    def storeBlob(self, path, data, content_type):
        blob = self.storageBucket.blob(path)
        blob.upload_from_string(data, content_type)
