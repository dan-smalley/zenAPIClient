# -*- coding: utf-8 -*-
import logging
from time import sleep
import requests
import json
from requests.exceptions import ConnectionError
from zenossapi.apiclient import ZenossAPIClientError, ZenossAPIClientAuthenticationError


class ZenossRouter(object):
    """
    Base class for Zenoss router classes
    """
    def __init__(self, url, headers, ssl_verify, endpoint, action, timeout=5, maxattempts=3):
        self.api_url = url
        self.api_headers = headers
        self.ssl_verify = ssl_verify
        self.api_endpoint = endpoint
        self.api_action = action
        self.api_timeout = timeout
        self.api_maxattempts = maxattempts

    def _check_uid(self, uid):
        if not uid.startswith('Devices'):
            if uid.startswith('/'):
                uid = 'Devices{0}'.format(uid)
            else:
                uid = 'Devices/{0}'.format(uid)

        return uid

    def _make_request_data(self, method, data=None):
        if data is None:
            return dict(
                action=self.api_action,
                method=method,
                tid=1,
            )
        else:
            return dict(
                action=self.api_action,
                method=method,
                data=[data],
                tid=1,
            )

    def _router_request(self, data, response_timeout=None):
        # Disable warnings from urllib3 if ssl_verify is False, otherwise
        # every request will print an InsecureRequestWarning
        if not self.ssl_verify:
            requests.urllib3.disable_warnings()

        if response_timeout is None:
            response_timeout = self.api_timeout

        tries = 0
        while tries < self.api_maxattempts:
            try:
                response = requests.request("POST",
                    '{0}/{1}'.format(self.api_url, self.api_endpoint),
                    headers=self.api_headers,
                    data=json.dumps(data).encode('utf-8'),
                    verify=self.ssl_verify,
                    timeout=response_timeout
                )
                break
            except ConnectionError as e:
                logging.warning('Error calling Zenoss API attempt %i/%i\n    Error: %s\n    Request data: %s' % (tries, self.api_maxattempts, e, data))
                # Atempt to display the failure reason from Zenoss
                try:
                    logging.warning("Query failure reason from Zensos: %s" % response['result']['msg'])
                except:
                    pass
                if tries == self.api_maxattempts:
                    raise ZenossAPIClientError('Unable to connect to Zenoss server {0}: {1}'.format(self.api_url, e))
                tries += 1

        if response.ok:
            if response.url.find('login_form') > -1:
                raise ZenossAPIClientAuthenticationError('API Login Failed')
            response_json = response.json()
            if 'result' in response_json:
                if response_json['result']:
                    if 'success' in response_json['result']:
                        if not response_json['result']['success']:
                            raise ZenossAPIClientError('Request failed: {}'.format(response_json['result']['msg']))
            else:
                raise ZenossAPIClientError('Request failed, no response data returned!')

            return response_json['result']

        else:
            raise ZenossAPIClientError('Request failed: {0} {1}'.format(response.status_code, response.reason))