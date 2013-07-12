:title: S3 Server
:description: Describes the use of the S3 Server
:keywords: etl, concepts, explanation, amazon, s3

.. _s3_server_def:

S3 Server
=================

Provides a method for interpreting data in Amazon S3 as if it were tables.
Data can be encoded in both the key and blobs.


S3 itself is a simple Key/Value store. It simply stores
a blob of data associated with a unique name. It makes
no attempt to interpret the data and the only quering 
capabilities it provides is listing keys and fetching 
specific blobs. Consequently if you need to interpret
a blob you need to fetch it's contents over the network
and interpret it locally.

The S3 server has cap

It's capabale of storing
millions of records, but it makes no attempt to interpret the
data stored in the value. That's typically an excercise left
to the 
