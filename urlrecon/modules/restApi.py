########################################################################################################
#                                                                                                      #
#                                                                                                      #
#                                REST API DRIVERS                                                      #
#                                                                                                      #
#               AUTHOR: SRINIVAS PISKALA GANESH BABU                                                   #
#                                                                                                      #
#               DESCRIPTION: (BASE MODULE)                                                             #
#                   The HTTP Rest Api Calls to Fetch data from a server                                #
#                   and return them in valid formats like Json and HTML-Data                           #
#                                                                                                      #
#               FUNCTIONS:                                                                             #
#                   * getRequest    - Used extensively in the project                                  #
#                   * postRequest   - Provisions for a POST request                                    #
#                   * deleteRequest - Provisions for a DELETE request                                  #
#                                                                                                      #
########################################################################################################

import logging
import requests
import json

logger = logging.getLogger(__name__)

REQUEST_TIMEOUT = 10  # seconds


class httpRequest:
    """Holds the restApi calls like get, post and delete.
    Exposes API to make HTTP/HTTPS requests.
    """

    def __init__(self, url):
        self.url = url

    def get_request(self, headers=None, type=None, auth=None):
        """Performs a HTTP/HTTPS GET request.

        Args:
            headers: Optional request headers dict.
            type: Output format — "json", "header", or None (returns text).
            auth: Optional authentication tuple.

        Returns:
            Response as JSON dict, headers dict, or text string. None on error.
        """
        if not headers:
            headers = {
                'user-agent': (
                    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:32.0) '
                    'Gecko/20100101 Firefox/32.0'
                ),
            }

        if str(type).lower() == "json":
            headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
            try:
                response = requests.get(self.url, headers=headers, timeout=REQUEST_TIMEOUT)
                try:
                    return response.json()
                except ValueError as e:
                    if str(e).lower().strip() == "no json object could be decoded":
                        return response.text
                    else:
                        logger.warning("JSON decode error for %s: %s", self.url, e)
                        return None
            except Exception as e:
                logger.warning("GET request to %s failed: %s", self.url, e)
                return None

        elif str(type) == "header":
            try:
                response = requests.get(self.url, headers=headers, timeout=REQUEST_TIMEOUT)
                return response.headers
            except requests.exceptions.SSLError:
                # SSL cert error — downgrade to HTTP and follow the redirect chain
                try:
                    http_url = self.url.replace("https://", "http://")
                    response = requests.get(
                        http_url, headers=headers,
                        allow_redirects=True, timeout=REQUEST_TIMEOUT
                    )
                    return response.headers
                except Exception as inner_e:
                    logger.warning("Header GET (http fallback) to %s failed: %s", self.url, inner_e)
                    return None
            except Exception as e:
                logger.warning("Header GET to %s failed: %s", self.url, e)
                return None

        elif str(type) == "header_noverify":
            # Last-resort fingerprint for servers with self-signed / expired certs.
            # TLS verification is intentionally disabled — only used for recon.
            try:
                import urllib3
                urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
                response = requests.get(
                    self.url, headers=headers,
                    timeout=REQUEST_TIMEOUT, verify=False
                )
                return response.headers
            except Exception as e:
                logger.warning("Header GET (no-verify) to %s failed: %s", self.url, e)
                return None

        else:
            try:
                response = requests.get(self.url, headers=headers, timeout=REQUEST_TIMEOUT)
                return response.text
            except Exception as e:
                logger.warning("GET request to %s failed: %s", self.url, e)
                return None

        if auth:
            try:
                response = requests.get(self.url, auth=auth, timeout=REQUEST_TIMEOUT)
                return response.text
            except Exception as e:
                logger.warning("Authenticated GET to %s failed: %s", self.url, e)
                return None

    def post_request(self, auth=None, body=None):
        """Performs an HTTP POST request."""
        response = requests.post(self.url, data=body, auth=auth, timeout=REQUEST_TIMEOUT)
        self.post_response = response.text
        return self.post_response

    def delete_request(self, auth=None):
        """Performs an HTTP DELETE request."""
        response = requests.delete(self.url, auth=auth, timeout=REQUEST_TIMEOUT)
        self.delete_response = response.text
        return self.delete_response
