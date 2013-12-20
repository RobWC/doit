#!/usr/bin/env python

'''
DevOps Inventory Technician (DOIT)
===================================================

DOIT is a simple dynamic inventory service designed to work exclusively with ansible 
'''

import sys
import os
import argparse
import re
import sqlite3
from time import time
import json


class DOIT(object):
  def _empty_inventory(self):
    return {"_meta": {"hostvars":{}}}

  def get_host_info(self):
    return 'foo'

  def get_inventory(self):
    return self.args.domain

  def parse_cli_args(self):
    ''' Command Line Argument Parser'''
    parser = argparse.ArgumentParser(description='Generate an Ansible Inventory File')
    parser.add_argument('--list',action='store_true',default=True,help='List hosts (default; True)')
    parser.add_argument('--host',action='store',help='Get all the variables about a specific instance')
    parser.add_argument('--domain',action='store',help='Specify the domain of hosts',required=True)
    self.args = parser.parse_args()

  def __init__(self):
    '''Main'''

    #Start with an empty inventory
    self.inventory = self._empty_inventory()

    self.parse_cli_args()

    if self.args.host:
      data_output = self.get_host_info()
    elif self.args.list:
      data_output = self.get_inventory()

    print data_output

DOIT()