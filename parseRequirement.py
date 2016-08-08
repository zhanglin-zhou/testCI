#!/usr/bin/python
import sys
import json
import urllib2

result = [{
   "agent" : { "os"     : "win7",
               "build"  : "4207301"},
   "broker" : { "os"    : "win2008"},
   "testcases" : ["case1", "case2"]
},{
   "agent" : { "os"     : "win10",
               "build"  : "4207301"},
   "broker" : { "os"    : "win2008"},
   "testcases" : ["case3", "case4"]
}];

for i, r in enumerate(result):
   with open(sys.argv[1]+"_"+str(i), 'w') as result_file:
      json.dump(r, result_file)

print json.dumps(result)
