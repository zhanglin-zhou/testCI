# Copyright 2016 VMware, Inc.  All rights reserved. -- VMware Confidential
# Owner: view-osx@vmware.com

import json
import logging
import os
import subprocess
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from util import webclientci_log
from util.webclientci_log import EntryExit


TARGET_PLIST_PATH = "~/Library/Preferences/com.vmware.horizon.plist"

BROKER_HOST_ATTR = "host"
RESOURCE_ATTR = "resources"
TEST_CASES_ATTR = "testcases"
USER_ATTR = "user"
USER_NAME_ATTR = "name"
USER_PASSWORD_ATTR = "password"

data = {}


class RunCasesForViewClientMac(object):

   @EntryExit()
   def _prepare_running(self):
      ''' Prepare the envs to run cases '''

      infos = data[RESOURCE_ATTR]
      broker = "https://%s:443/broker/xml" % infos[BROKER_HOST_ATTR]
      username = infos[USER_ATTR][USER_NAME_ATTR]
      password = infos[USER_ATTR][USER_PASSWORD_ATTR]

      cmds = [
         '/usr/libexec/PlistBuddy -c "Add broker-history array" %s' % \
              TARGET_PLIST_PATH,
         '/usr/libexec/PlistBuddy -c "Add broker-history: string %s" %s' % \
              (broker, TARGET_PLIST_PATH),
         '/usr/libexec/PlistBuddy -c "Add https\://%s\:443/broker/xmlusername '
              'string %s" %s' % (infos[BROKER_HOST_ATTR], username,
                                 TARGET_PLIST_PATH),
         '/usr/libexec/PlistBuddy -c "Add promptedUpgradePrinting bool YES" '
              '%s' % TARGET_PLIST_PATH,
         '/usr/libexec/PlistBuddy -c "Add promptedUSBPrintingServicesInstall '
              'bool YES" %s' % TARGET_PLIST_PATH,
         '/usr/libexec/PlistBuddy -c "Add promptSharingChecked bool YES" %s' %\
              TARGET_PLIST_PATH,
         '/usr/libexec/PlistBuddy -c "Add certificateVerificationMode integer 3"'
              ' %s' % TARGET_PLIST_PATH,
         '/usr/libexec/PlistBuddy -c "Add appSessionResumptionMode integer 2"'
              ' %s' % TARGET_PLIST_PATH,
         ]

      logger.info("Try to update info plist")
      for cmd in cmds:
         configure = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE).communicate()
         if not configure[1].strip() == "":
            logger.error('"%s" FAILED' % cmd)
            raise
      logger.info('Info plist update SUCCEED')

      cmd = 'defaults read %s' % TARGET_PLIST_PATH
      load = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE).communicate()
      if not load[1].strip() == "":
         logger.error('"%s" FAILED' % cmd)
         raise
      logger.info('Info plist load SUCCEED')


   @EntryExit()
   def _run_cases(self):
      ''' Run the given cases and return result '''

      cases = data[TEST_CASES_ATTR]
      cmd = 'xcodebuild test-without-building -xctestrun ' \
      'view_macosx10.12-x86_64.xctestrun -destination \'platform=macOS\' '\
      '\'arch=x86_64\''

      for case in cases:
         cmd += (' -only-testing:%s' % case)
      cmd += '| xcpretty'
      run = subprocess.Popen(cmd, shell=True).communicate()
'''
      if -1 != run[0].strip().find('Test execute Succeeded'):
         logger.info('\n\n%s\n\nTest cases run SUCCEED\n\n' % run[0].strip())
      else:
         logger.error('\n\n%s\n\nTest FAILED\n\n' % run[0].strip())
         raise
'''


if __name__ == "__main__":

   os.environ['LOG_LOC'] = os.curdir
   webclientci_log.init_log()
   logger = logging.getLogger(__name__)

   if len(sys.argv) == 1:
      logger.error("Need at least one input file to configure")
      sys.exit(-1)

   configuration_file = sys.argv[1]

   if not os.path.exists(configuration_file):
      logger.error("FAILED to find the given file %s" % configuration_file)
      sys.exit(-1)

   data = json.loads(open(configuration_file).read())

   runner = RunCasesForViewClientMac()
   runner._prepare_running()
   runner._run_cases()
