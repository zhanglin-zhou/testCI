# Copyright 2016 VMware, Inc.  All rights reserved. -- VMware Confidential
# Owner: view-osx@vmware.com

import argparse
import copy
import fcntl
import json
import logging
import sys

#sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

#from util import webclientci_log
#from util.webclientci_log import EntryExit

class ResourcePoolManager(object):

   #@EntryExit()
   def apply_resource(self, requirements, pool):
      '''
      request the resource specified in requirements from given pool resources
      '''
      req_res = []
      for req in requirements:
         b_req_os = req['broker']['os']
         #filter broker os
         brokers = [b for b in pool if b_req_os == 'any' or b_req_os == b['os']]
         select_broker = None
         select_agents = None
         for b in brokers:
            try:
               select_agents = []
               agents = copy.copy(b['agents'])
               for a_req in req['agents']:
                  a_req_os = a_req['os']
                  agent = next(a for a in agents if a_req_os == 'any' or a_req_os == a['os'])
                  select_agents.append(agent)
                  agents.remove(agent)
            except:
               select_agents = None
            else:
               select_broker = copy.copy(b)
               break
         if select_broker is not None:
            agent_res = select_broker['agents']
            for agent in select_agents:
               agent_res.remove(agent)
            select_broker['agents'] = select_agents
            req_res.append(select_broker)
         else:
            raise
      return req_res

   #@EntryExit()
   def release_resource(self, resources, pool):
      '''
         release resources to given pool
      '''
      for res in resources:
         broker = None
         try:
            broker = next(b for b in pool if b['host'] == res['host'])
         except StopIteration:
            pool.append(res)
         else:
            broker['agents'] += res['agents']

if __name__ == '__main__':
   parser = argparse.ArgumentParser(description ='Request or release resource')
   parser.add_argument('-a',
                       '--apply',
                       help='The required resource with json format',
                       action='store',
                       type=file,
                       dest='requirements')
   parser.add_argument('-r',
                       '--release',
                       help='The released resource with json format',
                       action='store',
                       type=file,
                       dest='resources')
   parser.add_argument('-p',
                       '--pool',
                       help='The available resources with json format',
                       action='store',
                       type=argparse.FileType('r+'),
                       dest='pool',
                       required=True)

   #os.environ['LOG_LOC'] = os.curdir
   #webclientci_log.init_log()
   logger = logging.getLogger(__name__)

   args = parser.parse_args()
   manager = ResourcePoolManager()

   pool = None
   requested_resources = None

   if args.pool is not None:
      fcntl.lockf(args.pool, fcntl.LOCK_EX)
      pool = json.load(args.pool)

   try:
      if args.resources is not None:
         resources = json.load(args.resources)
         manager.release_resource(resources['resouces'], pool)

      if args.requirements is not None:
         requirements = json.load(args.requirements)
         requested_resources = manager.apply_resource(requirements['resources'], pool)

      args.pool.seek(0)
      args.pool.truncate(0)
      json.dump(pool, args.pool)

      if requested_resources is not None:
         requirements['resources'] = requested_resources
         print json.dumps(requirements)
   except Exception as e:
      logging.exception('')
      sys.exit(-1)