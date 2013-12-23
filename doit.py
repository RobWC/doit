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

class Domain(object):
  def __init__(self):
    self.id = 0
    self.name = ''

class Host(object):
  def __init__(self,name,id):
    self.name = name
    self.id = id
    self.vars = {}
  def addVar(self,name,value):
    self.vars[name] = value
  def getVarsCount(self):
    return len(self.vars.keys())
  def toDict(self):
    returnDict = {self.name:{}}

    if self.vars != {}:
      returnDict[self.name]['vars'] = self.vars

    return returnDict

class Group(object):
  def __init__(self,name,id):
    self.name = name
    self.id = id
    self.hosts = []
    self.vars = {}
    self.children = []
  def addHost(self,host):
    self.hosts.append(host)
  def addVar(self,name,value):
    self.vars[name] = value
  def addChildren(self,name):
    self.children.append(name)
  def toDict(self):
    returnDict = {self.name:{}}

    if self.vars != {}:
      returnDict[self.name]['vars'] = self.vars

    if self.children != []:
      returnDict[self.name]['children'] = self.children

    if self.hosts != []:
      strHosts = []
      for host in self.hosts:
        strHosts.append(host.name)

      returnDict[self.name]['hosts'] = strHosts

    return returnDict

'''
{
    "databases"   : {
        "hosts"   : [ "host1.example.com", "host2.example.com" ],
        "vars"    : {
            "a"   : true
        }
    },
    "webservers"  : [ "host2.example.com", "host3.example.com" ],
    "atlanta"     : {
        "hosts"   : [ "host1.example.com", "host4.example.com", "host5.example.com" ],
        "vars"    : {
            "b"   : false
        },
        "children": [ "marietta", "5points" ],
    },
    "marietta"    : [ "host6.example.com" ],
    "5points"     : [ "host7.example.com" ]
}

{
    # results of inventory script as above go here
    # ...
    "_meta" : {
       "hostvars" : {
          "moocow.example.com"     : { "asdf" : 1234 },
          "llama.example.com"      : { "asdf" : 5678 },
       }
    }

}
'''

