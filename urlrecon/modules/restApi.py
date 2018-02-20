########################################################################################################
#                                                                                                      #
#                                                                                                      #
# 	 				                   REST API DRIVERS                                                #
#                                                                                                      #
# 				      AUTHOR: SRINIVAS PISKALA GANESH BABU                                             #
#                                                                                                      #
#				      DESCRIPTION: (BASE MODULE)                                                       #
#                           The HTTP Rest Api Calls to Fetch data from a server \                      #
#                                       and return them in valid formats like Json and HTML-Data       #
#                                                                                                      #
#			          FUNCTIONS:                                                                       #
#                           * getRequest    - Used extensively in the project                          #
#                           * postRequest   - Provisions for a POST request                            #
#                           * deleteRequest - Provisions for a DELETE request                          #
#                                                                                                      #
########################################################################################################

# Import Statements for Libraries
import requests # HTTP/HTTP Request Handles -- Default Lib
import json     # Handling JSON output      -- Default Lib


# httpRequest Class
#               - Definition - Holds the restApi calls like get, post and delete
#                            - Exposes API to make HTTP/HTTPS requests
#
class httpRequest:
    # Initialize Function
    #               - Input    : Url of the domain
    #               - Function : Class variable definitions
    #               - Output   : Fills the Object with the variable
    #
    def __init__(self, url):
        self.url = url

# Handle to make HTTP GET Request and return a JSON output
    # get_request Function
    #               - Input    : Url, Headers, Type (Output = "JSON", "Header"), Authentication
    #               - Function : Performs a HTTP/HTTPS Get Request with the Server
    #                            - HTTP  - Normal HTTP GET Request
    #                            - HTTPS - Ordinary Call
    #                                     - If Fails due to SSL Error, HTTP Call with 301 Redirect Header is taken into account
    #               - Output   : Returns the response based on the type - Json, Text or Header Output
    #
    def get_request(self, headers=None, type=None, auth=None):
        # Setting Default Headers - To anonymize the Request
        if not headers:
            headers = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:32.0) Gecko/20100101 Firefox/32.0',}
        # Output Type JSON Loop
        if str(type).lower() == "json":
            # Header Set to JSON Type
            headers = {'Content-Type':'application/json', 'Accept':'application/json'}
            try:
              response = requests.get(self.url, headers=headers)
              try:
               return response.json()
              except ValueError as e:
                  # JSON Decoding Error
                  if str(e).lower().strip() == "no json object could be decoded":
                      self.get_response = response.text
                      return self.get_response
                  else:
                      print "Get Request to the url " + str(self.url) + " failed!"
            except:
              print "Get Request to the url " + str(self.url) + " failed!"
        # Server Fingerprint Call - Only the header retireval
        elif str(type) == "header":
            try:
                response = requests.get(self.url, headers=headers)
                return response.headers
            except Exception as e:
                # SSL Error Handling - When SSL Error Occurs - Try HTTP call and capture the Redirect packet
                try:
                 if "ssl" in str(e.message).lower():
                    http_url = self.url
                    http_url = http_url.replace("https", "http")
                    response = requests.get(http_url, headers=headers, allow_redirects=False)
                    return response.headers
                 else:
                    response = requests.get(self.url, headers=headers, allow_redirects=False)
                    return response.headers
                except:
                    return None
            else:
              print "Get Request to the url " + str(self.url) + " failed!"
        # Default Call - HTML Text
        else:
            try:
              response = requests.get(self.url, headers)
              return response.text
            except:
              print "Get Request to the url " + str(self.url) + " failed!"
        # Call with Authentication
        if auth:
            try:
             response = requests.get(self.url, auth)
             return response.text
            except:
              print "Get Request to the url " + str(self.url) + " failed!"

# Handle to make HTTP POST Request and return a JSON output
    # POST Function - Unused Function - Just a Provision
    #               - Input    : Url, Authentication and Body
    #               - Function : Performs HTTP Post Request
    #               - Output   : Returns the response
    #
    def post_request(self, auth=None, body=None):
        response = requests.post(self.url, data=body, auth=auth)
        self.post_response = response.text
        return self.post_response

# Handle to make HTTP Delete Requests
    # DELETE Function
    #               - Input    : Url of the domain, Authentication
    #               - Function : Performs a HTTP Delete Request
    #               - Output   : Returns the Output
    #
    def delete_request(self, auth=None):
        response = requests.delete(self.url, auth=auth)
        self.delete_response = response.text
        return self.delete_response

# Function Driver - To Test the restApi Module Functions
# Test Driver Program for the module
#     # Function Definition and Call commented to supress during project execution
#     # Used for standalone module test
#                   - Input    : Nothing - Url hardcoded
#                   - Function : HTTP HTTPS Functions for GET POST DELETE
#                   - Output   : Returns Output in Text/Html, JSON and Headers alone as well
#
def main():
        testurl  = "http://isis.poly.edu/~marcbudofsky/cs6963-fall2016/URLs"
        testurl2 = "http://whois.arin.net/rest/poc/NYU-ARIN"
        testrequest = httpRequest(testurl2)
        print testrequest.get_request(None, "json")

#main()

