.. TBD documentation master file, created by
   sphinx-quickstart on Mon Aug 28 16:02:33 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to TBD's documentation!
===============================

This is a program to display simulation data from finite difference calculations.

Usage
=====

Call ``main.py -h`` for a little help.

With the provided example data in the programs main directory, a viable command
would be ``main.py -d example_data``. This would start the backend, which in
turn would look for simulation data in the directory ``example_data``. A web
server would also be started. This we could reach at ``http://localhost:8008``.

Contents
========

.. toctree::
   :maxdepth: 2
   :caption: Packages and modules:

   main
   backend
   frontend

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. js:autofunction:: grabCanvas
