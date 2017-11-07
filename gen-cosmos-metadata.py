#!/usr/bin/env python
"""A python script to generate the meta-data of the cosmos repository for search tool"""
import json
import requests
import sys

base_url = "https://api.github.com/repos/OpenGenus/cosmos/contents/"
token = "YOUR_TOKEN_HERE"
result = {}

def traverse(path):
    r = requests.get(base_url+path+"?access_token="+token)
    data = r.json()
    if "message" in data and data["message"] == "Bad credentials":
        print("Bad credentials/Api Rate Limit exceeded")
        sys.exit(0)

    files = []
    for dirname in data:
        if dirname["type"] == "file":
            files.append(dirname["name"])
            print(dirname["name"])
        else:
            traverse(dirname["path"])

    if len(files) > 0:
        result[path] = files

if __name__ == "__main__":
    traverse("code")
    with open("metadata.json", "w") as f:
        json.dump(result, f)      
