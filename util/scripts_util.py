import logging
import os
import datetime
from util.webclientci_log import EntryExit
import shutil
import stat


logger = logging.getLogger(__name__)

class ScriptService:
   ''' 
   copy2share: Used by script service box.  
      Copy scripts from p4 location to shared location, and name the folder to current time
   copy_from_share: Find the latest scripts from the shared location, and copy them local
   '''  
   
   FORMAT = "%Y-%m-%d_%H.%M.%S"
   DAYS_DELTA = 3

   def __init__(self):
      pass

   def _del_rw(self, action, name, exc):
      os.chmod(name, stat.S_IWRITE)
      os.remove(name)
      
   def _force_remove(self, file):
      os.chmod(file, stat.S_IWRITE)
      os.remove(file)

   @EntryExit()
   def copy2share(self, src_dir, dest_dir):

      # We don't need to verify the source directory since this file is in source directory
      if os.path.exists(dest_dir) and os.path.isdir(dest_dir):
         pass
      else:
         logger.error("Target directory does not exists")
         exit(1)

      tempdir = os.path.join(dest_dir, "temp")
      if os.path.exists(tempdir) and os.path.isdir(tempdir):
         logger.warn("%s exists, removing it" % tempdir)
         try:
            shutil.rmtree(tempdir, onerror=self._del_rw)
         except Exception as e:
            logger.error("Failed to remove %s" % tempdir)
            logger.error(e)
            exit(1)

      try:
         shutil.copytree(src_dir, tempdir)
         logger.info("Successfully copied scripts to %s." % tempdir)
      except shutil.Error as e:
         logger.error("Failed to copy scripts to %s." % tempdir)
         logger.error(e)
         exit(1)

      # rename the temp dir
      n = datetime.datetime.now().strftime(self.FORMAT)
      dirname = os.path.join(dest_dir, n)
      logger.info("Renaming %s to %s" % (tempdir, dirname))

      try:
         os.rename(tempdir, dirname)
         logger.info("Successfully renamed %s to %s." % (tempdir, dirname))
      except OSError as e:
         logger.info("Failed to rename %s to %s" % (tempdir, dirname))
         logger.error(e)
         exit(1)

      # start to remove old directories
      self._remove_old(dest_dir)

   def _remove_old(self, dest_dir):
      subdirs = self._get_subdirs(dest_dir)
      for sub in subdirs:
         cdir = os.path.join(dest_dir, sub)
         try:
            t = datetime.datetime.strptime(sub, self.FORMAT)
            delta = datetime.datetime.now() - t
            if delta.days >= self.DAYS_DELTA:
               try:
                  shutil.rmtree(cdir, onerror=self._del_rw)
                  logger.info("Successfully remove %s" % cdir)
               except Exception as e:
                  logger.error(e)
                  exit(1)
         except:
            # if the dir is not the time format, ignore it
            logger.info("Ignore directory %s" % cdir)

   def _get_subdirs(self, dir):
      return [name for name in os.listdir(dir)
              if os.path.isdir(os.path.join(dir, name))]
   
   def _listdir(self, dir, action1, action2):
      for the_file in os.listdir(dir):
         file_path = os.path.join(dir, the_file)
         try:
            logger.info("Current file %s" % file_path)
            if os.path.isfile(file_path):
               action1(file_path)
            elif os.path.isdir(file_path):
               action2(the_file)
         except Exception, e:
            raise e
            exit(1)

   @EntryExit()
   def copy_from_share(self, share, dest):
      scripts_dir = self._get_latest(share)
      if scripts_dir is None:
         logger.error("Have not got valid scripts directory from %s" % share)
         exit(1)
      else:
         scripts_dir = os.path.join(share, scripts_dir)
         logger.info("target scripts directory %s " % scripts_dir)
      
      try: 
         logger.info("Removing old scripts...")
         self._listdir(dest, lambda f: self._force_remove(f), 
                       lambda f: shutil.rmtree(os.path.join(dest, f), onerror=self._del_rw))

         logger.info("Copying the latest scripts...")
         self._listdir(scripts_dir, lambda f: shutil.copy(f, dest), 
                        lambda f: shutil.copytree(os.path.join(scripts_dir, f), os.path.join(dest, f)))
      except Exception, e:
         logger.error(e)
         exit(1)
            
            
   def _get_latest(self, dir):
      'get the latest scripts'
      
      latest = None
      for the_file in os.listdir(dir):
         try:
            file_path = os.path.join(dir, the_file)
            if os.path.isdir(file_path):
               d = datetime.datetime.strptime(the_file, self.FORMAT)
               if latest is None:
                  latest = d
               elif d > latest:
                  latest = d
         except Exception, e:
            logger.warn(e)
            exit(1)

      return datetime.datetime.strftime(latest, self.FORMAT)

if __name__ == "__main__":
   from util import webclientci_log
   webclientci_log.init_log()

   ss = ScriptService()
   ss.copy2share("c:/Users/bnie/Perforce/win_laptop/crt-webclientci/view/portal/ci", "c:/Temp/test")