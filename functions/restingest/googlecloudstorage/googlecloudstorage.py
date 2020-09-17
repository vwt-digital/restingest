import brotli

from retry import retry
from google.cloud import storage
from requests.exceptions import ConnectionError
from abstractcloudstorage import CloudStorageInterface


class GoogleCloudStorage(CloudStorageInterface):

    def __init__(self, bucket_name, compression=False):
        self.storageClient = storage.Client()
        self.storageBucket = storage.Client().get_bucket(bucket_name)
        self.bucket_name = bucket_name
        self.compression = compression

    @retry(ConnectionError, tries=3, delay=5, backoff=2, logger=None)
    def storeBlob(self, path, data, content_type, chunk_size=5242880):
        blob = self.storageBucket.blob(path, chunk_size)
        if self.compression:
            data = brotli.compress(data.encode("utf-8"))
            blob.content_encoding = 'br'
        blob.upload_from_string(data, content_type)
