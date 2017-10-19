#############################################################################################
#
#
# 	 				REST API DRIVERS
#
# 				AUTHOR: SRINIVAS PISKALA GANESH BABU
#
#				DESCRIPTION:
#
#
#
#				FUNCTIONS:
#
##############################################################################################

# Import Statements for Libraries
import requests # Rest Api Library


def get(url, auth=None):
    response = requests.get('url')
    return response.json()


