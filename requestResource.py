#!/usr/bin/python

import sys
import json
import urllib2

print "input json file: ", str(sys.argv[1]) 
with open(sys.argv[1]) as data_file:    
    data = json.load(data_file)

print "requested resource based on requirement:"
print json.dumps(data, indent=4, sort_keys=True)