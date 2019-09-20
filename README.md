# The platt backend #

This program displays the results of finite element simulations in a web
browser. The data is hosted on a ceph cluster and provided by the
[platt-ceph-gateway](https://github.com/Klump3n/platt-ceph-gateway).


## Requirements ##

This program relies on the CherryPy web server and the WebSocket4py packages
(`conda install cherrypy ws4py`).

To obtain data to be displayed it relies on a running running
[platt-ceph-gateway](https://github.com/Klump3n/platt-ceph-gateway). This in
turn requires a properly set up Ceph storage.

To build the documentation you will also need `sphinx` and `sphinx-js`. The
latter is not available via conda but must be pulled via pip, `pip install
sphinx-js`. `sphinx` will be pulled as a dependency.


## Client ##

Loading of displayed simulations is done via the command line utility.

TODO: Commands.


## Backend ##

The `backend/` directory contains the Python3 code for starting the web server
and doing things with the downloaded data from the gateway.


## Frontend ##

The `frontend/` directory contains the part of the project that is being handled
by the web browser. Warning: HTTPS is not being used. This is intended for use
in a closed environment with no exposition to the internet. If you would like to
use it online, it would be wise to add support for HTTPS. The `cherrypy` web
server should support it.

JavaScript

Documentation


## Use in conjunction with the `platt-ceph-gateway` ##


### Data format ###

Pool
Namespace
Binary files
Sha1Sum


## Classification of data ##

There are several types of data that can be processed.

Geometry data (the mesh)
Field data (data on the mesh).


## Mesh types supported ##

TODO: add system matrix calculator to some contrib folder.


## Not actively maintained ##

A warning: this project is not being actively maintained. If you would like to
do so, please fork this repository.
