"""Tests for domainInfoApi — all network calls are mocked."""

import sys
import os
import json
import unittest
from unittest.mock import patch, MagicMock

# Allow running tests from the repo root with `pytest test/`
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from urlrecon.modules import domainInfoApi


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

FAKE_IP = "142.250.80.46"
FAKE_DOMAIN = "drive.google.com"
FAKE_URL = f"https://{FAKE_DOMAIN}"

FAKE_WHOIS = {
    "asn": "15169",
    "asn_description": "GOOGLE, US",
    "network": {"cidr": "142.250.0.0/15"},
}

FAKE_GEO = {
    "ip": FAKE_IP,
    "city": "Mountain View",
    "region": "California",
    "country": "US",
    "latitude": 37.3861,
    "longitude": -122.0839,
    "org": "AS15169 Google LLC",
}

FAKE_HEADERS = {
    "Server": "ESF",
    "Content-Type": "text/html; charset=UTF-8",
}


def _make_domain_info(url=FAKE_URL):
    """Build a domainInfo object with all external calls mocked."""
    mock_ipwhois = MagicMock()
    mock_ipwhois.lookup_rdap.return_value = FAKE_WHOIS

    mock_dns_answer = [MagicMock()]
    mock_dns_answer[0].to_text.return_value = FAKE_IP

    with patch("socket.gethostbyname", return_value=FAKE_IP), \
         patch("ipwhois.IPWhois", return_value=mock_ipwhois), \
         patch("dns.resolver.resolve", return_value=mock_dns_answer), \
         patch.object(
             domainInfoApi.restApi.httpRequest, "get_request",
             side_effect=_mock_get_request,
         ):
        return domainInfoApi.domainInfo(url)


def _mock_get_request(headers=None, type=None, auth=None):
    """Simulate get_request responses for different call patterns.

    Used as a ``side_effect`` on ``httpRequest.get_request`` — not bound to an
    instance, so there is no ``self`` parameter here.
    """
    if type == "json":
        return FAKE_GEO
    if type == "header":
        return FAKE_HEADERS
    # Plain text — whois.com scrape
    return "<html>Raw Whois Data Domain\nRegistrar: GoDaddy\nFor more information</html>"


# ---------------------------------------------------------------------------
# Test cases
# ---------------------------------------------------------------------------

class TestDomainStripper(unittest.TestCase):

    def test_strips_https_url(self):
        with patch("socket.gethostbyname", return_value=FAKE_IP), \
             patch("ipwhois.IPWhois", return_value=MagicMock()), \
             patch("dns.resolver.resolve", return_value=[]), \
             patch.object(domainInfoApi.restApi.httpRequest, "get_request", return_value=None):
            info = domainInfoApi.domainInfo("https://www.example.com/path")
        assert info.domain == "www.example.com"

    def test_strips_http_url(self):
        with patch("socket.gethostbyname", return_value="93.184.216.34"), \
             patch("ipwhois.IPWhois", return_value=MagicMock()), \
             patch("dns.resolver.resolve", return_value=[]), \
             patch.object(domainInfoApi.restApi.httpRequest, "get_request", return_value=None):
            info = domainInfoApi.domainInfo("http://www.example.com/")
        assert info.domain == "www.example.com"

    def test_plain_domain_accepted(self):
        """A plain hostname (no scheme) should be returned as-is."""
        with patch("socket.gethostbyname", return_value="93.184.216.34"), \
             patch("ipwhois.IPWhois", return_value=MagicMock()), \
             patch("dns.resolver.resolve", return_value=[]), \
             patch.object(domainInfoApi.restApi.httpRequest, "get_request", return_value=None):
            info = domainInfoApi.domainInfo("www.example.com")
        assert info.domain == "www.example.com"

    def test_long_tld_accepted(self):
        """TLDs longer than 3 chars (.info, .travel) must be accepted."""
        with patch("socket.gethostbyname", return_value="1.2.3.4"), \
             patch("ipwhois.IPWhois", return_value=MagicMock()), \
             patch("dns.resolver.resolve", return_value=[]), \
             patch.object(domainInfoApi.restApi.httpRequest, "get_request", return_value=None):
            info = domainInfoApi.domainInfo("http://example.museum/")
        assert info.domain == "example.museum"

    def test_invalid_url_returns_empty_string(self):
        with patch("socket.gethostbyname", return_value=None), \
             patch("ipwhois.IPWhois", return_value=MagicMock()), \
             patch("dns.resolver.resolve", return_value=[]), \
             patch.object(domainInfoApi.restApi.httpRequest, "get_request", return_value=None):
            info = domainInfoApi.domainInfo("not-a-valid-url")
        assert info.domain == ""


class TestDomainIpFetch(unittest.TestCase):

    def test_returns_ip(self):
        info = _make_domain_info()
        assert info.ip == FAKE_IP

    def test_dns_failure_returns_none(self):
        with patch("socket.gethostbyname", side_effect=OSError("DNS error")), \
             patch("ipwhois.IPWhois", return_value=MagicMock()), \
             patch("dns.resolver.resolve", return_value=[]), \
             patch.object(domainInfoApi.restApi.httpRequest, "get_request", return_value=None):
            info = domainInfoApi.domainInfo(FAKE_URL)
        assert info.ip is None


class TestDomainInfo(unittest.TestCase):

    def setUp(self):
        self.info = _make_domain_info()

    def test_domain_parsed(self):
        assert self.info.domain == FAKE_DOMAIN

    def test_ip_resolved(self):
        import re
        ip_pattern = r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$"
        assert re.match(ip_pattern, self.info.ip)

    def test_whois_asn_description(self):
        assert self.info.whois["IpWhoIsResult"]["asn_description"] == "GOOGLE, US"

    def test_dns_records_populated(self):
        import re
        ip_pattern = r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$"
        assert len(self.info.dns) > 0
        assert re.match(ip_pattern, self.info.dns[0])

    def test_geolocation_present(self):
        assert self.info.geolocation is not None
        assert self.info.geolocation["city"] == "Mountain View"
        assert "latitude" in self.info.geolocation
        assert "longitude" in self.info.geolocation

    def test_server_fingerprint_present(self):
        assert self.info.server_fingerprint is not None


class TestGeoLocateMissing(unittest.TestCase):
    """geo_locate should return None gracefully when the API is unavailable."""

    def test_returns_none_on_api_failure(self):
        mock_ipwhois = MagicMock()
        mock_ipwhois.lookup_rdap.return_value = {}

        with patch("socket.gethostbyname", return_value=FAKE_IP), \
             patch("ipwhois.IPWhois", return_value=mock_ipwhois), \
             patch("dns.resolver.resolve", return_value=[]), \
             patch.object(domainInfoApi.restApi.httpRequest, "get_request", return_value=None):
            info = domainInfoApi.domainInfo(FAKE_URL)

        assert info.geolocation is None


class TestWhoisFailure(unittest.TestCase):
    """WHOIS lookups that raise should not crash the object construction."""

    def test_ipwhois_failure_stored_as_empty_string(self):
        mock_ipwhois = MagicMock()
        mock_ipwhois.lookup_rdap.side_effect = Exception("timeout")

        with patch("socket.gethostbyname", return_value=FAKE_IP), \
             patch("ipwhois.IPWhois", return_value=mock_ipwhois), \
             patch("dns.resolver.resolve", return_value=[]), \
             patch.object(domainInfoApi.restApi.httpRequest, "get_request", return_value=None):
            info = domainInfoApi.domainInfo(FAKE_URL)

        assert info.whois["IpWhoIsResult"] == ""


if __name__ == "__main__":
    unittest.main()
