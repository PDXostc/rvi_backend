Copyright (C) 2014, Jaguar Land Rover

This document is licensed under Creative Commons
Attribution-ShareAlike 4.0 International.


RVI BACKEND (RVI-BE) 0.1
========================

This document is an overview of the RVI Backend (RVI-BE) project. RVI-BE is a
database-backed web environment to interact with vehicles
(or any device for that matter) via the RVI middleware framework. For
details on RVI consult the documentation in the
[RVI](https://github.com/PDXostc/rvi) respository.


DESCRIPTION
-----------

RVI-BE consists of two components:

* [Web](https://github.com/PDXostc/rvibackend/tree/master/web)
* [Server](https://github.com/PDXostc/rvibackend/tree/master/server)

*Web* is a web interface with database backend built using the 
[Django](https://www.djangoproject.com) framework.

*Server* is a daemon process that receives and processes asynchronous
messages received via RVI from vehicles and other devices.


READER ASSUMPTIONS
------------------

To successfully install and utilize RVI-BE you are assumed to:

1. Know how to use a system running a mainstream Linux distribution such
as Debian, Fedora, OpenSuse, Ubuntu.

2. Know how to install software packages on your system using your
distribution's package management system e.g. apt-get, rpm, yum, zypper.

3. Have a basic understanding of Linux directory structures, how to
create new directories, create and edit files.


PREREQUISITES
-------------

1. To check out the RVI-BE code you will need to have the Git SCM installed on
your system.

2. Python v2.7 must be installed on your system. Python v3 or greater may
work, however we have not yet tested it at this point. Virtually any mainstream
Linux distribution installs Python by default.

3. RVI-BE requires additional Python packages that may not be installed by
default. We use pip to install these packages. You may need to install pip on
your system:

Fedora:
    sudo yum install python-pip

OpenSuse:
    sudo zypper install python-pip
    
Debian/Ubuntu:
    sudo apt-get install python-pip    
    