class DOIT(object):
  '''Database methods'''
  def open_database(self):
    dbLocation = ''
    if (self.args.db != None):
      dbLocation = self.args.db
    else:
      dbLocation = '/etc/ansible/hosts.db'
    
    try:
      if (os.path.exists(dbLocation)):
        self.db = sqlite3.connect(dbLocation)
      else:
        raise Exception("DBOpenError")
    except:
      print "Error: Unable to open database"
      sys.exit(1)

  def get_domain_id(self,name):
    cursor = self.db.cursor()
    cursor.execute("SELECT ROWID,name FROM domains WHERE name = '%s'" % name)
    result = cursor.fetchone()
    
    #Check that domain exists
    if (result is not None and result[0] is not None and result[1] is not None):
      self.domain.name = result[1]
      self.domain.id = result[0]
      if (self.domain.name == '' and self.domain.id == 0):
        print "Unable to find specified domain"
        sys.exit(1)
    else: 
      print "Unable to find specified domain"
      sys.exit(1)

  def get_groups_by_domain(self):
    '''Returns an array of Group objects that belong to the active domain'''
    cursor = self.db.cursor()
    cursor.execute("SELECT rowid,name FROM ans_groups WHERE domain = '%d'" % self.domain.id)
    group_list = []
    for group in cursor.fetchall():
      groupID = group[0]
      groupName = group[1]
      newGroup = Group(groupName,groupID)
      group_list.append(newGroup)

    return group_list

  def get_group_members(self,group):
    '''Get group members by Group'''
    #get group members
    cursor = self.db.cursor()
    cursor.execute("SELECT rowid,host FROM ans_host_group_members WHERE ans_group = '{0}' AND domain = '{1}'".format(group.id,self.domain.id))
    for host in cursor.fetchall():
      newHost = self.get_host_by_id(host[0])
      group.addHost(newHost)
      self.hosts.append(newHost)

    return group

  def get_group_vars(self,group):
    '''Get group vars by Group'''
    cursor = self.db.cursor()
    cursor.execute("SELECT name,value FROM ans_group_vars WHERE ans_group = '{0}' AND domain = '{1}'".format(group.id,self.domain.id))
    for groupVar in cursor.fetchall():
      group.addVar(groupVar[0],groupVar[1])

    return group

  def get_host_vars(self,hostid):
    '''Get host vars'''
    hostvars = []
    cursor = self.db.cursor()
    cursor.execute("SELECT name,value FROM host_vars WHERE host = '{0}' AND domain = '{1}'".format(hostid,self.domain.id))
    vars = cursor.fetchall()
    for var in vars:
      hostvars.append({var[0]:var[1]})
    return hostvars

  def get_group_children(self,group):
    '''Get group children'''
    cursor = self.db.cursor()
    cursor.execute("SELECT child_group FROM ans_child_group_members WHERE ans_group = '{0}' AND domain = '{1}'".format(group.id,self.domain.id))
    for child in cursor.fetchall():
      groupName = self.get_group_by_id(child[0])
      group.addChildren(groupName)

    return group

  def get_host_by_name(self,name):
    cursor = self.db.cursor()
    cursor.execute("SELECT rowid,name FROM hosts WHERE name = '{0}' AND domain = '{1}'".format(name,self.domain.id))
    hostValue = cursor.fetchone()
    if hostValue != None:
      host = Host(hostValue[1],hostValue[0])
      #get host vars
      hostvars = self.get_host_vars(hostValue[0])
      for hostvar in hostvars:
        key = hostvar.keys()[0]
        host.addVar(key,hostvar[key])
      return host
    else:
      return {}

  def get_host_by_id(self,hostid):
    cursor = self.db.cursor()
    cursor.execute("SELECT rowid,name FROM hosts WHERE rowid = '{0}' AND domain = '{1}'".format(hostid,self.domain.id))
    hostValue = cursor.fetchone()
    host = Host(hostValue[1],hostValue[0])
    #get host vars
    hostvars = self.get_host_vars(hostValue[0])
    for hostvar in hostvars:
      key = hostvar.keys()[0]
      host.addVar(key,hostvar[key])
    return host

  def get_group_by_id(self,groupid):
    cursor = self.db.cursor()
    cursor.execute("SELECT name FROM ans_groups WHERE rowid = '%d'" % groupid)
    return cursor.fetchone()[0]

  def get_hosts_by_domain(self):
    cursor = self.db.cursor()
    cursor.execute("SELECT rowid,name FROM hosts WHERE domain = '%d'" % self.domain.id)
    return cursor.fetchall()

  '''Inventory methods'''
  def _empty_inventory(self):
    '''Generate an empty inventory'''
    base_inventory = {}
    base_inventory["_meta"] = {}
    base_inventory["_meta"]["hostvars"] = {}
    return base_inventory

  def build_meta_hostvars(self):
    '''Generate _meta hostvars from gathered data'''
    if len(self.hosts) > 0:
      for host in self.hosts:
        if host.getVarsCount() > 0:
          self.inventory["_meta"]["hostvars"][host.name] = host.vars

  def get_host_info(self):
    self.get_domain_id(self.domain_name)
    host = self.get_host_by_name(self.args.host)
    hostVarsList = self.get_host_vars(host.id)
    hostVars = {}
    for dict in hostVarsList:
      hostVars.update(dict)
    return hostVars

  def get_inventory(self):
    '''Generate an inventory by group'''
    self.get_domain_id(self.domain_name)
    self.groups = self.get_groups_by_domain()
    for idx,group in enumerate(self.groups):
      updatedGroup = self.get_group_members(group)
      updatedGroup = self.get_group_vars(updatedGroup)
      updatedGroup = self.get_group_children(updatedGroup)
      self.groups[idx] = updatedGroup

    return self.groups

  def parse_cli_args(self):
    ''' Command Line Argument Parser'''
    parser = argparse.ArgumentParser(description='Generate an Ansible Inventory File')
    parser.add_argument('--list',action='store_true',default=True,help='List hosts (default; True)')
    parser.add_argument('--host',action='store',help='Get all the variables about a specific instance')
    parser.add_argument('--db',action='store',help='Specify db location')
    #add default location for the db /etc/ansible/hosts.sqlite3
    self.args = parser.parse_args()

  def __init__(self):
    '''Main'''

    #Start with an empty inventory
    self.inventory = None
    self.domain_name = os.environ.get('DOIT_DOMAIN')
    self.domain = Domain()
    self.groups = []
    self.hosts = []

    self.parse_cli_args()
    self.open_database()

    if self.args.host:
      data_output = self.get_host_info()
      self.inventory = data_output
    elif self.args.list:
      self.inventory = self._empty_inventory()
      data_output = self.get_inventory()
      for group in data_output:
        #this fixes the issue if a group exists within a domain but it doesn't have hosts
        self.inventory.update(group.toDict())

      self.build_meta_hostvars()
      
    if self.inventory == None:
      print {}
    else:
      print json.dumps(self.inventory)

DOIT()