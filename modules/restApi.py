######################################################################################
#
#
# 	 				                   REST API DRIVERS
#
# 				              AUTHOR: SRINIVAS PISKALA GANESH BABU
#
#				      DESCRIPTION:
#
#
#
#			          FUNCTIONS:
#                           * getRequest
#                           * postRequest
#######################################################################################
# Import Statements for Libraries
import requests # Rest Api Library
import json

# Handle to make HTTP GET Request and return a JSON output
def getRequest(url, headers=None, type=None, auth=None):
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
def postRequest(url, auth=None, body=None):
    response = requests.post(url, data=body)
    return response.json()

# Handle to make HTTP Delete Requests
def deleteRequest(url, auth=None):
    response = requests.delete(url)
    return response.json()

def main():
    testurl  = "http://isis.poly.edu/~marcbudofsky/cs6963-fall2016/URLs"
    testurl2 = "http://whois.arin.net/rest/poc/NYU-ARIN"
    print getRequest(testurl)
    print getRequest(testurl2, None, "json")

main()


