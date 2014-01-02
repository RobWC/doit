#!/usr/bin/env python

'''
DevOps Inventory Technician (DOIT) Client
===================================================

DOIT is a simple dynamic inventory service designed to work exclusively with ansible 
'''

import argparse
import urllib2
import sys
#import json

class DOITClient(object):
  '''Client to connect to DOIT server'''

  def get_list(self):
    doit_request = urllib2.urlopen('http://localhost:12345/api/1/ansible/list?domain=production')
    return doit_request.read()

  def get_host(self,host_name):
    doit_request = urllib2.urlopen('http://localhost:12345/api/1/ansible/host?domain=production&host={0}'.format(host_name))
    return doit_request.read()

  def get_ansible_data(self):
    parser = argparse.ArgumentParser(description='Generate an Ansible Inventory File')
    parser.add_argument('--list',action='store_true',default=False,help='List hosts (default: False)')
    parser.add_argument('--host',action='store',help='Get all the variables about a specific instance')
    #add default location for the db /etc/ansible/hosts.sqlite3
    self.args = parser.parse_args()

    if self.args.list == True:
      print self.get_list()
    elif self.args.host != None:
      print self.get_host(self.args.host)
    else:
      print 'Use --help to gather all available options'
      sys.exit(0)

  def __init__(self):
    '''Main'''
    self.get_ansible_data()

if __name__ == "__main__":
  doitClient = DOITClient()