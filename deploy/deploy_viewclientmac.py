# Copyright 2016 VMware, Inc.  All rights reserved. -- VMware Confidential
# Owner: view-osx@vmware.com

import argparse
import json
import logging
import os
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


class DeployViewClientMac(object):

   # Below are methods related to clean up env.
   @EntryExit()
   def _remove_old_build(self):
      ''' Remove the old build from INSTALL_PATH folder '''

      logger.info('Remove "%s"' % CLIENT_PATH)
      cmd = "rm -rf '%s'" % CLIENT_PATH
      remove = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE).communicate()
      if not remove[1].strip() == "":
         logger.error('"%s" FAILED' % cmd)
         raise
      logger.info('Remove old "%s" SUCCEED' % CLIENT_PATH)

   @EntryExit()
   def _unmount_dmg(self):
      ''' Unmount DMG file '''

      logger.info('Unmount the installer')
      cmd = 'hdiutil detach -force "%s"' % MOUNT_POINT
      unmount = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE).communicate()
      if not unmount[1].strip() == "":
         logger.error('"%s" FAILED' % cmd)
         raise
      logger.info('Unmount SUCCEED')

   @EntryExit()
   def _remove_cache(self):
      ''' Remove Cache files, like log, plist, Applicaton Support etc. '''
      locations = [
         ' %s/*.log' % os.curdir,
         ' ~/Library/Logs/VMware',
         ' ~/Library/Logs/"%s"' % CLIENT_TITLE,
         ' ~/Library/Preferences/com.vmware.horizon.plist',
         ' ~/Library/Preferences/com.vmware.horizon.keyboard.plist',
         ' ~/Library/Application\ Support/VMware\ Horizon\ View\ Client'
         ]
      cmd = 'rm -rf'
      for path in locations:
         cmd += path
      logger.info('Remove cache')
      remove = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE).communicate()
      if not remove[1].strip() == "":
         logger.error('"%s" FAILED' % cmd)
         raise
      logger.info('Remove cache SUCCEED')

   @EntryExit()
   def _restart_dock(self):
      ''' Restart Dock to clear garbage app icon in LaunchPad '''
      cmd = 'defaults write com.apple.dock ResetLaunchPad -bool true; \
             killall Dock'
      logger.info('Restart Dock')
      restart = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE).communicate()
      if not restart[1].strip() == "":
         logger.error('"%s" FAILED' % cmd)
         raise
      logger.info('Restart Dock SUCCEED')

   @EntryExit()
   def _reset_launch_services(self):
      ''' Reset launch services to clear garbage data in context menu '''

      cmd = ("/System/Library/Frameworks/CoreServices.framework/Versions/A/" +
             "Frameworks/LaunchServices.framework/Versions/A/Support/" +
             "lsregister -kill -r -domain local -domain system -domain " +
             "user; killall Finder")
      logger.info('Reset launch services')
      reset = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE).communicate()
      if not reset[1].strip() == "":
         logger.error('"%s" FAILED' % cmd)
         raise
      logger.info('Reset launch services SUCCEED')


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
         if info[DOWNLOAD_URL_ATTR].endswith(("dmg")):
            FancyURLopener(proxies={}).retrieve(info[DOWNLOAD_URL_ATTR],
                                                INSTALL_FILE)
            logger.info('Download %s to %s SUCCEED' %
                        (info[DOWNLOAD_URL_ATTR], INSTALL_FILE))



   # Below are methods related to install Horizon Mac Client.
   @EntryExit()
   def _mount_and_install(self):
      ''' Mount dmg file and install Mac client '''

      logger.info('Mount the installer dmg')
      cmd = 'hdiutil attach -mountpoint %s -noverify %s' % (MOUNT_POINT,
                                                            INSTALL_FILE)
      mount = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE).communicate()
      if not mount[1].strip() == "":
         logger.error('"%s" FAILED' % cmd)
         raise
      logger.info('Mount SUCCEED for %s' % INSTALL_FILE)

      logger.info('Copy the bundle to %s' % INSTALL_PATH)
      cmd = "cp -rf '%s' '%s'" % (MOUNT_APP, INSTALL_PATH)
      copy = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE).communicate()
      if not copy[1].strip() == "":
         logger.error('"%s" FAILED' % cmd)
         raise
      logger.info('Copy "%s" to /Applicatons SUCCEED' % MOUNT_APP)


   # Wrapper for clean up env.
   @EntryExit()
   def clean(self):
      ''' Clean up the env for deploy '''

      if os.path.exists(MOUNT_POINT):
         deployer._unmount_dmg()
      self._remove_old_build()
      self._remove_cache()
      self._reset_launch_services()
      self._restart_dock()


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

      try:
         self._mount_and_install()
      except:
         if os.path.exists(MOUNT_POINT):
            logger.info('Unmount after install')
            self._unmount_dmg()

         logger.error('Install FAILED, try to remove app')
         self._remove_old_build()
         sys.exit(-1)
      else:
         if os.path.exists(MOUNT_POINT):
            logger.info('Unmount after install')
            self._unmount_dmg()


if __name__ == "__main__":

   parser = argparse.ArgumentParser(description='Deploy VMware Horizon Client')
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
   deployer = DeployViewClientMac()

   if args.clean:
      deployer.clean()
   if args.build_num and not args.build_num.strip() == "":
      build_number = args.build_num
      deployer.download()
   if args.install:
      deployer.install()
