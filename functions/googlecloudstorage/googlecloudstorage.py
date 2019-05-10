import logging

import config

from google.cloud import storage
from abstractcloudstorage import CloudStorageInterface


class GoogleCloudStorage(CloudStorageInterface):

    def __init__(self, bucket_name):
        self.storageClient = storage.Client()
        self.storageBucket = storage.Client().get_bucket(bucket_name)
        self.bucket_name = bucket_name

    def storeBlob(self, path, data):
        logging.info("Storing to Google Storage [%s:%s] data: [%s]", self.bucket_name, path, data)
        blob = self.storageBucket.blob(path)
        blob.upload_from_string(data, 'application/json')

    def is_log_storage(self):
        if hasattr(config, 'GOOGLE_LOG_BUCKET'):
            return self.bucket_name == config.GOOGLE_LOG_BUCKET
        else:
            return False
