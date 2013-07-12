:title: Creating Views
:description: Instructions for Creating Views
:keywords: 

.. _creating_views:

Creating Views
==============

.. code-block:: python

  dataset.create_view(
    'billing',
    '''
      SELECT DISTINCT dt, customer_id
      FROM 's3://mybucket/myfoo/'
    '''
  )
