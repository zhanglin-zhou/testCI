import ConfigParser
import logging
from util.webclientci_log import EntryExit

logger = logging.getLogger(__name__)

class ExistingBuild:
   BUILD_INFO = 'c:/htmlaccess/.buildinfo'
   BROKER_SECTION = 'BROKER'
   BROKER_SECTION_OPT = 'VCS'
   AGENT_SECTION = 'AGENT'
   AGENT_SECTION_CLIP = 'CLIPBOARD'
   HTMLACCESS_PORTAL = 'HTMLACCESS'
   BUILD_NUM_OPT = 'BUILDNUMBER'


   def __init__(self, product):

      self.SECTIONS = [self.BROKER_SECTION, self.AGENT_SECTION, self.HTMLACCESS_PORTAL]

      self._product = product.upper()
      if not self._product in self.SECTIONS:
         logger.error("%s is an invalid product name." % product)
         exit(1)

      self.OPTIONS = {self.BROKER_SECTION: self.BROKER_SECTION_OPT, self.AGENT_SECTION: self.AGENT_SECTION_CLIP,self.HTMLACCESS_PORTAL:self.BUILD_NUM_OPT}


   @EntryExit()
   def getbuildnum(self):
      config = ConfigParser.ConfigParser()
      config.optionxform = str
      try:
         config.read(self.BUILD_INFO)
      except Exception as e:
         logger.warning(e)

      if not config.has_section(self._product):
         logger.warning("%s does not have valid build information" % self.BUILD_INFO)
         return ''

      try:
         build_number = config.get(self._product, self.OPTIONS.get(self._product))
         logger.info("Build number is %s" % build_number)
         return build_number
      except Exception as e:
         logger.warn(e)
         return ''

   @EntryExit()
   def writebuildnum(self, build_number):
      config = ConfigParser.ConfigParser()
      config.optionxform = str
      config.add_section(self._product)
      config.set(self._product, self.OPTIONS.get(self._product), build_number)

      cfgfile = None
      try:
         import os
         paredir = os.path.abspath(os.path.join(self.BUILD_INFO, os.pardir))
         if not os.path.exists(paredir):
            os.makedirs(paredir)
            logger.info("Created directory %s." % paredir)

         cfgfile = open(self.BUILD_INFO, 'w')
         config.write(cfgfile)
         logger.info("Successfully wrote build information, [%s]%s=%s" % (self._product, self.OPTIONS.get(self._product), build_number))
      except Exception as e:
         logger.warn(e)
      finally:
         if cfgfile is not None:
            cfgfile.close()