import os
import logging
import pandas as pd
import json

from google.cloud import storage

logger = logging.getLogger(__name__)


def flatten_dict(value):
    """
    Flattens a dictionary object with (nested) list values. For example:
    a_registration:  another_list_registration: {
                    _tt667dsfs: [ x: { y: fs56df64sd3} ]
                    }

    => { a_registration.another_list_registration._tt667dsfs.x.y: 'fs56df64sd3' }
    :param value:
    :return:
    """
    flat_dict__ = dict()
    for _key, _value in value.items():
        if isinstance(_value, list):
            torn = dict()
            for index, x in enumerate(_value):
                torn[f"items__{index}"] = pd.io.json.json_normalize(
                    x, sep="."
                ).to_dict(orient="records")[0]
                flat_dict__[_key] = torn
        else:
            flat_dict__[_key] = _value
    return flat_dict__


def create_csv_file(surveys):
    """
    Creates the csv file that gets downloaded exclusively data on request.
    And flatten sub question to a 2 dimensional data representation
    ** for example:
    locationSearch: {
        mast: 'x3srrR'
        typea: 'A type'
        another: [ anotherList: {
                    _tt667dsfs: fs56df64sd3}
                    ]
        }
    => locationSearch.mast: 'x3srrR' ...
    => locationSearch.another.anotherList._tt667dsfs: 'fs56df64sd3' ...
    :param surveys:
    :return:
    """
    data = dict()
    for k, v in surveys.items():
        for key, value in v["data"].items():
            if isinstance(value, list):
                flat_list = pd.DataFrame(value).to_dict(orient="records")[0]
                data[key] = pd.io.json.json_normalize(flat_list, sep=".").to_dict(
                    orient="records"
                )[0]
            elif isinstance(value, dict):
                data[key] = flatten_dict(value)
            else:
                data[key] = value

    data = pd.io.json.json_normalize(data, sep=".").to_dict(orient="records")[0]
    df = pd.DataFrame(json.loads(json.dumps(data)), index=[0]).transpose()
    return df.to_csv()


def get_batch_surveys(bucket_name):
    """
        lists all the surveys in the bucket
        - Using the a stringgetter() - batch them into a single dict file
    """
    storage_client = storage.Client(
        os.environ.get("PROJECT", "Specified environment variable is not set.")
    )

    bucket = storage_client.get_bucket(bucket_name)

    latest = list(bucket.list_blobs())[-1].download_as_string()
    logger.info("Downloaded Survey String", latest)
    return json.loads(latest)


def get_presentable_surveys(elements):
    """
    This method intends to filter survey data from source to data we mainly need for every survey
    by creating a neat dictionary with non-erroneous information ready for export
    :param elements:
    :return:
    """
    surveys = dict()
    for survey in elements:
        surveys[survey["id"]] = survey
    return surveys
