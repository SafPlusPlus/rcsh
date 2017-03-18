===============================
rcsh
===============================


.. image:: https://img.shields.io/pypi/v/rcsh.svg
        :target: https://pypi.python.org/pypi/rcsh

.. image:: https://img.shields.io/travis/SafPlusPlus/rcsh.svg
        :target: https://travis-ci.org/SafPlusPlus/rcsh

.. image:: https://readthedocs.org/projects/rcsh/badge/?version=latest
        :target: https://rcsh.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status

.. image:: https://pyup.io/repos/github/SafPlusPlus/rcsh/shield.svg
     :target: https://pyup.io/repos/github/SafPlusPlus/rcsh/
     :alt: Updates

.. image:: https://codecov.io/gh/SafPlusPlus/rcsh/branch/master/graph/badge.svg
  :target: https://codecov.io/gh/SafPlusPlus/rcsh

Non-interactive command whitelisted shell

This is a work-in-progress little script intended to be used as a shell for Linux user accounts which are allowed to run
a limited set of commands over SSH non-interactively and nothing else. The command which are allowed are based on a
whitelist of exact command invocation strings and/or a list of regular expressions which they should match.


* Free software: BSD license
* Documentation: https://rcsh.readthedocs.io. (no documentation yet, please stand by...)


Features
--------

* Allow execution of commands based on an exact or regular expression whitelist
* Log invocation using syslog's LOG_AUTH facilities

Credits
---------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage

