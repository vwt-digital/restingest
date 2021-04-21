import logging
import os
import re

import config
from flask import g, request
from jwkaas import JWKaas
from utils import get_secret

my_jwkaas = None
api_key_secret = None

if hasattr(config, "OAUTH_JWKS_URL"):
    my_jwkaas = JWKaas(
        config.OAUTH_EXPECTED_AUDIENCE,
        config.OAUTH_EXPECTED_ISSUER,
        jwks_url=config.OAUTH_JWKS_URL,
    )

if hasattr(config, "API_KEY_SECRET"):
    api_key_secret = get_secret(os.environ["PROJECT_ID"], config.API_KEY_SECRET)


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

    token_info = my_jwkaas.get_token_info(token)

    if not token_info and "X-Orig-Auth" in request.headers:
        logging.info(
            "Validation of 'Authorization' header failed, trying 'X-Orig-Auth' header"
        )
        token_info = my_jwkaas.get_token_info(
            extract_bearer_token(request.headers["X-Orig-Auth"])
        )

    return refine_token_info(token_info)


def info_from_apikey(apikey, required_scopes):
    if not api_key_secret:
        logging.error(
            "API Key authorization configured but API key secret is missing from config."
        )
    elif apikey == api_key_secret:
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
