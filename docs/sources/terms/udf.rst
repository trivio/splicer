:title: User Defined Functions (UDF)
:description: Definitions of a Datasect
:keywords: user defined functions, udf, concepts, explanation

.. _udf_def:

User Defined Functions (UDF)
============================

`splicer` provides sever functions for manipulating data
while querying it. In addition you can write your own
procedures in python to use in your queries. These are
known as User Defined Functions.


`splicer` provides 3 kinds

* Column functions for transforming values of a row during querying.

* Aggregate functions for summarizing row data using the group by clause

* Relational functinos for producing a set of rows that can be used as if
  it were another relation (table or view) in a FROM clause.