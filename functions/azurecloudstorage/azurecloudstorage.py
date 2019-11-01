import logging

from azure.storage.blob import BlockBlobService
from abstractcloudstorage import CloudStorageInterface


class AzureCloudStorage(CloudStorageInterface):

    def __init__(self, account, key, container):
        self.block_blob_service = BlockBlobService(account_name=account, account_key=key)
        self.container_name = container
        self.block_blob_service.create_container(self.container_name)

    def storeBlob(self, path, data, content_type):
        logging.info("Storing to Azure [%s:%s] data: [%s]", self.container_name, path, data)
        self.block_blob_service.create_blob_from_text(self.container_name, blob_name=path, text=data)
