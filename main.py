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
import whoisInfoApi

def main():
# Argument Fetch from the User
    if len(sys.argv) != 2:
        print "Please enter only the URL for the List of URLs/Domains to Test!"
        sys.exit()
    urls_to_test = sys.argv[1]


# Make Web Request to Fetch the List of urls

# Get the Whois Data of all the domains

