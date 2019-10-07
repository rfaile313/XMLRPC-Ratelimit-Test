#!/usr/bin/python3
"""ratelimit.py: For rate testing a site's XML-RPC file against the host."""
__author__ = "@rfaile313"

import requests
import time
import sys
import os

TIMES_TO_TEST = 50 
TIMED_OUT = "Request took longer than a minute to complete. Timed out."
RATELIMIT = "Ratelimit test for:"

headers = {
    'Content-Type': 'text/xml',
    'User-Agent': 'Jetpack by WordPress.com',
}

data = {
  '<?xml version': '"1.0"?><methodCall><methodName>demo.sayHello</methodName><params></params></methodCall>'
}

#some very basic error handling for URL structure
def detect_https(url):
    if "http" not in url and '/xmlrpc.php' not in url:
        return "https://{}/xmlrpc.php".format(url)
    elif "/xmlrpc.php" in url and "http" not in url:
        return "https://{}".format(url)
    else:
        return url + '/xmlrpc.php'

#detects if a URL is appended as a flag in the terminal, otherwise asks for it
try:
    URL = detect_https(sys.argv[1])
except IndexError:
    #no argument provided
    URL = detect_https(input("Enter the URL. Example: https://example.com \nURL:"))

def test_rate(url):
    start_time = time.time()
    results = []
    print(RATELIMIT, url)
    for i in range(TIMES_TO_TEST):
        response = requests.post(url, headers=headers, data=data)
        string_response = response_codes(response)
        print(string_response)
        results.append(string_response)
        ### This section checks to see if its been longer than a minute, then times out. 
        current_time = time.time()
        check_time = str(round((current_time - start_time), 2))
        float_time = float(check_time)
        if float_time >= 60:
            print(TIMED_OUT)
            break
        ### End timeout check
    end_time = time.time()
    total_time = str(round((end_time - start_time), 2))
    ending_information = "Done. {} Requests made. Time elapsed: {} Seconds.".format(i + 1, (total_time))
    print (ending_information)

    ## Ask/Write to file
    text_file = ask_yes_no("Would you like to send the results to a text file? [y/n]: ")
    if text_file == 'y' or text_file == 'yes':
        with open("results{}.txt".format(total_time), "w") as file:
            file.write("Ratelimit Test for {}:\n".format(url))
            for item in results:
                file.write("{}\n".format(item))
            ## timeout check
            if float_time >= 60:
                file.write("\n {}".format(TIMED_OUT))
            file.write(ending_information)
            file.write("\n============ End of Test ===========")
            file.close()
            print("results{}.txt written at {}".format(total_time, os.getcwd()))
    else:
        pass        

def ask_yes_no(question):
    response = None
    while response not in ('yes', 'y', 'no', 'n'):
        response = input(question).lower()
    return response

def response_codes(response):
    #Common Response Codes
    #TODO could definitely add more, or be more specific 🤷
    string_response = str(response)
    if "20" in string_response:
        string_response = string_response + " OK"
    elif "405" in string_response:
        string_response = string_response + " 405 Method Not Allowed. Are you using HTTP? Try HTTPS."
    elif "404" in string_response:
        string_response = string_response + " 404 Page not found"
    elif "40" in string_response:
        string_response = string_response + " 4xx Client Error"
    elif "50" in string_response:
        string_response = string_response + " 5xx Server Error"
    elif "429" in string_response:
        string_response = string_response + " TOO MANY REQUESTS!!"
    else:
        string_response = string_response + " Look up Response Code"
    return string_response

test_rate(URL)