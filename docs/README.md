Splicer documentation and website
=================================

Documentation
-------------
This is your definite place to contribute to the splicer documentation. 
The documentation is generated from the .rst files under sources. 

Basic document structure, build files and a tad bit of content (such
as these instructinos for contributing to the documentation) have 
been lifted from the excellent docker project (http://docker.io). 
If you notice any similarities, it's more than coincidental. Splicer
owes Dotcloude and Docker contributers a big thanks for developing 
such a great structure for documenting.



Installation
------------

* Work in your own fork of the code, we accept pull requests.
* Install sphinx: `pip install sphinx`
    * Mac OS X: `[sudo] pip-2.7 install sphinx`)
* Install sphinx httpdomain contrib package: `pip install sphinxcontrib-httpdomain`
    * Mac OS X: `[sudo] pip-2.7 install sphinxcontrib-httpdomain`
* If pip is not available you can probably install it using your favorite package manager as **python-pip**

Usage
-----
* Change the `.rst` files with your favorite editor to your liking.
* Run `make docs` to clean up old files and generate new ones.
* Your static website can now be found in the `_build` directory.
* To preview what you have generated run `make server` and open <http://localhost:8000/> in your favorite browser.

Working using GitHub's file editor
----------------------------------
Alternatively, for small changes and typo's you might want to use GitHub's
built in file editor. It allows you to preview your changes right online. 
Just be carefull not to create many commits.

Images
------
When you need to add images, try to make them as small as possible (e.g. as gif).


Notes
-----
* The index.html and gettingstarted.html files are copied from the source dir to the output dir without modification.
So changes to those pages should be made directly in html
* For the template the css is compiled from less. When changes are needed they can be compiled using
lessc ``lessc main.less`` or watched using watch-lessc ``watch-lessc -i main.less -o main.css``


Guides on using sphinx
----------------------
* To make links to certain pages create a link target like so:

  ```
    .. _hello_world:

    Hello world
    ===========

    This is.. (etc.)
  ```

  The ``_hello_world:`` will make it possible to link to this position (page and marker) from all other pages.

* Notes, warnings and alarms

  ```
    # a note (use when something is important)
    .. note::

    # a warning (orange)
    .. warning::

    # danger (red, use sparsely)
    .. danger::

* Code examples

  Start without $, so it's easy to copy and paste.
