#######################################################################################################
#
#
# 	 				                        REPORT GENERATOR HANDLE
#
# 				      AUTHOR: SRINIVAS PISKALA GANESH BABU
#
#				      DESCRIPTION:
#
#
#			          FUNCTIONS:
#                           * getRequest
#
#
#########################################################################################################

# Module

# Custom or Third Party Module Imports
# Kml File Gen
import simplekml

# OS
import os # -- default Lib

# SQL Lite Database
import sqlite3

# JSON
import json

# Report Gen Class holding all the report generator functions
class reportGen():
    def __init__(self, path, option=None ):
        # Report Folder Creation (Future Get the Report as Argument)
        self.directory = path+"/report"
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)
        if option == "kml":
            self.kmlfile = self.createkmlfile()
        elif option == "text":
            self.report = self.create_report()
        elif option == "sql":
            self.database = self.create_database()
        else:
            self.report = self.create_report()
            self.database = self.create_database()
            self.kmlfile = self.create_kmlfile()

    def push_data_to_report(self, domainInfoApiObject):
        if self.report:
            self.update_report(domainInfoApiObject)
        if self.database:
            self.update_database(domainInfoApiObject)
        if self.kmlfile:
            self.update_kmlfile(domainInfoApiObject)

# Creation of Output folders
# Report Text Creation and Handle return
    def create_report(self):
        try:
          text_handle = open(self.directory+"/report.txt","w")
          return text_handle
        except Exception as e:
            print "Could not create the report text file !!!!! Please debug error %s" % (str(e.message))

    def create_database(self):
        try:
         sql_handle = sqlite3.connect(self.directory + r"/" + r"urlInformation.db")
         cur = sql_handle.cursor()
         return cur
        except Exception as e:
            print "Could not create the report database !!!!! Please debug error %s" % (str(e.message))

    def create_kmlfile(self):
        try:
            kml_handle = simplekml.Kml()
            return kml_handle
        except Exception as e:
            print "Could not create the kml file !!!!! Please debug error %s" % (str(e.message))

    def update_report(self, domainInfoObject):
        self.report.write("=="*70)
        self.report.write("\n"*3)
        self.report.write("URL: %s" %domainInfoObject.url)
        self.report.write("\n"*3)
        self.report.write("Domain: %s" % domainInfoObject.domain)
        self.report.write("\n"*3)
        self.report.write("DNS: %s" % domainInfoObject.dns)
        self.report.write("\n"*3)
        self.report.write("whoIs Data: %s" % json.dumps(domainInfoObject.whois, indent = 2, sort_keys = True)) # domainInfoObject.whois
        self.report.write("\n"*3)
        self.report.write("Server Fingerprint: %s" % domainInfoObject.server_fingerprint)
        self.report.write("\n"*3)
        self.report.write("Geo Location: %s" % json.dumps(domainInfoObject.geolocation, indent = 2, sort_keys = True))
        self.report.write("\n"*3)

    def update_database(self, domainInfoObject):
        try:
            self.database.execute("""CREATE TABLE urlData (URL text, Domain text, IP text, dnsIp text, whoIsInfo text, serverFingerprint text, geoLocation text)""")
        except:
            pass
        self.database.execute("INSERT INTO urlData VALUES (?, ?, ?, ?, ?, ?, ?)",(str(domainInfoObject.url), str(domainInfoObject.domain), str(domainInfoObject.ip), str(domainInfoObject.dns), str(domainInfoObject.whois), str(domainInfoObject.server_fingerprint), str(domainInfoObject.geolocation)))

    def update_kmlfile(self, domainInfoObject):
            self.kmlfile.newpoint(name=domainInfoObject.url, coords=[(domainInfoObject.geolocation['latitude'], domainInfoObject.geolocation['longitude'])])

    def close_all(self):
        if self.report:
            self.report.close()
        if self.database:
            self.database.close()
        if self.kmlfile:
            self.kmlfile.save(self.directory + "/"+ 'urlLocation.kml')


