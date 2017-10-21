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
    def __init__(self, url):
        self.url = url
# Handle to make HTTP GET Request and return a JSON output
    def get_request(self, headers=None, type=None, auth=None):
        if not headers:
            headers = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:32.0) Gecko/20100101 Firefox/32.0',}
        if str(type).lower() == "json":
            headers = {'Content-Type':'application/json', 'Accept':'application/json'}
            try:
              response = requests.get(self.url, headers=headers)
              try:
               return response.json()
              except ValueError as e:
                  if str(e).lower().strip() == "no json object could be decoded":
                      self.get_response = response.text
                      return self.get_response
                  else:
                      print "Get Request to the url " + str(self.url) + " failed!"
            except:
              print "Get Request to the url " + str(self.url) + " failed!"
        # Fingerprint Call - Only the header retireval
        elif str(type) == "header":
            try:
                response = requests.get(self.url, headers=headers)
                return response.headers
            except Exception as e:
                try:
                 if "ssl" in str(e.message).lower():
                    http_url = self.url
                    http_url = http_url.replace("https", "http")
                    print http_url
                    response = requests.get(http_url, headers=headers, allow_redirects=False)
                    print response
                    print response.headers
                    return response.headers
                 else:
                    response = requests.get(self.url, headers=headers, allow_redirects=False)
                    return response.headers
                except:
                    return None
            else:
              print "Get Request to the url " + str(self.url) + " failed!"
        else:
            try:
              response = requests.get(self.url, headers)
              return response.text
            except:
              print "Get Request to the url " + str(self.url) + " failed!"
        if auth:
            try:
             response = requests.get(self.url, auth)
             return response.text
            except:
              print "Get Request to the url " + str(self.url) + " failed!"

# Handle to make HTTP POST Request and return a JSON output
    def post_request(self, auth=None, body=None):
        response = requests.post(self.url, data=body, auth=auth)
        self.post_response = response.text
        return self.post_response

# Handle to make HTTP Delete Requests
    def delete_request(self, auth=None):
        response = requests.delete(self.url, auth=auth)
        self.delete_response = response.text
        return self.delete_response

# Function Driver - To Test the restApi Module Functions
def main():
        testurl  = "http://isis.poly.edu/~marcbudofsky/cs6963-fall2016/URLs"
        testurl2 = "http://whois.arin.net/rest/poc/NYU-ARIN"
        testrequest = httpRequest(testurl2)
        print testrequest.get_request(None, "json")

#main()


"""
 if "https" in self.url:
"""
