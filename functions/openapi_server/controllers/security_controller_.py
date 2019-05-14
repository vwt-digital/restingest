import config
from jwkaas import JWKaas

my_jwkaas = None

if hasattr(config, 'OAUTH_JWKS_URL'):
    my_jwkaas = JWKaas(config.OAUTH_EXPECTED_AUDIENCE,
                       config.OAUTH_EXPECTED_ISSUER,
                       jwks_url=config.OAUTH_JWKS_URL)


def refine_token_info(token_info):
    if token_info and 'appid' in token_info:
        try:
            for appid_info in config.OAUTH_APPID:
                if token_info['appid'] == appid_info['appid']:
                    token_info['scopes'] = appid_info['scopes']
        except NameError:
            pass
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
    return refine_token_info(my_jwkaas.get_token_info(token))
