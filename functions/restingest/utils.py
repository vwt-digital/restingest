import base64

from google.cloud import kms_v1
from google.cloud import secretmanager_v1


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
