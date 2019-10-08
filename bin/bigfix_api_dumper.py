import lxml
import requests
import os

from bigfix_api import RelevanceQueryDumper

print("i am inside the script")
print(f"my auth token is {os.environ['tok']}")