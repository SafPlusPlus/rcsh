=====
Usage
=====

After adding rcsh as the shell of a user account you can whitelist commands for that user by editing the following
files:

* ``/etc/rcsh.d/<username>.exact``
* ``/etc/rcsh.d/<username>.regex``

Exact whitelist
===============

Every line in ``/etc/rcsh.d/<username>.exact`` represents a command which this user is allowed to execute over ssh.

Regular expression whitelist
============================

Every line in ``/etc/rcsh.d/<username>.regex`` must be a valid Python regular expression and must start with '^' and end
with '$'. If the user tried to execute a command which matches one of these, it will be allowed.