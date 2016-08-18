# Copyright 2016 VMware, Inc.  All rights reserved. -- VMware Confidential
# Owner: view-osx@vmware.com

import sys
import json
import urllib2

"""
   Currently we always return one kind of requirement.
    
   {
      "os": "10.12", 
      "was": "true",
      "testcases": [
         "mac_bat/test2"
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
   ,
   {
      "os": "10.12", 
      "testcases": [
         "viewUITests/vmtAboutWindow/testConnectToDesktop"
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
   },
"""

spec = [
   {
      "os": "10.11", 
      "testcases": [
         "viewUITests/vmtAboutWindow/testOpenAboutWindow",
         "viewUITests/vmtAboutWindow/testConnectToDesktop"
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
   }
];

print json.dumps(spec)
