# Copyright 2016 VMware, Inc.  All rights reserved. -- VMware Confidential
# Owner: view-osx@vmware.com

import argparse
import json
import logging
import os
import re
import subprocess
import sys
import urllib2

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from urllib import FancyURLopener

from util import webclientci_log
from util.webclientci_log import EntryExit


CLIENT_TITLE = "VMware Horizon Client"
INSTALL_PATH = "/Applications"
INSTALL_FILE = "installer.dmg"
CLIENT_PATH = "%s/%s.app" % (INSTALL_PATH, CLIENT_TITLE)
MOUNT_POINT = "%s/installer" % os.curdir
MOUNT_APP = "%s/%s.app" % (MOUNT_POINT, CLIENT_TITLE)

DELIVERABLE_URL_ATTR = "_deliverables_url"
DOWNLOAD_URL_ATTR = "_download_url"
LIST_ATTR = "_list"
URL_PREFIX = "http://buildapi.eng.vmware.com"

build_number = ""


class DeployAgent(object):

   # Below are methods related to clean up env.
   @EntryExit()
   def _remove_old_build(self):
      ''' Remove the old build from INSTALL_PATH folder '''


   @EntryExit()
   def _remove_cache(self):
      ''' Remove Cache files, like log, plist, Applicaton Support etc. '''


   # Below are methods related to download components from buildweb.
   @EntryExit()
   def _download_build(self):
      build_url = URL_PREFIX
      if build_number.startswith(('4', '5', '6')):
         build_url += "/ob"
      else:
         build_url += "/sb"
      build_url += "/build/%s" % build_number
      logger.info("Build url is %s" % build_url)

      resource = json.loads(urllib2.urlopen(build_url).read())
      deliverable_url = URL_PREFIX + "/%s" % resource[DELIVERABLE_URL_ATTR]
      infos = json.loads(urllib2.urlopen(deliverable_url).read())
      for info in infos[LIST_ATTR]:
         if info[DOWNLOAD_URL_ATTR].find("VMware-viewconnectionserver") > 0:
            filename = os.path.basename(info['path'])
            FancyURLopener(proxies={}).retrieve(info[DOWNLOAD_URL_ATTR], filename)
            logger.info('Download %s to %s SUCCEED' %
                        (info[DOWNLOAD_URL_ATTR], filename))


   # Wrapper for clean up env.
   @EntryExit()
   def clean(self):
      ''' Clean up the env for deploy '''


   # Wrapper for download components.
   @EntryExit()
   def download(self):
      ''' Download components, add retry in case there is network issue '''

      attemps = 0
      while attemps < 10:
         attemps += 1
         try:
            self._download_build()
         except:
            logger.error('Download failed for %d times' % attemps)
         else:
            return
         logger.error('Download FAILED for too many times')
         sys.exit(-1)


   # Wrapper for installation.
   @EntryExit()
   def install(self):
      ''' Install and unmount the dmg after '''


if __name__ == "__main__":

   parser = argparse.ArgumentParser(description='Deploy VMware Horizon Agent')
   parser.add_argument("-b", help="Dowload the given build",
                       action="store", dest="build_num", metavar="build_number")
   parser.add_argument("-c", help="Clean up the env for deploy",
                       action="store_true", dest="clean")
   parser.add_argument("-i", help="Install VMware Horizon Client",
                       action="store_true", dest="install")
   args = parser.parse_args()

   os.environ['LOG_LOC'] = os.curdir
   webclientci_log.init_log()
   logger = logging.getLogger(__name__)
   deployer = DeployAgent()

   if args.clean:
      deployer.clean()
   if args.build_num and not args.build_num.strip() == "":
      build_number = args.build_num
      deployer.download()
   if args.install:
      deployer.install()
