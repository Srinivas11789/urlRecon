########################################################################################################################
#                                                                                                                      #
#                                                                                                                      #
#                                 Main Module - Program that drives the Application                                    #
#                                                                                                                      #
#                             AUTHOR: Srinivas Piskala Ganesh Babu                                                     #
#                                                                                                                      #
#                                                                                                                      #
########################################################################################################################
# Import Libraries
import os
import sys
# Import Custom Modules
sys.path.insert(0, 'modules/')
import restApi
import domainInfoApi
import reportGenerator

def main():
# Argument Fetch from the User
    if len(sys.argv) != 2:
        print "Please enter only the URL for the List of URLs/Domains to Test!"
        sys.exit()
    urls_file = sys.argv[1]

# Make Web Request to Fetch the List of urls
    urls_to_test = restApi.httpRequest(urls_file).get_request()
    urls_to_test = urls_to_test.split('\n')

# Report Initiation

    report = reportGenerator.reportGen(os.path.basename(os.path.dirname(os.path.realpath(__file__))))

# Get the Whois Data of all the domains
    for url in urls_to_test:
        print url
        domain_info = domainInfoApi.domainInfo(url)
        report.push_data_to_report(domain_info)

# Close Call
    report.close_all()

if __name__ == "__main__":
    main()


    """ DEBUG OUTPUT
        print whois_info.whois
        print "\n\n"
        print whois_info.domain
        print whois_info.ip
        print whois_info.whois
        print whois_info.dns
        print whois_info.server_fingerprint
        print whois_info.geolocation
        """