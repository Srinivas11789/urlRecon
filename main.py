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
import os   #-- default lib - packed with python
import sys  #-- default lib
import datetime  #-- default lib

# Import Custom Modules - Self created by the author
sys.path.insert(0, 'modules/')
import restApi
import domainInfoApi
import reportGenerator

# Import 3rd party Libraries -- Needed to be installed using pip
import warnings
warnings.filterwarnings("ignore", category=UserWarning)

def main():
# Argument Fetch from the User
    if len(sys.argv) < 2:
        print "Please enter only the URL for the List of URLs/Domains to Test!"
        print """
======================================================================================================
+ Usage:                                                                                             +
+    "python main.py <url_to_fetch_input_list_to_test> <option_for_report> <output_path_of_report>"  +
+                                                                                                    +
+ Arguments:                                                                                         +
+    * <url_to_fetch_input_list_to_test> - A url where all the urls to test can be fetched           +
+    * <option_for_report> - Output Type for Report                                                  +
+                            * "Text" - For a text based report only                                 +
+                            *  "SQL" - For a SQL Databse of report                                  +
+                            *  "KML" - For a KML based report of geolocation                        +
+    * <output_path_of_report> - Full path where the output shoule be created                        +
+                                                                                                    +
+ Mandatory:                                                                                         +
+    * <url_to_fetch_input_list_to_test>                                                             +
+                                                                                                    +
+ FallBack to Defaults:                                                                              +
+    * <option_for_report>     - Default to all types of output                                      +
+    * <output_path_of_report> - Defaults to current working directory                               +
======================================================================================================="""
        sys.exit()
    urls_file = sys.argv[1]
    option = None
    output_path = os.path.basename(os.path.dirname(os.path.realpath(__file__)))
    if len(sys.argv) > 2:
        option = sys.argv[2]
        output_path = sys.argv[3]
        if option.lower() == "kml":
            option = "kml"
        elif option.lower() == "text":
            option = "text"
        elif option.lower() == "sql":
            option = "sql"
        else:
            option = None
            print "Option provided not recognized, proceed with option to output all type of report!\n"

# Make Web Request to Fetch the List of urls
    urls_to_test = restApi.httpRequest(urls_file).get_request()
    urls_to_test = urls_to_test.split('\n')

# Report Initiation
    try:
      report = reportGenerator.reportGen(output_path)
    except:
      print " ==> Report Path Invalid error, Proceeding with report creation at the current folder!\n"
      try:
       report = reportGenerator.reportGen(os.path.basename(os.path.dirname(os.path.realpath(__file__))), option)
      except Exception as e:
        end_time = datetime.datetime.utcnow()
        print "\n"
        print " ==> Exception: %s" % (str(e.message))
        print " ==> Program ended at %s" % (str(end_time))
        print " =========> Program Finished with Failure !!!\n"
        sys.exit()

    start_time = datetime.datetime.utcnow()
    print " ==> Program Started at %s" % (str(start_time))
    print " ==> Fetching Information for various URLs",
# Get the Whois Data of all the domains
    try:
        for url in urls_to_test:
            domain_info = domainInfoApi.domainInfo(url)
            report.push_data_to_report(domain_info)
            print ".",
            sys.stdout.flush()
    except Exception as e:
        end_time = datetime.datetime.utcnow()
        print "\n"
        print " ==> Exception: %s" % (str(e.message))
        print " ==> Program ended at %s" % (str(end_time))
        print " =========> Program Finished with Failure !!!\n"
        report.close_all()
        sys.exit()

# Close Call
    report.close_all()

    end_time = datetime.datetime.utcnow()
    print "\n"
    print " ==> Program ended at %s" % (str(end_time))
    print " ==> Output Successfully Generated at " + output_path
    print " ==> Time for the Program to Complete Execution = %s" % (end_time - start_time)
    print " =========> Program Finished Successfully !!!\n"

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