import logging
import json
from typing import List, Any, Dict, Tuple, Union, Sequence

import oauthlib.oauth2
import requests_oauthlib


DEFAULT_OAUTH2_URL = 'https://services.sentinel-hub.com/oauth'

logger = logging.getLogger(__name__)

class ApiBase:
    def __init__(self, client_id, client_secret, oauth2_url=DEFAULT_OAUTH2_URL, session=None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.oauth2_url = oauth2_url
        self.token = None

        if session is not None:
            self.session = session
        else:
            client = oauthlib.oauth2.BackendApplicationClient(client_id=client_id)
            self.session = requests_oauthlib.OAuth2Session(client=client)

    def close(self):
        self.session.close()

    @property
    def token_info(self) -> Dict[str, Any]:
        resp = self.session.get(f'{self.oauth2_url}/tokeninfo')
        return json.loads(resp.content)

    def refresh_token(self):
        token_url = f'{self.oauth2_url}/token'
        logger.info(f'Fetching new access token from {token_url}')
        self.token = self.session.fetch_token(
            token_url=token_url,
            client_id=self.client_id,
            client_secret=self.client_secret
        )
        return self.token

    def with_retry(self, command, *args, **kwargs):
        """ Utility function to wrap a function call that uses the session.
            Catches TokenExpiredErrors and retries after refreshing the token.
        """
        if not self.token:
            self.refresh_token()

        retried = False
        while True:
            try:
                return command(self.session, *args, **kwargs)
            except oauthlib.oauth2.TokenExpiredError:
                if retried:
                    raise

                logger.info('Token expired')
                self.refresh_token()
                retried = True
