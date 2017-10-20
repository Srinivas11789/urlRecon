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
import ipwhois

class whoisFetch:
    def __init__(self, domain):
        self.domain = self.domain_stripper(domain)
        self.ip = self.domain_ip_fetch()
        self.whois = self.whois_info_fetch()

    def domain_ip_fetch(self):
        try:
            return socket.gethostbyname(self.domain)
        except:
            print "Domain Resolving Error! Check the Connectivity!"

    def domain_stripper(self,domain):
        print domain
        if not re.match("^[a-zA-Z0-9._-]+\.[a-z]{3}",domain):
            extract_domain = re.search("^http:\/\/([a-zA-Z_.-]+)\/", domain)
            if extract_domain.group(1):
                domain_name = extract_domain.group(1)
                return domain_name
            else:
                print "Url provided is invalid! \n"
                return ""
        else:
            print "Url provided is invalid! \n"
            return ""

    def whois_info_fetch(self):
       try:
         whois_info = ipwhois.IPWhois(self.ip).lookup_rdap()
       except:
         whois_info = None
       return whois_info


# Driver Program for the module
def main():
    domain = "http://play.plaidctf.com/"
    domain_info = whoisFetch(domain)
    print domain_info.domain
    print domain_info.ip
    print domain_info.whois

main()
