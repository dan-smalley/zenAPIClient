# -*- coding: utf-8 -*-

import requests
from zenossapi.apiclient import ZenossAPIClientError, ZenossAPIClientAuthenticationError


class ZenossRouter(object):
    """
    Base class for Zenoss router classes
    """
    def __init__(self, url, headers, ssl_verify, endpoint, action):
        self.api_url = url
        self.api_headers = headers
        self.ssl_verify = ssl_verify
        self.api_endpoint = endpoint
        self.api_action = action

    def _make_request_data(self, method, data):
        return dict(
            action=self.api_action,
            method=method,
            data=[data],
            tid=1,
        )

    def _router_request(self, data):
        # Disable warnings from urllib3 if ssl_verify is False, otherwise
        # every request will print an InsecureRequestWarning
        if not self.ssl_verify:
            requests.urllib3.disable_warnings()

        response = requests.post(
            '{0}/{1}'.format(self.api_url, self.api_endpoint),
            headers=self.api_headers,
            json=data,
            verify=self.ssl_verify,
        )

        if response.ok:
            if response.url.find('login_form') > -1:
                raise ZenossAPIClientAuthenticationError('API Login Failed')
            response_json = response.json()
            if response_json['result']:
                if 'success' in response_json['result']:
                    if not response_json['result']['success']:
                        raise ZenossAPIClientError('Request failed: {}'.format(response_json['result']['msg']))
            else:
                raise ZenossAPIClientError('Request failed, no response data returned!')

            return response_json['result']

        else:
            raise ZenossAPIClientError('Request failed: {0} {1}'.format(response.status_code, response.reason))
