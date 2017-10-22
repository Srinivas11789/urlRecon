#######################################################################################################
#
#
# 	 				                        REPORT GENERATOR HANDLE
#
# 				      AUTHOR: SRINIVAS PISKALA GANESH BABU
#
#				      DESCRIPTION:
#                           The HTTP Rest Api Calls to Fetch data from a server \
#                              and return them in valid formats like Json and HTML-Data
#
#			          FUNCTIONS:
#                           * getRequest
#                           * postRequest
#                           * deleteRequest
#                           *
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

# Report Gen Class holding all the report generator functions
class reportGen():
    def __init__(self, domainInfoApiObject, option, path):
        self.domainInfoObject = domainInfoApiObject
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
            self.kmlfile = self.createkmlfile()

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

    def update_report(self):
        self.report.write("=="*50)
        self.report.write("\n"*3)
        self.report.write("URL: %s",self.domainInfoObjecturl)
        self.report.write("\n"*3)
        self.report.write("Domain: %s",self.domainInfoObject.domain)
        self.report.write("\n"*3)
        self.report.write("DNS: %s",self.domainInfoObject.dns)
        self.report.write("\n"*3)
        self.report.write("whoIs Data: %s",self.domainInfoObject.whois)
        self.report.write("\n"*3)
        self.report.write("Server Fingerprint: %s",self.domainInfoObject.server_fingerprint)
        self.report.write("\n"*3)
        self.report.write("Geo Location: %s",self.domainInfoObject.geolocation)
        self.report.write("\n"*3)

    def update_database(self):
        try:
            self.database.execute("""CREATE TABLE urlData (Domain text, whoIsInfo text, dnsIp text, serverFingerprint text, geoLocation text)""")
        except:
            pass
        self.database.execute("INSERT INTO urlData VALUES (?, ?, ?, ?, ?, ?)",(self.domainInfoObject.url, self.domainInfoObject.domain, self.domainInfoObject.ip, self.domainInfoObject.dns, self.domainInfoObject.whois, self.domainInfoObject.server_fingerprint, self.domainInfoObject.geolocation))

    def update_kmlfile(self):
            self.kmlfile.newpoint(name=self.domainInfoObject.url, coords=[(self.domainInfoObject.geolocation['latitude'], self.domainInfoObject.geolocation['longitude'])])

    def close_all(self):
        if self.report:
            self.report.close()
        if self.database:
            self.database.close()
        if self.kmlfile:
            self.kmlfile.save(self.directory + "/"+ 'urlLocation.kml')


