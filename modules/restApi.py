#######################################################################################################
#
#
# 	 				                   REST API DRIVERS
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
import requests # Rest Api Library
import json

class httpRequest:
# Handle to make HTTP GET Request and return a JSON output
    def get_request(self, url, headers=None, type=None, auth=None):
        if not headers:
            headers = {'Content-Type':'text/html'}
        if str(type).lower() == "json":
            headers = {'Content-Type':'application/json', 'Accept':'application/json'}
            response = requests.get(url, headers=headers)
        else:
            response = requests.get(url, headers)
        if auth:
            response = requests.get(url, auth)
        try:
            return response.json()
        except ValueError as e:
            if str(e).lower().strip() == "no json object could be decoded":
                return response.text
            else:
                print "Get Request to the url "+str(url)+" failed!"

# Handle to make HTTP POST Request and return a JSON output
    def post_request(url, auth=None, body=None):
        response = requests.post(url, data=body, auth=auth)
        return response

# Handle to make HTTP Delete Requests
    def delete_request(url, auth=None):
        response = requests.delete(url, auth=auth)
        return response.json()

# Function Driver - To Test the restApi Module Functions
def main():
        testurl  = "http://isis.poly.edu/~marcbudofsky/cs6963-fall2016/URLs"
        testurl2 = "http://whois.arin.net/rest/poc/NYU-ARIN"
        testrequest = httpRequest()
        print testrequest.get_request(testurl2, None, "json")

main()



