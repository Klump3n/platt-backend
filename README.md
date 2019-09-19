# The platt backend #

This program displays the results of finite element simulations in a web
browser. The data is hosted on a ceph cluster and provided by the
[platt-ceph-gateway](https://github.com/Klump3n/platt-ceph-gateway).


### OLD ###

If you want to check out another version of the program (because you might need
to do so for combatibility reasons):

You have a version of the server runnning, i.e. FemGL v1alpha-4-g5e98ffb -- then
all you need to do is take the last part of the version number, in this case
g5e98ffb, ignore the leading 'g' (which stands for git) and you are left with
5e98ffb.
Now to get to this version, type

git checkout 5e98ffb

and you are on a compatible version.

Package requirements are:

cherrypy
sphinx -- for server documentation
sphinx-js -- for js documentation

