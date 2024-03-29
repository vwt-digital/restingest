import hashlib
import hmac
import json
import logging
import os
import re

import config
from flask import g, request
from jwkaas import JWKaas
from requests.exceptions import ConnectionError

from utils import get_secret

my_jwkaas = None
api_key_secret = None
api_key_secret_conversion = None

if hasattr(config, "OAUTH_JWKS_URL"):
    my_jwkaas = JWKaas(
        config.OAUTH_EXPECTED_AUDIENCE,
        config.OAUTH_EXPECTED_ISSUER,
        jwks_url=config.OAUTH_JWKS_URL,
    )

if hasattr(config, "API_KEY_SECRET"):
    api_key_secret = get_secret(os.environ["PROJECT_ID"], config.API_KEY_SECRET)

if hasattr(config, "API_KEY_SECRET_CONVERSION"):
    api_key_secret_conversion = config.API_KEY_SECRET_CONVERSION


class LevelRaiser(logging.Filter):
    def filter(self, record):
        if record.levelno == logging.WARNING:
            record.levelno = logging.INFO
            record.levelname = logging.getLevelName(logging.INFO)
        return True


def configure_library_logging():
    library_root_logger = logging.getLogger(request.__name__)
    library_root_logger.addFilter(LevelRaiser())


def refine_token_info(token_info):
    if hasattr(config, "OAUTH_APPID") and token_info and "appid" in token_info:
        for appid_info in config.OAUTH_APPID:
            if token_info["appid"] == appid_info["appid"]:
                token_info["scopes"] = appid_info["scopes"]
    return token_info


def info_from_oauth2(token):
    """
    Validate and decode token.
    Returned value will be passed in 'token_info' parameter of your operation function, if there is one.
    'sub' or 'uid' will be set in 'user' parameter of your operation function, if there is one.
    'scope' or 'scopes' will be passed to scope validation function.
    :param token Token provided by Authorization header
    :type token: str
    :return: Decoded token information or None if token is invalid
    :rtype: dict | None
    """
    if hasattr(config, "DEBUG_LOGGING") and config.DEBUG_LOGGING is True:
        configure_library_logging()

    token_info = get_token_info(token)

    if not token_info and "X-Orig-Auth" in request.headers:
        logging.info(
            "Validation of 'Authorization' header failed, trying 'X-Orig-Auth' header"
        )
        token_info = get_token_info(
            extract_bearer_token(request.headers["X-Orig-Auth"])
        )

    return refine_token_info(token_info)


def get_token_info(token):
    try:
        token_info = my_jwkaas.get_token_info(token)
    except ConnectionError as e:
        logging.error(f"An error occurred during retrieval of JWK token: {str(e)}")
        return None
    else:
        return token_info


def info_from_apikey(apikey, required_scopes):
    if not api_key_secret:
        logging.error(
            "API Key authorization configured but API key secret is missing from config."
        )
    elif apikey_conversion_and_validation(api_key_secret_conversion, apikey):
        g.user = "apikeyuser"
        return {"sub": "apikeyuser"}

    return None


def extract_bearer_token(token):
    """
    Remove Bearer from authorization header
    """

    re_match = re.match("^Bearer\\s+(.*)", token)

    if re_match:
        return re_match.group(1)

    return None


def get_request_body_as_bytes():
    if request.is_json:
        req_body = json.dumps(
            request.get_json(silent=True), separators=(",", ":")
        )  # Retrieve JSON as minified object
    else:
        req_body = request.data

    if not isinstance(req_body, bytes):
        req_body = bytes(req_body, "utf8")

    return req_body


def apikey_conversion_and_validation(conversion, apikey):
    if not conversion and apikey == api_key_secret:
        return True

    if conversion == "hmac_sha256":
        payload = get_request_body_as_bytes()  # Retrieve request data as bytes object
        secret = api_key_secret.encode()  # Retrieve API Key as bytes object

        # Construct HMAC generator with our secret as key, and SHA-256 as the hashing function
        signature = hmac.new(key=secret, msg=payload, digestmod=hashlib.sha256)

        # Create the hex digest and append prefix to match the GitHub request format
        digest = f"sha256={signature.hexdigest()}"

        if hmac.compare_digest(digest, apikey):
            return True

    return False
