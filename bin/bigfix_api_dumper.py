#!/usr/bin/env python3

import lxml
import requests
from os import environ
import sys
from bigfix_api import RelevanceQueryDumper
import configparser
import json

# extract important variables that were passed in from the wrapper script
AUTH_TOKEN = environ['AUTH_TOKEN']
APP_LOCATION = sys.argv[1]

config_default = APP_LOCATION + "/default/bigfix_api_dumper.conf"
config_local = APP_LOCATION + "/local/bigfix_api_dumper.conf"

# read values in from config file
config = configparser.ConfigParser()
config.read([config_default, config_local])
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

if __debug__:
    print(f"api_url is {bigfix_url}")
    print(f"bigfix username is {username}")
    print(f"bigfix password is {password}")
    print(f"authentication token is {AUTH_TOKEN}")

# object for interacting with splunk's collections api
splunk_collections_session = requests.Session()
splunk_collections_session.headers.update({"Authorization": f"Bearer {AUTH_TOKEN}"})
collection_url = "https://localhost:8089/servicesNS/nobody/bigfix_api_dumper/storage/collections/data/bigfix" 


# object for interacting with BigFix
relevance_api_url = bigfix_url + "/api/query"
bigfix_dumper = RelevanceQueryDumper(relevance_api_url, username, password, verify=False)
# get the a dump from bigfix
bigfix_database = bigfix_dumper.dump(["os", "ip address","User name","License Type","Last Report Time"])
#print(bigfix_database)

splunk_verify = False

# create db object
def create_db_obj(name, properties):
    """ takes in a computer name and dict of properties from bigfix
    returns pivoted object to feed into the kvstore"""
    json_object = {"_key": name}
    json_object.update(properties)
    return json_object


### perform database update opertions
# get all the data in the kvstore
kvstore_request = splunk_collections_session.get(collection_url,
    verify = splunk_verify)
kvstore = json.loads(kvstore_request.text)

# missing items that were removed from bigfix
deleted_keys = []
for item in kvstore:
    # check if we need to update an item
    key = item["_key"]
    if key in bigfix_database:
        # perform update on kvstore
        new_record = create_db_obj(key, 
            bigfix_database[key])
        splunk_collections_session.post(
            collection_url + "/" + key,
            json=new_record,
            verify = splunk_verify
        )
    else: 
        # delete the key from the kvstore, and keep track of missing items
        deleted_keys.append(key)
        splunk_collections_session.delete(
            collection_url + "/" + key,
            verify = splunk_verify
        )
print(f"deleted keys: {deleted_keys}")


# create a list of DB keys to check against
kvstore_keys = [ entry['_key'] for entry in kvstore ]

# new items that were added to bigfix and need to be created in the keystore
new_keys = []
for name,properties in bigfix_database.items():
    if not name in kvstore_keys:
        # create a new item in the kvstore
        new_record = create_db_obj(name, properties)
        new_keys.append(name)
        splunk_collections_session.post(
            collection_url,
            json = new_record,
            verify = splunk_verify
        )

print(f"new keys: {new_keys}")

