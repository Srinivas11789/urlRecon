############################################################################################################
#                                                                                                          #
#                                                                                                          #
#                          Domain Information Fetch Module                                                 #
#                                                                                                          #
#               AUTHOR: SRINIVAS PISKALA GANESH BABU                                                       #
#                                                                                                          #
#               DESCRIPTION:                                                                               #
#                   Creates a class object for the URL input, fetches the:                                 #
#                    * Domain Name                                                                         #
#                    * IP address                                                                          #
#                    * DNS IP Information - A Record [IPv4]                                                #
#                    * Server Fingerprint                                                                  #
#                    * Geo Location of the Server                                                          #
#                                                                                                          #
#               FUNCTIONS:                                                                                 #
#                   * __init__          - Fill the object with information                                 #
#                   * domain_ip_fetch   - Obtain the IP of the domain                                     #
#                   * domain_stripper   - Strip the domain from the URL                                   #
#                   * whois_info_fetch  - Fetch whois information from Domain and IP                       #
#                   * dns_info_fetch    - Fetch the DNS IP record                                          #
#                   * server_fingerprint - Obtain server fingerprint from headers                          #
#                   * geo_locate        - Locate the IP via well-known API                                 #
#                                                                                                          #
############################################################################################################

import json
import logging
import os
import re
import socket
import warnings

warnings.filterwarnings("ignore", category=UserWarning)

import ipwhois
import dns.resolver

try:
    from . import restApi
except ImportError:
    import restApi  # noqa: E402  (direct-script fallback)

logger = logging.getLogger(__name__)

# API endpoints
IPAPI_URL = "https://ipapi.co/{ip}/json"
IPAPI_KEY_URL = "https://ipapi.co/{ip}/json/?key={key}"
WHOISCOM_URL = "https://www.whois.com/whois/{domain}"


class domainInfo:
    """Given a URL, returns an object containing all domain intelligence."""

    def __init__(self, domain):
        self.url = domain.strip()
        self.domain = self.domain_stripper(self.url)
        self.ip = self.domain_ip_fetch()
        self.whois = self.whois_info_fetch()
        self.dns = self.dns_info_fetch()
        self.server_fingerprint = self.server_fingerprint(self.url)
        self.geolocation = self.geo_locate()

    def domain_ip_fetch(self):
        """Resolve domain to IPv4 address via socket."""
        try:
            return socket.gethostbyname(self.domain)
        except Exception as e:
            logger.warning("Domain resolving error for %s: %s", self.domain, e)
            return None

    def domain_stripper(self, domain):
        """Strip the bare hostname from a URL or plain domain string.

        Accepts:
            - Full URLs: ``https://www.example.co.uk/path``
            - Plain domains: ``www.example.com``

        Returns:
            Hostname string, or ``""`` if the input cannot be parsed.
        """
        # Plain hostname/domain (no scheme) — matches labels with dots and a
        # TLD of 2 or more characters (fixes the original 3-char TLD limit).
        if re.match(r"^[a-zA-Z0-9._-]+\.[a-z]{2,}$", domain.strip()):
            return domain.strip()

        # Full URL — extract the host portion after the scheme
        extract_domain = re.search(r"^htt[a-z]+://([a-zA-Z0-9_.-]+)[/]?", domain)
        if extract_domain and extract_domain.group(1):
            return extract_domain.group(1)

        logger.warning("URL provided is invalid: %s", domain)
        return ""

    def whois_info_fetch(self):
        """Fetch WHOIS data for the domain's IP (via ipwhois) and from whois.com."""
        whois_data = {}

        try:
            whois_info = ipwhois.IPWhois(self.ip).lookup_rdap()
            whois_data["IpWhoIsResult"] = whois_info
        except Exception as e:
            logger.warning("IPWhois lookup failed for %s: %s", self.ip, e)
            whois_data["IpWhoIsResult"] = ""

        try:
            whois_dict = {}
            raw = restApi.httpRequest(WHOISCOM_URL.format(domain=self.domain)).get_request()
            if raw:
                html_strip = re.search(
                    r'Raw.+?Whois.+?Data.+?Domain((.|\n)*)For.+?more.+?information', raw
                )
                if html_strip:
                    parts = str(html_strip.group(1)).replace("\n", ",").split(",")
                    for item in parts:
                        if ":" in item:
                            key, _, val = item.partition(":")
                            whois_dict[key] = val
            whois_data["WhoIsComResult"] = whois_dict
        except Exception as e:
            logger.warning("whois.com lookup failed for %s: %s", self.domain, e)
            whois_data["WhoIsComResult"] = ""

        return whois_data

    def dns_info_fetch(self):
        """Query A records for the domain."""
        dns_data = []
        try:
            dns_info = dns.resolver.resolve(self.domain, 'A')
            for rdata in dns_info:
                dns_data.append(rdata.to_text())
        except Exception as e:
            logger.warning("DNS lookup failed for %s: %s", self.domain, e)
        return dns_data

    def server_fingerprint(self, domain):
        """Return the response headers dict for the domain, or None on failure.

        Tries HTTPS first; falls back to HTTP (with verify=False) for servers
        that have certificate errors — common on internal/test hosts encountered
        during recon.
        """
        headers = restApi.httpRequest(domain).get_request(None, "header")
        if headers is not None:
            return dict(headers)
        # SSL / cert error fallback: retry with TLS verification disabled so
        # we can still fingerprint servers with self-signed or expired certs.
        try:
            headers = restApi.httpRequest(domain).get_request(None, "header_noverify")
            if headers is not None:
                logger.warning("Server fingerprint for %s used verify=False (cert issue)", domain)
                return dict(headers)
        except Exception as e:
            logger.warning("Server fingerprint failed for %s: %s", domain, e)
        return None

    def geo_locate(self):
        """Geo-locate the domain's IP via ipapi.co. Returns JSON dict or None.

        Reads IPAPI_KEY from the environment for authenticated requests (removes
        the 1,000 req/day free-tier rate limit).
        """
        if not self.ip:
            return None
        try:
            api_key = os.environ.get("IPAPI_KEY")
            url = (
                IPAPI_KEY_URL.format(ip=self.ip, key=api_key)
                if api_key
                else IPAPI_URL.format(ip=self.ip)
            )
            result = restApi.httpRequest(url).get_request(None, "json")
            if isinstance(result, dict) and result.get("error"):
                reason = result.get("reason", "unknown")
                logger.warning("ipapi.co error for %s: %s", self.ip, reason)
                return None
            return result
        except Exception as e:
            logger.warning("Geolocation unavailable for %s: %s", self.ip, e)
            return None
