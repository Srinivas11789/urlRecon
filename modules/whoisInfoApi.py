#######################################################################################################
#
#
# 	 				                   WHO IS Information Fetch handle
#
# 				              AUTHOR: SRINIVAS PISKALA GANESH BABU
#
#				      DESCRIPTION:
#                           The HTTP Rest Api Calls to Fetch data from a server \
#                                       and return them in valid formats like Json and HTML-Data
#
#			          FUNCTIONS:
#                           * getRequest
#                           * postRequest
#                           * deleteRequest
#
#########################################################################################################
# Import Statements for Libraries
import json
import socket
import re

class whoisFetch:
    def __init__(self, domain):
        self.domain = domain
        self.ip = self.domain_ip_fetch()
        self.whois = None

    def domain_ip_fetch(self):
        try:
            return socket.gethostbyname(self.domain)
        except:
            print "Domain Resolving Error! Check the Connectivity!"

    def domain_stripper(self):
        if not re.match("^[a-zA-Z0-9.-_]+\.[a-z]{3}",self.domain):
            extract_domain = re.find("^http:\/\/([a-zA-Z_.-]+)\/", self.domain)
            if extract_domain.group(1):
                self.domain = extract_domain.group(1)

   def who_is_url_constructor(self):
       



# Driver Program for the module
def main():
    domain = "http://play.plaidctf.com/"
    domain_info = whoisFetch(domain)
    print domain_info.domain
    print domain_info.ip

main()
