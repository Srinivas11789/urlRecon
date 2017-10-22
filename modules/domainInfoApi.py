#######################################################################################################
#
#
# 	 				               WHO IS Information Fetch handle
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
        self.url = domain
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
       whois_data = {}
       try:
         whois_info = ipwhois.IPWhois(self.ip).lookup_rdap()
         whois_data["IpWhoIsResult"] = whois_info
       except:
           whois_data["IpWhoIsResult"] = ""
       try:
           whois_dict = {}
           whois_info = restApi.httpRequest("https://www.whois.com/whois/"+self.domain).get_request()
           html_strip = re.search('Raw.+?Whois.+?Data.+?Domain((.|\n)*)For.+?more.+?information', whois_info)
           html_strip = str(html_strip.group(1)).replace("\n",",")
           html_strip = html_strip.split(",")
           for item in html_strip:
               if ":" in item:
                items = item.split(":")
                whois_dict[items[0]] = items[1]
           whois_data["WhoIsComResult"] = whois_dict
       except:
           whois_data["WhoIsComResult"] = ""

       return whois_data

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
        try:
         return server_get_query['server']
        except:
          try:
              server_delete_query = restApi.httpRequest(domain).delete_request(None, "header")
              return server_delete_query['server']
          except:
              return None

    def geo_locate(self):
        location = None
        try:
         if self.ip:
           # Location Errors in Free GEO IP - "http://www.freegeoip.net/json/" migrated to geoipfree
           geolocate_api_service_1 = "http://www.geoipfree.com/json/" + self.domain
           location = restApi.httpRequest(geolocate_api_service_1).get_request(None, "json")
        except:
            print "Location information not available !!!"
        return location



# Driver Program for the module
def main():
    #domain = "http://play.plaidctf.com/"
    domain = "http://nuitduhack.com/"
    domain = "https://www.derbycon.com"
    domain = "https://www.defcon.org/"
    domain = "https://www.facebook.com/"
   # domain = "https://drive.google.com"
    domain_info = domainInfo(domain)
    print domain_info.domain
    print domain_info.ip
    print json.dumps(domain_info.whois, indent = 4, sort_keys = True)
    print domain_info.dns
    print domain_info.server_fingerprint
    print domain_info.geolocation

#main()
