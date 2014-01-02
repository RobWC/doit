#!/usr/bin/env python

'''
DevOps Inventory Technician (DOIT)
===================================================

DOIT is a simple dynamic inventory service designed to work exclusively with ansible 
'''

import sys
import os
import argparse
import sqlite3
import json

class Domain(object):
  def __init__(self,name):
    self.id = 0
    self.name = name
  def toDict(self):
    returnDict = {'name':self.name,'id':self.id}
    return returnDict

class Var(object):
  def __init__(self,name,value,type):
    self.name = name
    self.value = value
    self.domain = 0
    self.id = 0
    self.type = type # host,group,role
  def toDict(self):
    returnDict = dict({'name':self.name,'value':self.value,'id':self.id,'type':self.type})
    return returnDict

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
    returnDict = {'name':self.name,'id':self.id}

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
  def addVar(self,name,value,id):
    self.vars[name] = value
  def addChildren(self,name):
    self.children.append(name)
  def toAnsible(self):
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

  def get_domain_list(self):
    cursor = self.db.cursor()
    cursor.execute("SELECT name,rowid FROM domains")
    result = cursor.fetchall()
    return result

  def get_domain_count(self):
    cursor = self.db.cursor()
    cursor.execute("SELECT count(name) FROM domains")
    result = cursor.fetchone()
    return result[0]

  def get_domain_by_name(self,name):
    cursor = self.db.cursor()
    cursor.execute("SELECT rowid,name FROM domains WHERE name = '{0}'".format(name))
    domainValue = cursor.fetchone()
    if domainValue != None:
      domain = Domain(domainValue[1])
      domain.id = domainValue[0]
      #get host vars
      return domain
    else:
      domain = Domain('')
      return domain

  def delete_domain_by_name(self,name):
    cursor = self.db.cursor()
    cursor.execute("SELECT rowid,name FROM domains WHERE name = '{0}'".format(name))
    domainValue = cursor.fetchone()
    if domainValue != None:
      domain = Domain(domainValue[1])
      domain.id = domainValue[0]
      #TODO delete all associated objects???????
      cursor.execute("DELETE FROM domains WHERE name = '{0}'".format(name,self.domain.id))
      self.db.commit()
      domain = Domain('')
      return domain
    else:
      domain = Domain('')
      return domain

  def get_domain_id(self,name):
    cursor = self.db.cursor()
    cursor.execute("SELECT rowid,name FROM domains WHERE name = '%s'" % name)
    result = cursor.fetchone()
    
    #Check that domain exists
    if (result is not None and result[0] is not None and result[1] is not None):
      self.domain.name = result[1]
      self.domain.id = result[0]
    else: 
      self.domain.name = name
      self.domain.id = 0

  def add_domain(self,name):
    cursor = self.db.cursor()
    #check if host name exists
    domainCheck  = self.get_domain_by_name(name)
    if domainCheck.id == 0:
      #host does not exist
      cursor.execute("INSERT INTO domains (name) VALUES ('{0}')".format(name))
      self.db.commit()
      domain  = self.get_domain_by_name(name)
    else:
      #host already exists
      domain = domainCheck

    return domain

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

  def get_groups_by_domain_list(self):
    '''Returns an array of Group objects that belong to the active domain'''
    cursor = self.db.cursor()
    cursor.execute("SELECT rowid,name FROM ans_groups WHERE domain = '%d'" % self.domain.id)
    group_list = []
    for group in cursor.fetchall():
      groupID = group[0]
      groupName = group[1]
      group_list.append([groupID,groupName])

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
    cursor.execute("SELECT name,value,rowid FROM ans_group_vars WHERE ans_group = '{0}' AND domain = '{1}'".format(group.id,self.domain.id))
    for groupVar in cursor.fetchall():
      group.addVar(groupVar[0],groupVar[1],groupVar[2])

    return group

  def delete_group_host(self,host):
    '''Delete group host vars'''
    cursor = self.db.cursor()
    cursor.execute("DELETE FROM ans_host_group_members WHERE host = '{0}' AND domain = '{1}'".format(host.id,self.domain.id))
    self.db.commit()
    vars = cursor.fetchall()
    return vars

  def delete_group_vars(self,group):
    '''Delete group vars'''
    cursor = self.db.cursor()
    cursor.execute("DELETE FROM ans_group_vars WHERE ans_group = '{0}' AND domain = '{1}'".format(group.id,self.domain.id))
    self.db.commit()
    vars = cursor.fetchall()
    return vars

  def delete_child_group_members(self,group):
    '''Delete group vars'''
    cursor = self.db.cursor()
    cursor.execute("DELETE FROM ans_child_group_members WHERE ans_group = '{0}' AND domain = '{1}'".format(group.id,self.domain.id))
    self.db.commit()
    vars = cursor.fetchall()
    return vars

  def delete_host_vars(self,host):
    '''Delete host vars'''
    cursor = self.db.cursor()
    cursor.execute("DELETE FROM host_vars WHERE host = '{0}' AND domain = '{1}'".format(host.id,self.domain.id))
    self.db.commit()
    vars = cursor.fetchall()
    return vars

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

  def add_group(self,name):
    cursor = self.db.cursor()
    #check if host name exists
    groupCheck  = self.get_group_by_name(name)
    if groupCheck.id == 0:
      #host does not exist
      cursor.execute("INSERT INTO ans_groups (name,domain) VALUES ('{0}',{1})".format(name,self.domain.id))
      self.db.commit()
      group  = self.get_group_by_name(name)
    else:
      #host already exists
      group = groupCheck

    return group

  def add_group_var(self,name,value,group_name):
    group = self.get_group_by_name(group_name)
    cursor = self.db.cursor()
    #check if host name exists
    groupVarCheck  = self.get_group_var_by_name(name,group)
    if groupVarCheck.id == 0:
      #host does not exist
      cursor.execute("INSERT INTO ans_group_vars (name,value,ans_group,domain) VALUES ('{0}','{1}','{2}','{3}')".format(name,value,group.id,self.domain.id))
      self.db.commit()
      groupVar  = self.get_group_var_by_name(name, group)
    else:
      #host already exists
      groupVar = groupVarCheck

    return groupVar

  def delete_group_var(self,name,group_name):
    group = self.get_group_by_name(group_name)
    cursor = self.db.cursor()
    #check if host name exists
    groupVarCheck  = self.get_group_var_by_name(name,group)
    if groupVarCheck.id == 0:
      #host does not exist
      cursor.execute("DELETE FROM ans_group_vars WHERE name = '{0}' AND domain = '{1}' AND ans_group = '{2}'".format(name,self.domain.id,group.id))
      self.db.commit()
      groupVar  = self.get_group_var_by_name(name, group)
    else:
      #host already exists
      groupVar = groupVarCheck

    return groupVar

  def add_host(self,name):
    cursor = self.db.cursor()
    #check if host name exists
    hostCheck  = self.get_host_by_name(name)
    if hostCheck.id == 0:
      #host does not exist
      cursor.execute("INSERT INTO hosts (name,domain) VALUES ('{0}',{1})".format(name,self.domain.id))
      self.db.commit()
      host  = self.get_host_by_name(name)
    else:
      #host already exists
      host = hostCheck

    return host

  def delete_group_by_name(self,name):
    cursor = self.db.cursor()
    cursor.execute("SELECT rowid,name FROM ans_groups WHERE name = '{0}' AND domain = '{1}'".format(name,self.domain.id))
    groupValue = cursor.fetchone()
    if groupValue != None:
      # host exists delete and forgien key rows
      group = Group(groupValue[1],groupValue[0])
      #delete host vars
      self.delete_group_vars(group)
      self.delete_child_group_members(group)
      cursor.execute("DELETE FROM ans_groups WHERE name = '{0}' AND domain = '{1}'".format(name,self.domain.id))
      self.db.commit()
      group = Group('',0)
      return group
    else:
      #host doesnt exist
      group = Group('',0)
      return group
    
  def delete_host_by_name(self,name):
    cursor = self.db.cursor()
    cursor.execute("SELECT rowid,name FROM hosts WHERE name = '{0}' AND domain = '{1}'".format(name,self.domain.id))
    hostValue = cursor.fetchone()
    if hostValue != None:
      # host exists delete and forgien key rows
      host = Host(hostValue[1],hostValue[0])
      #delete host vars
      self.delete_host_vars(host)
      self.delete_group_host(host)
      cursor.execute("DELETE FROM hosts WHERE name = '{0}' AND domain = '{1}'".format(name,self.domain.id))
      self.db.commit()
      host = Host('',0)
      return host
    else:
      #host doesnt exist
      host = Host('',0)
      return host

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
      host = Host('',0)
      return host

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

  def get_group_by_name(self,groupname):
    cursor = self.db.cursor()
    cursor.execute("SELECT rowid,name FROM ans_groups WHERE name = '{0}' AND domain = '{1}'".format(groupname,self.domain.id))
    groupValue = cursor.fetchone()
    print groupValue
    if groupValue != None:
      group = Group(groupValue[1],groupValue[0])
    else:
      group = Group('',0)
      
    return group

  def get_group_var_by_name(self,name,group):
    cursor = self.db.cursor()
    cursor.execute("SELECT rowid,name,value FROM ans_group_vars WHERE ans_group = '{0}' AND domain = '{1}' AND name = '{2}'".format(group.id,self.domain.id,name))
    groupVarValue = cursor.fetchone()
    if groupVarValue != None:  #def __init__(self,name,value,type):
      groupVar = Var(groupVarValue[1],groupVarValue[0],'')
    else:
      groupVar = Var('',0,'')
      
    return groupVar

  def get_group_by_id(self,groupid):
    cursor = self.db.cursor()
    cursor.execute("SELECT name FROM ans_groups WHERE rowid = '%d'" % groupid)
    return cursor.fetchone()[0]

  def get_groups_with_domain_name(self):
    cursor = self.db.cursor()
    cursor.execute("SELECT ans_groups.name,ans_groups.rowid,domains.name,domains.rowid FROM ans_groups INNER JOIN domains ON ans_groups.domain = domains.rowid")
    return cursor.fetchall()

  def get_hosts_with_domain_name(self):
    cursor = self.db.cursor()
    cursor.execute("SELECT hosts.name,hosts.rowid,domains.name,domains.rowid FROM hosts INNER JOIN domains ON hosts.domain = domains.rowid")
    return cursor.fetchall()

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

  def get_host_info(self,name):
    self.get_domain_id(self.domain_name)
    host = self.get_host_by_name(name)
    hostVarsList = self.get_host_vars(host.id)
    hostVars = {}
    for dict in hostVarsList:
      hostVars.update(dict)
    return hostVars

  def get_inventory(self):
    '''Generate an inventory by group'''
    self.inventory = self._empty_inventory()
    self.get_domain_id(self.domain_name)
    self.groups = self.get_groups_by_domain()
    for idx,group in enumerate(self.groups):
      updatedGroup = self.get_group_members(group)
      updatedGroup = self.get_group_vars(updatedGroup)
      updatedGroup = self.get_group_children(updatedGroup)
      self.groups[idx] = updatedGroup

    for group in self.groups:
      self.inventory.update(group.toDict())

    return self.inventory

  def parse_cli_args(self):
    ''' Command Line Argument Parser'''
    parser = argparse.ArgumentParser(description='Generate an Ansible Inventory File')
    parser.add_argument('--db',action='store',help='Specify db location')
    #add default location for the db /etc/ansible/hosts.db
    self.args = parser.parse_args()

  def __init__(self,domain):
    '''Main'''
    #Start with an empty inventory
    self.inventory = None

    self.parse_cli_args()
    self.open_database()
    self.domain_name = domain.name
    self.domain = domain
    self.get_domain_id(self.domain_name)
    self.domain = domain
    self.groups = []
    self.hosts = []