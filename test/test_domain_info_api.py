import re,sys,json

if sys.path[0]:
   sys.path.insert(0,sys.path[0]+"/../urlrecon/modules/")
else:
   sys.path.insert(0,"/../urlrecon/modules/")

#print sys.path[0]

import domainInfoApi

def test_domain_info():
    domain = "https://drive.google.com"
    domain_info = domainInfoApi.domainInfo(domain)
    assert(re.match("([0-9]{3}|[0-9]{2}|[0-9]{1})\.([0-9]{3}|[0-9]{2}|[0-9]{1})\.([0-9]{3}|[0-9]{2}|[0-9]{1})\.([0-9]{3}|[0-9]{2}|[0-9]{1})",domain_info.ip))
    assert "drive.google.com" == domain_info.domain
    assert domain_info.whois["IpWhoIsResult"]["asn_description"] == "GOOGLE - Google LLC, US"
    assert (re.match("([0-9]{3}|[0-9]{2}|[0-9]{1})\.([0-9]{3}|[0-9]{2}|[0-9]{1})\.([0-9]{3}|[0-9]{2}|[0-9]{1})\.([0-9]{3}|[0-9]{2}|[0-9]{1})",domain_info.dns[0]))
    #print json.loads(domain_info.server_fingerprint)
    #assert domain_info.server_fingerprint['Content-Type'] == 'text/html'
    #assert domain_info.geolocation['city'] == 'Mountain View'

#test_domainInfo()


