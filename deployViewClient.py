#!/usr/bin/python

import sys
import json
import urllib2

print "trying to deploy view client build: ", str(sys.argv[1])
print "resouces file: ", str(sys.argv[2]) 
with open(sys.argv[2]) as data_file:    
    data = json.load(data_file)

print "provided resouces:"
print json.dumps(data, indent=4, sort_keys=True)
