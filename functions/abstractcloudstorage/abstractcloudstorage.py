from abc import ABC, abstractmethod


class CloudStorageInterface(ABC):

    @abstractmethod
    def storeBlob(self, path, data):
        pass

    @abstractmethod
    def is_log_storage(self):
        return False
