:title: Basic Commands
:description: Common usage and commands
:keywords: Examples, Usage, basic commands,splicer, documentation, examples

.. _the_basics:

The Basics
==========

`splicer`  blends data from multiple sources together and
lets you query it, as if it were part of one giant,
read only database system. Here's the typical usage pattern.

Start off by creating a python file, in a directory created in
a manner described in :ref:`installation`. Call the file *myproject.py*.

Inside we'll create a :ref:`dataset_def` which holds a collection of
:ref:`Servers <server_def>`,  :ref:`Tables <table_def>`, 
:ref:`Views <view_def>` and :ref:`User Defined Functions <udf_def>`.

Create a DataSet
----------------


Add the following code to import splicer and create a :ref:`dataset_def`.

.. code-block:: python

  import splicer
  dataset = splicer.DataSet()



Add a Server
------------

:ref:`Servers <server_def>` provide  tables and other
relations  to the dataset.  

.. note::
  Since `splicer` is based on Relational
  Algebra  we'll  often  use the name *relation* 
  interchangeablly with *tables* in this doc.

Let's modify the code to add a DictServer which lets us
query a list of dictionaries entirely from memmory. 

.. code-block:: python

  import splicer
  from splicer.servers.dict_server import DictServer

  dataset = splicer.DataSet()


  dataset.add_server(DictServer(
    users = [
      dict(username="tom", customer_id=123, full_name="Tom Talbert", active=True),
      dict(username="sally", customer_id=456, full_name="Sally Sanders", active=False),
      dict(username="marry",customer_id=789, full_name="Marry Mabel", active=True),
      dict(username="john", customer_id=999, full_name="John Jonas", active=False)
    ]
  ))


The arguments to the server class are unique to the
implmentation of each server. For instance
if you were talking to a Postgres server you'd simply pass
in your login credentials. In this case we pass in a keyword
argument 'users' which is a list of dictionaries. This particular
Server will use that data to expose a `relation` named `users`


Query the dataset
-----------------

A quick and dirty way to interact with data is to run your
script using the `python -i` like so:

.. code-block:: bash

  $ python -i myproject.py
  >>> 

This will execute your script and leave you in python's 
interactive interpreter where you can, drum roll please...
interact with your dataset.

We can query using two different forms. The first is to use
the query() method which should be familiar to anyone
who has ever worked with a SQL database. It takes a SQL
select statement and returns a Query object.


.. code-block:: python

  >>> query = dataset.query('select * from users')

Within the interpreter you  introspect the query by simply
typing it's name and hitting enter.

.. code-block:: python

  >>> query
  Relation user:
    username:STRING
    customer_id:123
    full_name:STRING
    active:BOOLEAN

This displays the ref:`schema <schema_def>` of the underlying data that will be returned
when the query is executed. To execute the query simply iterate it.

.. code-block:: python

  >>> for user in query:
  ...   print user.username, user.full_name, user.active

Which produces the following output in your terminal.

.. code-block:: none

  tom     Tom Talbert    True
  sally   Sally Sanders  False
  marry   Mary Mabel     True
  john    John Jonas     False


The second method of querying uses the method chaing style
which is useful for building up a query programtically.


.. code-block:: python

  >>>  for user in dataset.select('*').frm('users'):
  ...    print user.username, user.full_name, user.active

Which produces the same output.


Filtering using a query
-----------------------

`splicer` goal is to provide the full range of declarative power that
you get with a normal SQL select method. Which means you can do things
like filter with where and having clauses, order on columns, group and
so on.

.. code-block:: python

  query = dataset.query('''
  SELECT *
  FROM users
  WHERE active = TRUE
  ''')

  for user in query:
   print user.username, user.full_name, user.active



.. code-block:: none

  tom     Tom Talbert    True
  marry   Mary Mabel     True
 

Or 

.. code-block:: python

  query = dataset.query('''
  SELECT active, count(*)
  FROM users
  GROUP BY active
  ''')

  for active_count in query:
   print active_count.active, active_count.count

.. code-block:: none

  TRUE    2
  FALSE   2


Adding additional tables
------------------------

`splicer` really shines when it's time to work with data in
disparate locations. For example maybe you have some data in an
Amazon S3 Bucket. Using the `splicer` Server for S3 we can access
data as if it were tables.

Thes :ref:`s3_server_def` provides a slew of options for mapping
data in Amazon S3 into tables from either the key names or the
contents of the blob while avoiding costly network round
trips. Look in the server section for more details


Let's pretend we have a bunch of customer specific data
in csv files in S3 like so.


.. code-block:: none

  s3://mybucket/myfoo/dt=2012-05-31/customer_id=123/blob1.csv
  s3://mybucket/myfoo/dt=2012-06-01/customer_id=123/blob2.csv
  s3://mybucket/myfoo/dt=2012-05-31/customer_id=546/blob3.csv


Notice that we've followed the  Hive convention of encoding 
partition information in the key.  For example  We've uploaded
the data by date and customer_id. You'll see that the date is 
incoprorated in the url of thet data as dt=<date stirng> and
customer_id=<number>.

You can then modify your script to setup add an S3 server

.. code-block:: python

  import splicer
  from splicer.servers.dict_server import DictServer
  from splicer_aws import S3

  dataset = splicer.DataSet()

  dataset.add_server(Dictionaries(
    users = [
      dict(username="tom", customer_id=123, full_name="Tom Talbert", active=True),
      dict(username="sally", customer_id=456, full_name="Sally Sanders", active=False),
      dict(username="marry",customer_id=789, full_name="Marry Mabel", active=True),
      dict(username="john", customer_id=999, full_name="John Jonas", active=False)
    ]
  ))

  dataset.add_server(S3(
    access_key="<YOUR AWS KEY>", 
    access_secret="<AWS SECRET>"
  ))

Now you can query your "table"

.. code-block:: python

  query = dataset.query('''
    SELECT DISTINCT dt, customer_id
    FROM 's3://mybucket/myfoo/'
  ''')

  for log in query:
    print log.dt, log.customer_id

Notice we're using the DISTINCT word and only querying on the values
thate were encoded in the urls of the blobs. With that particular 
combination the S3 server is smart enough to return the values
interpreted from the Amazon S3 keys rather than fetching the
entire blobs, which could be a lengthy process especially if
the blobs are large.

Had we not used DISTINCT the S3 server would have been forced to download
each blob interpret it into records and then emmit one (dt, customer_id)
for each record found.

.. note::

  At the time of this writing, the splicer_aws extension has not
  been released. However it should be in the not to distant future.

Creating Views
--------------

Specifying the url for an S3 table in the from clause is a pain
and maybe we want to reuse this query multiple times. `splicer`
provides views for that purpose. Simply call 
dataset.create_view(name, query) like so


.. code-block:: python

  dataset.create_view(
    'billing',
    '''
      SELECT DISTINCT dt, customer_id
      FROM 's3://mybucket/myfoo/'
    '''
  )


Now we can perform queries using the name `billing`

.. code-block:: python

  query = dataset.query('''
    SELECT *
    FROM billing
  ''')


Joining Data
------------

And here's how easy it is to work with data in two seperate tables. 
This query joins users to billing, counts how many customer records
there are.


.. code-block:: python

  query = dataset.query('''
    SELECT full_name, count(dt)
    FROM users join billing on users.customer_id = billing.customer_id
    GROUP BY full_name
  ''')

  for record_counts in query:
    print record_counts.full_name, record_counts.count

.. code-block:: none

  Tom Talbert    2
  Sally Sanders  1

