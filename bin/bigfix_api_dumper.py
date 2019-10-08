#!/usr/bin/env python3

import lxml
import requests
from os import environ
import sys
from bigfix_api import RelevanceQueryDumper
import configparser

# extract important variables that were passed in from the wrapper script
AUTH_TOKEN = environ['AUTH_TOKEN']
CONFIG_FILE = sys.argv[1]

# read values in from config file
config = configparser.ConfigParser()
config.read(CONFIG_FILE)
try:
    bigfix_url = config["DEFAULT"]["bigfix_api_url"]
except:
    sys.exit("bigfix_api_url missing from config")
try:
    username = config["DEFAULT"]["username"]
except:
    sys.exit("username missing from config")
try:
    password = config["DEFAULT"]["password"]
except:
    sys.exit("password missing from config")

print(f"api_url is {bigfix_url}")
print(f"bigfix username is {username}")
print(f"bigfix password is {password}")
print(f"authentication token is {AUTH_TOKEN}")

# object for interacting with splunk's collections api
splunk_collections_session = requests.Session()

splunk_collections_session.headers.update({"Authorization": f"Bearer {AUTH_TOKEN}"})

collection_url = "https://localhost:8089/servicesNS/nobody/bigfix_api_dumper/storage/collections/config" 

collections = splunk_collections_session.get(collection_url, verify=False)


print(collections.status_code)
print(collections.text)




