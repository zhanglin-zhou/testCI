from util.webclientci_log import EntryExit
from util import webclientci_log
import logging
from string import Template

logger = logging.getLogger(__name__)

class Build:
   BUILD_URL = Template('http://buildweb.eng.vmware.com/ob/api/legacy/builds_search/?product=$prod&branch=$bran&count=1&status=succeeded&buildtype=release')
   COMPARE_URL = Template('http://buildweb.eng.vmware.com/api/changelog/between/$b1/and/$b2/')
   PRODUCT_TAG = 'product'
   FILE_TAG = 'file'
   BUILD_NUM_ATTR = 'build_num'
   URL_ATTR = 'url'
   HTMLACCESS_PATH= "//depot/maug/crt-main/view/portal"

   def __init__(self, product, branch, filefilter):
      if product is None or branch is None:
         raise Exception("Invalid product or branch")

      self._product = product
      self._branch = branch
      self._filefilter = filefilter
      self._downloadurl = None
      self._url = self.BUILD_URL.substitute(prod=product, bran=branch)

      self._getinfo()

   @EntryExit()
   def _getinfo(self):
      import urllib2

      try:
         logger.info(self._url)
         rep = urllib2.urlopen(self._url).read()

         # response is like
         # <products>
         #  <product></product>
         # </products>
         from xml.dom.minidom import parseString
         import xml.dom.minidom

         tree = parseString(rep)
         root = tree.documentElement
         prod = root.getElementsByTagName(self.PRODUCT_TAG)[0]

         self.build_num = prod.getAttribute(self.BUILD_NUM_ATTR)

         files = prod.getElementsByTagName(self.FILE_TAG)
         for file in files:
            url = file.getAttribute(self.URL_ATTR)
            if self._filefilter in url:
               self._downloadurl = url
               logger.info("Download URL is %s" % url)
               break

         if self._downloadurl is None:
            logger.error("Failed to get the download URL.")
            exit(1)
      except Exception as e:
         logger.error(e)
         exit(1)

   @EntryExit()
   def compare(self, build_num):
      logger.info("Comparing build %s and %s" % (self.build_num, build_num))
      if build_num == '':
         logger.info("No build to compare.")
         return None
      try:
         if not int(self.build_num) == int(build_num):
            import urllib2
            api = self.COMPARE_URL.substitute(b1=self.build_num, b2=build_num)
            change = urllib2.urlopen(api).read()
            import json
            return json.loads(change)
         else:
            return None
      except Exception as e:
         logger.error(e)
         return None

   @EntryExit()
   def saveDiffContent(self, content, localtmpdir, name):
      diffContent = "no change since last build"
      import os
      diffFilename = os.path.join(localtmpdir, name+'changediff.properties')

      if not content is None:
         diffContent =''
         changes = content["product_diff"]["changes"]
         for change in changes:
            flag = False
            for file in change["files"]:
                if file.find(self.HTMLACCESS_PATH) > -1:
                    flag = True
            if flag == True or not name == 'Portal':
               diffContent = diffContent + 'change '+ change["changenum"] +' by ' + change["username"]+', '


      try:
         DiffName = name + 'DiffContent'
         BuildNumber = name + 'BuildNumber'
         with open(diffFilename,'w') as f:
            f.write("%s" % '')
            f.write("%s=%s\n" % (DiffName,diffContent))
            f.write("%s=%s\n" % (BuildNumber,self.build_num))
      except Exception as e:
         logger.error(e)
         exit(1)

   @EntryExit()
   def download(self, dest):
      if self._downloadurl is None:
         logger.warn("No download URL.")
         return

      import urllib2
      try:
         data = urllib2.urlopen(self._downloadurl).read()
         f = open(dest, 'wb')
         f.write(data)
         f.close()
         logger.info("Build downloaded to %s" % dest)
      except Exception as e:
         logger.error(e)
         exit(1)