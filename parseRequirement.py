# Copyright 2016 VMware, Inc.  All rights reserved. -- VMware Confidential
# Owner: view-osx@vmware.com

import sys
import json
import urllib2

"""
   Currently we always return one kind of requirement.
"""

spec = [
   {
      "os": "10.11", 
      "testcases": [
         "viewUITests/vmtAboutWindow/testOpenAboutWindow"
      ],
      "resources" : {
         "agents": [
            {
               "os": "win7"
            }
         ], 
         "broker": {
            "os": "any"
         }
      }
   },
   {
      "os": "10.11", 
      "was": "true",
      "testcases": [
         "viewUITests/vmtAboutWindow/testOpenAboutWindow"
      ],
      "resources" : {
         "agents": [
            {
               "os": "any"
            }
         ], 
         "broker": {
            "os": "any"
         }
      }
   }
];

print json.dumps(spec)
