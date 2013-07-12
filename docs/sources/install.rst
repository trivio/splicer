:title: Splicer Installation
:description: 
:keywords: installation

.. _installation:

Installation
============

Splicer and it's add-ons are distributed via PyPI Python's package
index. The simpelest way to install splicer is to use a command
like pip.

.. code-block:: bash

  $ pip install splicer splicer_console

One of the main motivatinos of splicer is to make sharing data analysis 
and ETL scripts easy between individuals. Therefore we recomend you setup
your project in a manner similar to modern python web apps.

Assuming you have git, pip and virtualenv installed this is how you would
typically setup a project to use Splicer and it's add-ons.


.. code-block:: bash

  $ mkdir myproject
  $ cd myproject
  $ git init
  $ cat > .gitignore <<-EOF
  bin/
  include/
  lib/
  *.py[co]
  EOF

  $ virtualenv .
  $ source bin/activate
  $ cat > requirements.txt <<-EOF
  splicer>=0.1.0
  splicer_console>=0.1.0
  $ pip install -r requirments.txt

Then create a python script similar to one described in :ref:`the_basics` and
publish this git repository the way you normally would (via github etc...)

If you're a member of the team then working a splicer project would look something
like this.

.. code-block:: bash

  $ git clone git@github.com:<your org>/myproject.git
  $ cd myproject
  $ virtualenv .
  $ source bin/activate
  $ pip install -r requirments.txt
  $ python ./project.py


That's all you need to install splicer form scratch or get some one elses project
up and running, so why not learn how to set up a dataset and query it in
:ref:`the_basics`