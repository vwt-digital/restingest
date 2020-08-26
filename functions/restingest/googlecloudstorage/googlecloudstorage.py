from retry import retry
from google.cloud import storage
from requests.exceptions import ConnectionError
from abstractcloudstorage import CloudStorageInterface


class GoogleCloudStorage(CloudStorageInterface):

    def __init__(self, bucket_name):
        self.storageClient = storage.Client()
        self.storageBucket = storage.Client().get_bucket(bucket_name)
        self.bucket_name = bucket_name

    @retry(ConnectionError, tries=3, delay=2, backoff=2, logger=None)
    def storeBlob(self, path, data, content_type, chunk_size=5242880):
        blob = self.storageBucket.blob(path, chunk_size)
        blob.upload_from_string(data, content_type)
