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
# Module Imports
import restApi
# Import Statements for Libraries
# JSON -- default lib
import json
# SOCKET -- default lib
import socket
# Regular Expression -- default lib
import re
# Custom Library Import
# Whois
import ipwhois
# dns
import dns


class domainInfo:
    def __init__(self, domain):
        self.domain = self.domain_stripper(domain)
        self.ip = self.domain_ip_fetch()
        self.whois = self.whois_info_fetch()
        self.dns = self.dns_info_fetch()
        self.server_fingerprint = self.server_fingerprint(domain)
        self.geolocation = self.geo_locate()

    def domain_ip_fetch(self):
        try:
            return socket.gethostbyname(self.domain)
        except:
            print "Domain Resolving Error! Check the Connectivity!"

    def domain_stripper(self,domain):
        if not re.match("^[a-zA-Z0-9._-]+\.[a-z]{3}",domain):
            extract_domain = re.search("^htt[a-z]+:\/\/([a-zA-Z0-9_.-]+)[/]?", domain)
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

    def dns_info_fetch(self):
        dns_data = []
        try:
            dns_info = dns.resolver.query(self.domain, 'A') # dns.rdatatype.ANY
            for rdata in dns_info:
                dns_data.append(rdata.to_text())
        except:
            pass
        return dns_data

    def server_fingerprint(self, domain):
        # Make a Get Request and Receive the headers
        server_get_query = restApi.httpRequest(domain).get_request(None, "header")
        return server_get_query['server']

    def geo_locate(self):
        geolocate_api_service_1 = "http://www.freegeoip.net/json/" + self.ip
        location = restApi.httpRequest(geolocate_api_service_1).get_request(None, "json")
        return location



# Driver Program for the module
def main():
    #domain = "http://play.plaidctf.com/"
    domain = "http://nuitduhack.com/"
    domain_info = domainInfo(domain)
    print domain_info.domain
    print domain_info.ip
    print domain_info.whois
    print domain_info.dns
    print domain_info.server_fingerprint
    print domain_info.geolocation

main()
