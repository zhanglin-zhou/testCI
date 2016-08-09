#!/usr/bin/python
import sys
import json
import urllib2

result = [{
   "agent"     : { "os"     : "win7",
                   "build"  : "4207301"},
   "broker"    : { "os"    : "win2008"},
   "testcases" : ["case1", "case2"],
   "os"        : "10.11"
},
{  "agent"     : { "os"     : "win7",
                   "build"  : "4207301"},
   "broker"    : { "os"     : "win2008"},
   "testcases" : ["case3", "case4"],
   "os"        : "10.11"
},
{
   "agent"     : { "os"     : "win10",
                   "build"  : "4207301"},
   "broker"    : { "os"    : "win2008"},
   "testcases" : ["case5", "case6"],
   "os"        : "10.12"
}];

for i, r in enumerate(result):
   with open(sys.argv[1]+"_"+str(i), 'w') as result_file:
      json.dump(r, result_file)

print json.dumps(result)
