#######################################################################################################
#                                                                                                     #
#                                                                                                     #
#                            REPORT GENERATOR HANDLE                                                  #
#                                                                                                     #
#               AUTHOR: SRINIVAS PISKALA GANESH BABU                                                  #
#                                                                                                     #
#               DESCRIPTION:                                                                          #
#                   Report Generation class that takes DomainInfoObject as input and                  #
#                   populates reports in three formats: text, KML, and SQLite database.               #
#                                                                                                     #
#               FUNCTIONS:                                                                            #
#                   * __init__            - Create all reports based on options                       #
#                   * push_data_to_report - Update reports with URL information                       #
#                   * create_report       - Create text report file                                   #
#                   * create_database     - Create SQLite database (with table schema)                #
#                   * create_kmlfile      - Create KML file handle                                    #
#                   * update_report       - Write URL info to text report                             #
#                   * update_database     - Insert URL info row into database                         #
#                   * update_kmlfile      - Add geolocation point to KML                             #
#                   * close_all           - Flush and close all open handles                          #
#                                                                                                     #
#######################################################################################################

import json
import logging
import os
import sqlite3

import simplekml

logger = logging.getLogger(__name__)


class reportGen:
    """Generate and update URL recon reports in text, SQLite, and KML formats."""

    def __init__(self, path, option=None):
        self.report = None
        self.database = None
        self.cursor = None
        self.kmlfile = None

        self.directory = path + "/report"
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)

        if option == "kml":
            self.kmlfile = self.create_kmlfile()
        elif option == "text":
            self.report = self.create_report()
        elif option == "sql":
            self.database = self.create_database()
            self.cursor = self.database.cursor()
        else:
            # Default: all three formats
            self.report = self.create_report()
            self.database = self.create_database()
            self.kmlfile = self.create_kmlfile()
            self.cursor = self.database.cursor()

    def push_data_to_report(self, domainInfoApiObject):
        """Write all available report formats with data from a domainInfo object."""
        if self.report:
            self.update_report(domainInfoApiObject)
        if self.database:
            self.update_database(domainInfoApiObject)
        if self.kmlfile:
            self.update_kmlfile(domainInfoApiObject)

    # --- Creation helpers ---

    def create_report(self):
        try:
            return open(self.directory + "/report.txt", "w")
        except Exception as e:
            logger.error("Could not create text report: %s", e)
            return None

    def create_database(self):
        """Open the SQLite database and ensure the table schema exists."""
        try:
            conn = sqlite3.connect(self.directory + "/urlInformation.db")
            conn.execute(
                """CREATE TABLE IF NOT EXISTS urlData (
                    URL text,
                    Domain text,
                    IP text,
                    dnsIp text,
                    whoIsInfo text,
                    serverFingerprint text,
                    geoLocation text
                )"""
            )
            conn.commit()
            return conn
        except Exception as e:
            logger.error("Could not create database: %s", e)
            return None

    def create_kmlfile(self):
        try:
            return simplekml.Kml()
        except Exception as e:
            logger.error("Could not create KML handle: %s", e)
            return None

    # --- Update helpers ---

    def update_report(self, domainInfoObject):
        self.report.write("==" * 70 + "\n\n\n")
        self.report.write(f"URL: {domainInfoObject.url}\n\n\n")
        self.report.write(f"Domain: {domainInfoObject.domain}\n\n\n")
        self.report.write(f"DNS: {domainInfoObject.dns}\n\n\n")
        self.report.write(
            "whoIs Data: {}\n\n\n".format(
                json.dumps(domainInfoObject.whois, indent=2, sort_keys=True)
            )
        )
        self.report.write(f"Server Fingerprint: {domainInfoObject.server_fingerprint}\n\n\n")
        self.report.write(
            "Geo Location: {}\n\n\n".format(
                json.dumps(domainInfoObject.geolocation, indent=2, sort_keys=True)
            )
        )

    def update_database(self, domainInfoObject):
        self.cursor.execute(
            "INSERT INTO urlData VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                str(domainInfoObject.url),
                str(domainInfoObject.domain),
                str(domainInfoObject.ip),
                str(domainInfoObject.dns),
                str(domainInfoObject.whois),
                str(domainInfoObject.server_fingerprint),
                str(domainInfoObject.geolocation),
            ),
        )

    def update_kmlfile(self, domainInfoObject):
        """Add a placemark for the domain if geolocation data is available."""
        geo = domainInfoObject.geolocation
        if not geo:
            logger.warning("No geolocation data for %s — skipping KML point", domainInfoObject.url)
            return
        lat = geo.get('latitude')
        lon = geo.get('longitude')
        if lat is None or lon is None:
            logger.warning(
                "Incomplete geolocation for %s (lat=%s, lon=%s) — skipping KML point",
                domainInfoObject.url, lat, lon,
            )
            return
        self.kmlfile.newpoint(name=domainInfoObject.url, coords=[(lon, lat)])

    # --- Close ---

    def close_all(self):
        if self.report:
            self.report.close()
        if self.database:
            self.database.commit()
            self.database.close()
        if self.kmlfile:
            self.kmlfile.save(self.directory + "/urlLocation.kml")
