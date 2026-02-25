"""End-to-end workflow tests — all network calls are mocked."""

import os
import sys
import json
import sqlite3
import tempfile
import unittest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from urlrecon.modules import domainInfoApi, reportGenerator

# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

FAKE_IP = "93.184.216.34"
FAKE_GEO = {
    "ip": FAKE_IP,
    "city": "Norwell",
    "region": "Massachusetts",
    "country": "US",
    "latitude": 42.1596,
    "longitude": -70.8217,
    "org": "AS15133 Edgecast Inc.",
}
FAKE_WHOIS = {"asn": "15133", "asn_description": "EDGECAST, US"}
FAKE_HEADERS = {"Server": "ECS (dcb/7F37)", "Content-Type": "text/html"}


def _mock_get_request(headers=None, type=None, auth=None):
    """Simulate get_request — used as side_effect, not a bound method."""
    if type == "json":
        return FAKE_GEO
    if type == "header":
        return FAKE_HEADERS
    return "<html>Raw Whois Data Domain\nRegistrar: GoDaddy\nFor more information</html>"


def _build_domain_info(url):
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


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestFullWorkflow(unittest.TestCase):
    """Smoke-test that reports are created and contain expected data."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.urls = [
            "https://www.example.com/",
            "https://www.wikipedia.org/",
        ]

    def _run_workflow(self, option=None):
        report = reportGenerator.reportGen(self.tmpdir, option)
        for url in self.urls:
            domain_info = _build_domain_info(url)
            report.push_data_to_report(domain_info)
        report.close_all()
        return os.path.join(self.tmpdir, "report")

    def test_all_reports_created(self):
        report_dir = self._run_workflow()
        self.assertTrue(os.path.exists(os.path.join(report_dir, "report.txt")))
        self.assertTrue(os.path.exists(os.path.join(report_dir, "urlInformation.db")))
        self.assertTrue(os.path.exists(os.path.join(report_dir, "urlLocation.kml")))

    def test_text_report_contains_urls(self):
        report_dir = self._run_workflow("text")
        with open(os.path.join(report_dir, "report.txt")) as f:
            content = f.read()
        for url in self.urls:
            self.assertIn(url, content)

    def test_database_contains_rows(self):
        report_dir = self._run_workflow("sql")
        conn = sqlite3.connect(os.path.join(report_dir, "urlInformation.db"))
        rows = conn.execute("SELECT URL FROM urlData").fetchall()
        conn.close()
        urls_in_db = [r[0] for r in rows]
        for url in self.urls:
            self.assertIn(url, urls_in_db)

    def test_database_schema(self):
        report_dir = self._run_workflow("sql")
        conn = sqlite3.connect(os.path.join(report_dir, "urlInformation.db"))
        cols = [desc[1] for desc in conn.execute("PRAGMA table_info(urlData)").fetchall()]
        conn.close()
        expected = ["URL", "Domain", "IP", "dnsIp", "whoIsInfo", "serverFingerprint", "geoLocation"]
        for col in expected:
            self.assertIn(col, cols)

    def test_kml_contains_points(self):
        report_dir = self._run_workflow("kml")
        with open(os.path.join(report_dir, "urlLocation.kml")) as f:
            kml_content = f.read()
        # KML placemark names come from the URL
        self.assertIn("www.example.com", kml_content)

    def test_no_crash_on_missing_geolocation(self):
        """update_kmlfile should skip silently when geolocation is None."""
        report = reportGenerator.reportGen(self.tmpdir, "kml")
        domain_info = _build_domain_info(self.urls[0])
        domain_info.geolocation = None  # simulate missing geo
        report.push_data_to_report(domain_info)  # must not raise
        report.close_all()

    def test_no_crash_on_incomplete_geolocation(self):
        """update_kmlfile should skip when latitude/longitude are absent."""
        report = reportGenerator.reportGen(self.tmpdir, "kml")
        domain_info = _build_domain_info(self.urls[0])
        domain_info.geolocation = {"city": "Unknown"}  # no lat/lon
        report.push_data_to_report(domain_info)  # must not raise
        report.close_all()


class TestInvalidUrlHandling(unittest.TestCase):
    """Verify that invalid or unreachable URLs don't crash the pipeline."""

    def test_bad_url_domain_is_empty_string(self):
        with patch("socket.gethostbyname", return_value=None), \
             patch("ipwhois.IPWhois", return_value=MagicMock()), \
             patch("dns.resolver.resolve", return_value=[]), \
             patch.object(domainInfoApi.restApi.httpRequest, "get_request", return_value=None):
            info = domainInfoApi.domainInfo("not-a-valid-url")
        self.assertEqual(info.domain, "")

    def test_dns_failure_sets_ip_none(self):
        with patch("socket.gethostbyname", side_effect=OSError("DNS failure")), \
             patch("ipwhois.IPWhois", return_value=MagicMock()), \
             patch("dns.resolver.resolve", return_value=[]), \
             patch.object(domainInfoApi.restApi.httpRequest, "get_request", return_value=None):
            info = domainInfoApi.domainInfo("https://nonexistent.example/")
        self.assertIsNone(info.ip)


if __name__ == "__main__":
    unittest.main()
