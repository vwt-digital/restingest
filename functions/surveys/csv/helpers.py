import os
import logging
import pandas as pd
import json

from google.cloud import storage

logger = logging.getLogger(__name__)


def create_csv_file(surveys):
    """
    Creates the csv file that gets downloaded on request
    :param surveys:
    :return:
    """
    return pd.DataFrame(surveys).to_csv()


def get_batch_surveys(bucket_name):
    """
        lists all the surveys in the bucket
        - Using the a stringgetter() - batch them into a single dict file
    """
    storage_client = storage.Client(os.environ.get('PROJECT', 'Specified environment variable is not set.'))

    bucket = storage_client.get_bucket(bucket_name)
    surveys = {}
    blobs = bucket.list_blobs()
    content = json.loads(blobs[:-1].download_as_string(), encoding="utf-8")
    logger.info('Downloaded Survey String', content)
    surveys["latest"] = dict(content)
    return surveys


def get_presentable_surveys(elements):
    """
    This method intends to filter survey data from source to data we mainly need for every survey
    by creating a neat dictionary with non-erroneous information ready for export
    :param elements:
    :return:
    """
    surveys = dict()
    for survey in elements:
        surveys[survey['id']] = survey
    return pd.DataFrame(surveys).to_json()
