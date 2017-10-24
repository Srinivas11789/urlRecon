############################################################################################################
#                                                                                                          #
#                                                                                                          #
# 	 				               Domain Information Fetch Module                                         #
#                                                                                                          #
# 				      AUTHOR: SRINIVAS PISKALA GANESH BABU                                                 #
#                                                                                                          #
#				      DESCRIPTION:                                                                         #
#                           Creates an Class Object for the URL Input, Fetches the                         #
#                            * Domain Name                                                                 #
#                            * IP address                                                                  #
#                            * DNS IP Information - A Record [Ipv4]                                        #
#                            * Server Fingerprint                                                          #
#                            * Geo Location of the Server                                                  #
#                           Fills the Object and returns                                                   #
#                                                                                                          #
#			          FUNCTIONS:                                                                           #
#                           * init - To fill the object with information                                   #
#                           * domain_ip_fetch - To obtain the IP of the domain                             #
#                           * domain_stripper - To strip the domain from the URL                           #
#                           * whois_info_fetch - Fetch whois information from Domain as well as IP         #
#                           * dns_info_fetch - Fetch the DNS IP record                                     #
#                           * server_fingerprint - To obtain the server fingerprint from the header        #
#                           * geo_locate - to locate the IP from a well known API                          #
#                                                                                                          #
############################################################################################################

# Module Imports
# RestApi module written and existing in the same folder
import restApi

# Import Statements for Libraries
# JSON -- default lib
import json
# SOCKET -- default lib
import socket
# Regular Expression -- default lib
import re
# Custom Library Import
# Warnings - to suppress UserWarnings in the output
import warnings
warnings.filterwarnings("ignore", category=UserWarning)
# Whois - Obtain the whois information from the IP
import ipwhois
# dns - To obtain the dns info - by default installed by ipwhois
import dns


# domainInfo
# Module Class Definition - "domainInfo" = Given a url, Returns an object with all domain information
#
class domainInfo:
    # Initialize Function
    #               - Input    : Url of the domain
    #               - Function : Class variable definitions and function calls
    #               - Output   : Fills all the class parameters
    #
    def __init__(self, domain):
        self.url = domain
        self.domain = self.domain_stripper(domain)
        self.ip = self.domain_ip_fetch()
        self.whois = self.whois_info_fetch()
        self.dns = self.dns_info_fetch()
        self.server_fingerprint = self.server_fingerprint(domain)
        self.geolocation = self.geo_locate()

    # domain_ip_fetch
    #               - Input     : Domain Name
    #               - Function  : Fetch Ip of the domain through sockets resolve
    #               - Output    : returns the Ip address
    def domain_ip_fetch(self):
        try:
            return socket.gethostbyname(self.domain)
        except:
            print "Domain Resolving Error! Check the Connectivity!"

    # domain_stripper
    #                - Input     : Url
    #                - Function  : strips the domain from the url given as input using regex
    #                - Output    : Returns the Domain Name
    def domain_stripper(self,domain):
        # Regex to
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

    # whois_info_fetch
    #                  - Input    : Domain Name and IP address
    #                  - Function : Obtains the Whois Information for the given domain or IP
    #                               * Domain
    #                                 * Leverages restApi with "whois.com/whois" api call
    #                               * IP
    #                                 * Leverages the ipWhois python library to fetch info
    #                  - Output   : Returns the whois data obtained from whois.com and ipwhois
    #
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

    # dns_info_fetch
    #               - Input    : domain_name
    #               - Function : Obtains the DNS information of IP address of the target domain
    #                            Leverages the "dns" python library to fetch the dns ip address
    #               - Output   : returns the DNS IP information
    #
    def dns_info_fetch(self):
        dns_data = []
        try:
            dns_info = dns.resolver.query(self.domain, 'A') # dns.rdatatype.ANY
            for rdata in dns_info:
                dns_data.append(rdata.to_text())
        except:
            pass
        return dns_data

    # server_fingerprint
    #             - Input    : url
    #             - Function : HTTP - Obtains the server info from the response header
    #                          HTTPS - Obtains the server info from the redirect as the SSL connect fails
    #             - Output   : Server Key from the Header
    #
    def server_fingerprint(self, domain):
        # Make a Get Request and Receive the headers
        server_get_query = restApi.httpRequest(domain).get_request(None, "header")
        try:
         return str(server_get_query)
        except:
          try:
              server_delete_query = restApi.httpRequest(domain).delete_request(None, "header")
              return str(server_delete_query)
          except:
              return None

    # geo_locate
    #           - Input   : domain name of the server/url
    #           - Function: Geo locates the Domain from the "freegeoip" or "geoipfree" domains
    #           - Returns : JSON of all the location information
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



# Test Driver Program for the module
#     # Function Definition and Call commented to supress during project execution
#     # Used for standalone module test
#                   - Input    : Nothing
#                   - Function : Creates class object adn Retrieves all the object information
#                   - Output   : Prints the domain information to the standard out
#
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
