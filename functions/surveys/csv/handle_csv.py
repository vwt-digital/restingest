import os

from flask import Response

from surveys.csv.helpers import get_batch_surveys, create_csv_file


def create_survey_csv(bucket):
    """
    This function is called in the main() to create a csv file of the
    survey batch
    Allows calls to it to download the csv file
    :return:
    """
    surveys = get_batch_surveys(bucket_name=os.environ.get("BUCKET", bucket))

    return Response(
        create_csv_file(surveys),
        headers={
            "Content-Type": "text/csv",
            "Content-Disposition": 'attachment; filename="~/blobs.csv"',
        },
    )

