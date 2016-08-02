#!/usr/bin/python

import json
import urllib2

buildinfo = json.load(urllib2.urlopen("http://buildapi.eng.vmware.com/ob/build/?product=viewclientmac&branch=crt-main&buildstate__in=succeeded,storing&buildtype=beta&_limit=1&_order_by=-id"))
print buildinfo['_list'][0]['id']