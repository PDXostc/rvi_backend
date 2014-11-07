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

### General Prerequisites

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
    

### Database Installation

RVI-BE requires a database. Django supports SQLite, MySQL, PostgreSQL and Oracle.
Since the RVI-BE does a lot of writing to the database we recommend that you use
a database server rather than SQLite. We use MySQL (or MariaDB) for our testing.
[MariaDB](https://www.mariadb.com) is the community-developed fork of the
[MySQL](http://www.mysql.com) database. It is a drop-in replacement for MySQL.
All mainstream Linux distributions now include MariaDB in their package
repositories rather than MySQL. Many distributions install the MariaDB server by
default. To check if MariaDB is already installed on your system:

Fedora:

    yum list installed | grep mariadb
    
OpenSuse:

    zypper se 'mariadb*'
    
Debian/Ubuntu:

    dpkg --get-selections | grep mariadb
    
If the previous does not yield any output on your system you will need to install
the MariaDB database server:

Fedora:

    sudo yum install mariadb

OpenSuse:

    sudo zypper in mariadb

Debian/Ubuntu:

    sudo apt-get install mariadb
    
To access MySQL databases an API driver is required. There are several options. We
are using [MySQL Connector/Python](http://dev.mysql.com/downloads/connector/python)
which is a pure Python driver from Oracle that does not require the MySQL client
library or any other Python modules outside the standard Python libraries. The
mainstream distributions include this driver in their package repositories:

Fedora:

    sudo yum install mysql-connector-python
    
OpenSuse:

    sudo zypper in mysql-connector-python
    
Debian/Ubuntu:

    sudo apt-get install mysql-connector-python


### Database Server Startup

After installing the database server you will need to start the MariaDB server
and enable it on system startup.

Fedora/OpenSuse (distributions using systemd):

    sudo systemctl enable mariadb.service
    sudo systemdtl start mariadb.service

Debian/Ubuntu (distributions using SysV Init):

    sudo update-rc.d mysql defaults
    
*Note:* The command above for Debian/Ubuntu uses 'mysql' although the it is the
MariaDB Server that will be started.


### Database Server Setup

Next we need to prepare the database server. For the following steps when we use
the notation *shell>* it means that you will have to enter the command in a Linux
shell. When we use the notation *mysql>* then the command has to be issued from
the MySQL shell typically as *root* user.

*Note:* SQL syntax requires that every command is terminated with a semicolon.

1. Load Timezone Definitions

        shell> mysql_tzinfo_to_sql /usr/share/zoneinfo | mysql -u root mysql
   
1. Set Root Password

        shell> mysql -u root
        mysql> select user, host, password from mysql.user;
        mysql> update mysql.user set password = PASSWORD('newpwd') where user = 'root';
        mysql> flush privileges;
   
2. Remove anonymous accounts

        mysql> drop user ''@'localhost';
        mysql> drop user ''@'hostname';

3. Drop test database

        mysql> drop database test;  
   
4. Create RVI Database

        mysql> create database rvi character set utf8;
   
6. Create User for RVI

        mysql> create user 'rvi_user'@'localhost' identified by 'rvi';
   
8. Grant User All Rights to Database

        mysql> grant all on rvi.* to 'rvi_user'@'localhost';

    
