#!/usr/bin/python3
"""ratelimit.py: For rate testing a site's XMLRPC file against the host."""
__author__ = "@rfaile313"

import requests
import time
import os

TIMES_TO_TEST = 49 #50 bc index starts @ 0
TIMED_OUT = "Request took longer than a minute to complete. Timed out."
RATELIMIT = "Ratelimit test for:"

headers = {
    'Content-Type': 'text/xml',
    'User-Agent': 'Jetpack by WordPress.com',
}

data = {
  '<?xml version': '"1.0"?><methodCall><methodName>demo.sayHello</methodName><params></params></methodCall>'
}

def detect_https(url):
    if "http" not in url:
        return "https://{}".format(url)
    else:
        return url
  
URL = detect_https(input("Enter the URL. Don't include XMLRPC.php - example: https://example.com \nURL:"))

def test_rate(times_to_run, url):
    current_iteration = 0
    start_time = time.time()
    results = []
    print(RATELIMIT, url)
    while current_iteration <= times_to_run:
        response = requests.post('{}/xmlrpc.php'.format(url), headers=headers, data=data)
        string_response = response_codes(response)
        print(string_response)
        results.append(string_response)
        current_iteration += 1
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
    ending_information = "Done. {} Requests made. Time elapsed: {} Seconds.".format(current_iteration, (total_time))
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
    #turn response into string
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

test_rate(TIMES_TO_TEST, URL)