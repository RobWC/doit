#!/usr/bin/python

from flask import Flask, render_template, request, Response, url_for, make_response

import argparse
import sqlite3
import os
import sys
import json
sys.path.append('/home/rcameron/code/doit')

#import doit core
from doit import DOIT
from doit import Group

if __name__ == '__main__':

  parser = argparse.ArgumentParser(description='Generate an Ansible Inventory File')
  parser.add_argument('--db',action='store',help='Specify db location')
  args = parser.parse_args()

  myDoit = DOIT()

  app = Flask(__name__, static_url_path='')
  app.debug = True

  @app.route('/')
  def index():    # Get domain count
    myDoit = DOIT()
    typeCounts = {'domains':0,'groups':0,'hosts':0}
    typeCounts['domains'] = myDoit.get_domain_count()
    typeCounts['groups'] = len(myDoit.get_groups_by_domain())
    typeCounts['hosts'] = len(myDoit.get_hosts_by_domain())
    return render_template('dashboard.j2', title="Dashboard",typeCounts=typeCounts)

  @app.route('/domains')
  def domains():
    myDoit = DOIT()
    domainList = myDoit.get_domain_list()
    return render_template('domains.j2',title="Domains",domainList=domainList)

  @app.route('/hosts')
  def hosts():
    myDoit = DOIT()
    hostList = myDoit.get_hosts_with_domain_name()
    return render_template('hosts.j2',title="Hosts",hostList=hostList)

  @app.route('/groups')
  def groups():
    myDoit = DOIT()
    groupList = myDoit.get_groups_with_domain_name()
    return render_template('groups.j2',title="Groups",groupList=groupList)

  @app.route('/group_vars')
  def group_vars():
    myDoit = DOIT()
    groupList = myDoit.get_groups_with_domain_name()
    return render_template('group_vars.j2',title="Group Variables",groupList=groupList)

  @app.route('/group_vars/<group>/list')
  def group_vars_by_group(group):
    myDoit = DOIT()
    groupId = myDoit.get_group_by_name(group)
    groupObj = Group(group,groupId)
    groupObj = myDoit.get_group_vars(groupObj)
    try:
      groupVars = groupObj.toDict()[group]['vars']
    except KeyError:
      groupVars = {}

    title = "{0} Variables".format(group)
    return render_template('group_vars_list.j2',title=title,groupVars=groupVars)

  '''
  API for DOIT

  Types:
  -------
  host
  group
  domain
  group_var

  Actions:
  ---------
  create - Creates new object of specified type [POST]
  delete - Deletes existing object of specified type [DELETE]
  update - Updates existing object of specified type [PUT]
  list - List all data for existing object [GET]

  Return Values:
  ---------------
  All returned values must be correctly formatted JSON

  ????
  {
    status: 'OK', #OK, Error
    message: '',
    type: '', #data type returned
    data: {} #returned data object
  }

  '''
  @app.route('/api/<type>/<name>/<action>', methods = ['POST','DELETE','PUT','GET'])
  def api(type,name,action):
    reqMethod = request.method
    response = Response()
    #contentType = request.headers['content-type']
    a = None
    b = None
    value = "foo"
    myDoit = DOIT()
    #content = request.json['content']
    if type == 'host':
      #handle host requests
      if action == 'create' and reqMethod == 'POST':
        response.data = json.dumps(myDoit.add_host(name).toDict())
      elif action == 'delete' and reqMethod == 'DELETE':
        response.data = json.dumps(myDoit.delete_host_by_name(name).toDict())
      elif action == 'update' and reqMethod == 'PUT':
        response.data = json.dumps(myDoit.update_host_by_name().toDict())
      elif action == 'list' and reqMethod == 'GET':
        response.data = json.dumps(myDoit.get_host_by_name(name).toDict())
      else:
        print "Invalid action"
    elif type == 'group':
      #handle group requests
      a = 1
    elif type == 'domain':
      #handle domain requests
      a = 1
    elif type == 'group_var':
      #handle group_var requests
      a = 1
    else:
      a = None

    print a
    print b
    response.headers['Content-Type'] = 'application/json'
    return response
    #return make_response(json.dumps(value.toDict()))

  app.run(host="0.0.0.0",port=int("12345"))
