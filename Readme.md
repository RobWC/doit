DOIT - DevOps Inventory Technician
----------------------------------

The DOIT tool is used as a system to store both metadata and files about hosts in a network. It can be integrated with systems such as ansible to provide inventory of hosts for automation purposes.

DOIT is a simple RESTful based API system to store,fetch,update and delete information about hosts. Authentication is done using a generated api key. The API key is included in the API call. 


Documentation:
---------------------------------

Storing information about a host:
--------------------------------
All hosts are keyed off of a unique hostname. This hostname should be the complete fqdn as this is typical within an environment. You are also able to add alias names to hosts for secondary interfaces. 

Within DOIT any information can be stored in a key/pair value. This keeps it easy and flexible to manage the scehma within DOIT. Fields can be added and omitted at will. The only base requirement is the use of the hostname for discussing hosts, sitename for discussing sites, or any other top level container. 


Create item:
------------

POST
/<type>/<name>?api=<key>
Content-Type: application/json
{metadata:{key:"value"}}

Update item:
------------

PUT
/<type>/<name>?api=<key>
Content-Type: application/json
{metadata:{key:"value"}}

Delete item:
------------

Deletes item Completely
DELETE
/<type>/<name>?api=<key>
content-type: application/json
{delete:true}

Deletes item data
DELETE
/<type>/<name>?api=<key>
content-type: application/json
{metadata:{key:{delete:true}}}

Deletes all item data
DELETE
/<type>/<name>?api=<key>
content-type: application/json
{metadata:{delete:true}}

Retreiving Data:
----------------------------

The power of DOIT is to be able to retrieve data back in a consumeable format for your application. This works perticularly well as an inventory system as you can easily group like systems together.

Get an item:
-----------
GET
/<type>/<name>?api=<key>
Returns all data as json

Get specific infomation on an item:
-----------------------------------
GET
/<type>/<name>?api=<key>
Content-Type: application/json
{metadata:{key:true}}}
Returns only the value of the keys

Return the complete inventory list:
GET
/inventory?api=<key>
Returns ansible json format

Return status codes:
---------------------
- 200 Action Success
- 304 No update made
- 401 unauthoried: Api key is invalid
- 404 object not found
- 500 error processing request
