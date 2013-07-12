:title: Welcome to Documentation for Splicer
:description: An overview of the Splicer Documentation
:keywords: relational algebra, etl, databases, concepts, explanation

.. _introduction:

.. note:

  This documentation covers the initial release of Splicer. There
  are some forward looknig feature descriptions in this documentation
  that at the time of this writing may not be completely implmeneted.
  Hopefully this situation does not last long, in any event if something
  described herein does not work or seems confusing we'd love to hear
  form you!
  

Welcome
=======

``splicer``, the In Place Data Querying Library, is a python module
for working with data from disparate sources using commands to those
familliar with SQL. It aims to make quick one off queries and
:ref:`etl_def` scripts more declarative rather than procedural.


``splicer`` enables:

* Analysts to create :ref:`dataset_def` linking various
  foreign tables together along with :ref:`udf_def`. Once defind the
  datasets can be queried via SQL Select statements to create new Views
  of the Data.

* Extension Developers to create extensions that make various data sources
  REST endpoints, log files, NoSQL Servers, traditional Databases,
  CSV Files to behave like tables.

  ``splicer`` will take advanatage of these various sources capabilities where 
  appropiate and will compensate for sources that lack basic
  features. 

  For example if a database supports joins and you want to query
  two tables within that database, ``splicer`` will have that system
  perform the join for you. If however the your worknig with a less
  sophisticated source, like a plain files, ``splicer`` will perform the
  operations for you locally.


Enough reading! :ref:`Try it out! <installation>`
