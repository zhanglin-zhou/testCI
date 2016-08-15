'''
Created on 2016/1/29

Initialize the root log
log directory should be passed by Jenkins job

@author: bnie
'''

import functools
import logging

def init_log():
   formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

   ch = logging.StreamHandler()
   ch.setLevel(logging.INFO)
   ch.setFormatter(formatter)

   root_logger = logging.getLogger("")
   root_logger.setLevel(logging.INFO)
   root_logger.addHandler(ch)

   log_dir = None
   # init log file
   import os
   try:
      log_dir = os.environ['LOG_LOC']
   except:
      pass

   if log_dir is None:
      root_logger.info("log_dir is not set, using user_home")
      from os.path import expanduser

      # Use ~/logs as the default log directory
      log_dir = os.path.join(expanduser("~"), "logs")

   if os.path.exists(log_dir) and os.path.isdir(log_dir):
      pass
   else:
      try:
         os.makedirs(log_dir)
      except Exception as e:
         root_logger.error(e)
         exit(1)

   # build number is passed by Jenkins
   build_number = None
   try:
      build_number = os.environ['BUILD_NUMBER']
   except:
      pass

   if build_number is None:
      from datetime import datetime as dt
      build_number = dt.now().microsecond

   import datetime

   log_file_name = os.path.join(log_dir, "".join([str(datetime.date.today()), "_", str(build_number), ".log"]))

   if log_file_name is None:
      root_logger.error("Failed to get log file name")
      exit(1)

   fh = logging.FileHandler(log_file_name)
   fh.setLevel(logging.INFO)
   fh.setFormatter(formatter)
   root_logger.addHandler(fh)

class EntryExit(object):
   '''
   Automatic log decorator for method entry and exit
   '''

   ENTRY_MESSAGE = 'Entering {}'
   EXIT_MESSAGE = 'Exiting {}'

   def __init__(self, logger=None):
      self.logger = logger

   def __call__(self, func):
      # set logger if it was not set earlier
      if not self.logger:
         self.logger = logging.getLogger(func.__module__)

         @functools.wraps(func)
         def wrapper(*args, **kwds):
            self.logger.info(self.ENTRY_MESSAGE.format(func.__name__))
            f_result = func(*args, **kwds)
            self.logger.info(self.EXIT_MESSAGE.format(func.__name__))
            return f_result
         return wrapper
