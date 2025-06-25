# -*- coding: utf-8 -*-
import logging
import requests
import json
from requests import ReadTimeout
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
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
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=2, min=2, max=20), retry=retry_if_exception_type(ReadTimeout))
    def _router_request(self, data, response_timeout=None):
        # Disable warnings from urllib3 if ssl_verify is False, otherwise
        # every request will print an InsecureRequestWarning
        if not self.ssl_verify:
            requests.urllib3.disable_warnings()

        if response_timeout is None:
            response_timeout = self.api_timeout

        try:
            response = requests.request("POST",
                '{0}/{1}'.format(self.api_url, self.api_endpoint),
                headers=self.api_headers,
                data=json.dumps(data).encode('utf-8'),
                verify=self.ssl_verify,
                timeout=response_timeout
            )
        except ConnectionError as e:
            logging.warning('Error calling Zenoss API: %s\n    Request data: %s' % (e, data))
            # Atempt to display the failure reason from Zenoss
            try:
                logging.warning("Query failure reason from Zensos: %s" % response['result']['msg'])
            except:
                pass

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