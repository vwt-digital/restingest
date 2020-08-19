import base64
import requests

from google.cloud import kms_v1
from google.cloud import secretmanager_v1

from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


def decrypt_secret(project_id, kms_region, kms_keyring, kms_key, encrypted_secret_base64):
    """
    Returns a KMS decrypted secret.
    """

    client = kms_v1.KeyManagementServiceClient()

    key_name = client.crypto_key_path_path(
        project_id,
        kms_region,
        kms_keyring,
        kms_key)

    encrypted_secret = base64.b64decode(encrypted_secret_base64)
    decrypt_response = client.decrypt(key_name, encrypted_secret)
    payload = decrypt_response.plaintext.decode("utf-8").replace('\n', '')

    return payload


def get_secret(project_id, secret_id):
    """
    Returns a Secret Manager secret.
    """

    client = secretmanager_v1.SecretManagerServiceClient()

    secret_name = client.secret_version_path(
        project_id,
        secret_id,
        'latest')

    response = client.access_secret_version(secret_name)
    payload = response.payload.data.decode('UTF-8')

    return payload


def get_requests_session(retries=3, backoff=1, status_forcelist=(500, 502, 503, 504)):
    """
    Returns a requests session with retry enabled.
    """

    session = requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff,
        status_forcelist=status_forcelist,
    )

    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    return session
