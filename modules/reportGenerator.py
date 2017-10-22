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
import domainInfoApi

# Custom or Third Party Module Imports
import simplekml

# Report Gen Class holding all the report generator functions
class reportGen():
    def __init__(self, domainInfoApiObject):
        self.domainInfoObject = domainInfoApiObject
        self.report = self.create_report()
        self.database = self.create_database()
        self.kmlfile = self.createkmlfile()



# Creation of Output folders
# Report Text Creation and Handle return
    def create_report(self):

    def create_database(self):

    def create_kmlfile(self):

    def update_report(self):

    def update_database(self):

    def update_kmlfile(self):

    def close_all(self):



