#!/usr/bin/python

import sys
import json
import urllib2

print "input json file: ", str(sys.argv[1]) 
with open(sys.argv[1]) as data_file:    
    data = json.load(data_file)

print "requested resource based on requirement:"
print json.dumps(data, indent=4, sort_keys=True)

resources = { "broker" : "10.112.118.187",
              "agent"  : "agent1"
            }

output = {
   "resources" : resources,
   "testcases" : data["testcases"]
}

with open(sys.argv[2], 'w') as out_file:
   json.dump(output, out_file)


print "provided resources:"
print json.dumps(resources, indent=4, sort_keys=True)