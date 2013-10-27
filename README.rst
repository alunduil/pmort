Description
===========

A simple local post-mortem analysis logging system.  Saves pertinent information
for after-the-fact troubleshooting.

I would recommend using an actual remote logging and analysis service rather
than this crude utility but in a pinch this utility may get the information
needed to find the root of an issue.

Installation
============

This package is stored in PyPI and can be installed the standard way::
    pip install pmort

The problem with installing pmort this way is the necessity to create your own
daemonizer script (RC script).  Package managers should be preferred as they
will come with the appropriate init system scripts to run this as a daemon.

The latest release available from PyPI is:

.. image:: https://badge.fury.io/py/pmort.png
    :target: http://badge.fury.io/py/pmort

If you prefer to clone this package directly from git or assist with
development, the URL is https://github.com/alunduil/pmort and the current status
of the build is:

.. image:: https://secure.travis-ci.org/alunduil/pmort.png?branch=master
    :target: http://travis-ci.org/alunduil/pmort

Optional Dependencies
---------------------

Some of the non-traditional collectors (shell scripts, &c) require other
programs to be installed and don't work properly without them.  I've
categorized them according to Gentoo USE flags here so only the desired groups
need be installed:

:apache:    apache2ctl
:mysql:     mysqladmin, mysqltuner
:sysstat:   iostat
:net-tools: netstat
:procps     free, ps, uptime, vmstat

Usage
=====

Usage of this package is quite simple, run the pmort executable.  To change the
behaviour of pmort you can check the command line help (--help) or edit the
sample configuration file (located in ``/usr/share/doc/pmort-VERSION/`` by
default).

Authors
=======

* Alex Brandt <alunduil@alunduil.com>

Known Issues
============

Known issues can be found in the github issue list at
https://github.com/alunduil/pmort/issues.

Troubleshooting
===============

If you need to troubleshoot pmort or submit information in a bug report, we
recommend enabling debug logging and submitting and stack traces you recieve
while running the pmort executable by hand (without any daemonizer).
