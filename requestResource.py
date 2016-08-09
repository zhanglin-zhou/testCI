#!/usr/bin/python

import sys
import json
import urllib2

print "input json file: ", str(sys.argv[1]) 
with open(sys.argv[1]) as data_file:    
    data = json.load(data_file)

print "requested resource based on requirement:"
print json.dumps(data, indent=4, sort_keys=True)

resources = [{
   "agent"     : "agent1",
   "broker"    : "10.112.118.187",
   "testcases" : ["case1", "case2"],
   "os"        : "10.11"
},
{  "agent"     : "agent2",
   "broker"    : "10.112.118.187",
   "testcases" : ["case3", "case4"],
   "os"        : "10.11"
},
{
   "agent"     : "agent3",
   "broker"    : "10.112.118.187",
   "testcases" : ["case5", "case6"],
   "os"        : "10.12"
}]

with open(sys.argv[2], 'w') as out_file:
   json.dump(resources, out_file)


print "provided resources:"
print json.dumps(resources, indent=4, sort_keys=True)
