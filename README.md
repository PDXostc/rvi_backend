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

Verify if the following prerequisites are met by your system:

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
    

INSTALLATION AND SETUP
----------------------

The following steps explain on how to set up the RVI Backend on your system.

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
        
    These are the default user name and password. If you change them you will
    also have to change them in the *mysql.cnf* file (see section on RVI
    Backend Installation).
   
8. Grant User All Rights to Database

        mysql> grant all on rvi.* to 'rvi_user'@'localhost';


### Django Installation

To install Django you need to have *pip* installed on your system as explained
earlier. We are using Django version 1.7.

    sudo pip install django==1.7

Verify installation with:

    python -c "import django; print(django.get_version())"
    
which should print *1.7* to the console.


### RVI Backend Installation

1. Clone the RVI Backend Repository from GitHub

        git clone https://github.com/PDXostc/rvibackend.git rvibackend
    
2. Change into the *rvibackend/web* Directory

        cd rvibackend/web
    
3. Create the Tables for the RVI Backend Database

        python manage.py migrate

    This will access the MariaDB database server. If you set the database up according
    to the above instructions this will work right out of the box. If you did change
    user name and/or password when setting up the database then you will need to modify
    the file *rvibackend/mysql.cnf* accordingly.

4. Create the Admin User for the RVI Backend

        python manage.py createsuperuser
        
5. Start the Development Server

    For development purposes and to test the RVI Backend it is easiest to use
    the built-in web server. Executing
    
        python manage.py runserver
        
    will start the development server listening on *localhost:8000*. The
    development server will perform a couple of system checks, read the settings
    file and then listen to incoming HTTP requests:
    
        Performing system checks...

        System check identified no issues (0 silenced).
        November 07, 2014 - 02:17:21
        Django version 1.7, using settings 'rvi.settings'
        Starting development server at http://127.0.0.1:8000/
        Quit the server with CONTROL-C.
        
    You can now use your web browser and point it to *http://localhost:8000/admin*
    to see the login prompt for the RVI Backend administrative user interface.
    
    
### Start the RVI Backend Server Daemon

Before you can start the RVI Backend Server Daemon you will need to have the RVI
Middleware Server running on your system. Please consult the instructions at
[RVI](https://github.com/PDXostc/rvi) on how to setup and start the server.

The RVI Backend Server Daemon connects to the RVI Middleware Server on the
service edge at *localhost:8801*. If you configured your RVI Middleware Server
to listen to a different host/port you will have to change the setting

    RVI_SERVICE_EDGE_URL = 'http://127.0.0.1:8801'
    
in the file *web/rvi/settings.py*. This file is the common configuration file for
the RVI Backend. After that you can start the RVI Backend Server Daemon in
console or foreground mode with

    python rviserver.py foreground
    
If everything is configured correctly you will see

    INFO RVI Server: Starting...
    INFO RVI Server: Configuration: RVI_SERVICE_EDGE_URL: http://127.0.0.1:8801, RVI_SOTA_CALLBACK_URL: http://127.0.0.1:20001, RVI_SOTA_SERVICE_ID: /sota, RVI_SOTA_CHUNK_SIZE: 65536, MEDIA_ROOT: ../web/../files/
    INFO RVI Server: Starting SOTA Callback Server on http://127.0.0.1:20001 with service id /sota.
    INFO RVI Server: SOTA Callback Server started.
    INFO RVI Server: Setting up outbound connection to RVI Service Edge at http://127.0.0.1:8801
    INFO RVI Server: Initiate download service name: jlr.com/backend/sota/initiate_download
    INFO RVI Server: Cancel download service name: jlr.com/backend/sota/cancel_download
    INFO RVI Server: Download complete service name: jlr.com/backend/sota/download_complete
    INFO RVI Server: Starting SOTA Transmission Server.
    INFO RVI Server: SOTA Transmission Server started.
    
Every 10 seconds the RVI Backend Server will issue a heartbeat message:

    DEBUG RVI Server: Heartbeat.


Your RVI Backend is now ready for use.


USING THE RVI BACKEND
---------------------




