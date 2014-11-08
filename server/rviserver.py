"""
Copyright (C) 2014, Jaguar Land Rover

This program is licensed under the terms and conditions of the
Mozilla Public License, version 2.0.  The full text of the 
Mozilla Public License is at https://www.mozilla.org/MPL/2.0/

Maintainer: Rudolf Streif (rstreif@jaguarlandrover.com) 
"""

"""
Backend daemon that connects to RVI, receives, dispatches and processes
incoming messages from vehicles.
"""

import sys, os, logging, jsonrpclib, base64, atexit, threading
import time, datetime, pytz
from signal import *
import logging.config
from urlparse import urlparse
from jsonrpclib.SimpleJSONRPCServer import SimpleJSONRPCServer
import jsonrpclib
import Queue

import django
from django.conf import settings
from django.db import connection

# The backend server daemon depends on the Django ORM and uses settings
# from DJANGO_SETTINGS_MODULE. Append the relative path to the web
# backend to the Python search path for modules.
sys.path.append('../web')

# set the default Django settings module
# set the default Django settings module
os.environ['DJANGO_SETTINGS_MODULE'] = 'rvi.settings'
django.setup()

# import models after importing the settings
import sota.models

# setup logging
logging.config.dictConfig(settings.LOGGING)
# use RVI logger for general logging
rvi_logger = logging.getLogger('rvi')
# use SOTA logger for SOTA logging
sota_logger = logging.getLogger('rvi.sota')


# globals
package_queue = Queue.Queue()


# RVI RPC Server Class
class RVIJSONRPCServer(SimpleJSONRPCServer):
    # Check if method is 'message', if so dispatch on
    # name 'service_name' instead.
    def _dispatch(self, method, params):
        # print "dispatch:", params
        if method == 'message':
            # print "Will dispatch message to: " + params['service_name']
            dict_param = {}
            # Extract the 'parameters' element from the top level JSON-RPC
            # 'param'. 
            # Convert 'parameters' from [{'vin': 1234}, {hello: 'world'}] to
            # a regular dictionary: {'vin': 1234, hello: 'world'}

            # print "Parameters:", params['parameters']
            msg_params = params['parameters'] 
            for i in range(0, len(msg_params)):
                for j in range(0, len(msg_params[i].keys())):
                    # print "params", msg_params[i].keys()[j], "=", msg_params[i].values()[j]
                    dict_param[msg_params[i].keys()[j]] = msg_params[i].values()[j]

            # print "Parameter disctionary: ", dict_param
            # print 
            # Ship the processed dispatch info upward.
            return SimpleJSONRPCServer._dispatch(self, params['service_name'], dict_param)           
        return SimpleJSONRPCServer._dispatch(self,message, params)
        
# SOTA Callback Server
class SOTACallbackServer(threading.Thread):
    def __init__(self, callback_url, service_id):
        threading.Thread.__init__(self)
        url = urlparse(callback_url)
        self.localServer =  RVIJSONRPCServer(addr=((url.hostname, url.port)), logRequests=False)
        self.localServer.register_function(initiate_download, service_id + "/initiate_download")
        self.localServer.register_function(cancel_download, service_id + "/cancel_download")
        self.localServer.register_function(download_complete, service_id + "/download_complete")
        
    def run(self):
        self.localServer.serve_forever()
        
    def shutdown(self):
        self.localServer.shutdown()
        
# SOTA Transmission Server
class SOTATransmissionServer(threading.Thread):
    def __init__(self, service_edge, service_id='/sota', chunk_size=65536):
        threading.Thread.__init__(self)
        self.service_edge = service_edge
        self.service_id = service_id
        self.chunk_size = chunk_size
        self.transaction_id = 0
        
    def shutdown(self):
        self._Thread__stop()
        
    def run(self):
        while True:
            [package, destination, retry] = package_queue.get()
            rvi_logger.info('SOTA Transmission Server: Sending package %s to %s', package, destination)

            # accessing database objects
            retry_obj = None
            update_obj = None
            package_obj = None
            try:
                retry_obj = sota.models.Retry.objects.filter(pk=retry)[0]
                update_obj = retry_obj.ret_update
                package_obj = update_obj.upd_package
            except Exception as e:
                rvi_logger.error('SOTA Transmission Server: Cannot access database object: %s, Error: %s', retry, e)
                continue

            try:
                f = open(package_obj.pac_file.url)
            except Exception as e:
                sota_logger.error('SOTA Transmission Server: %s: Cannot open file: %s', retry_obj, package_obj.pac_file.url)
                retry_obj.set_status(sota.models.Status.FAILED)
                update_obj.set_status(sota.models.Status.FAILED)
                continue
 
            retry_obj.set_status(sota.models.Status.RUNNING)
            update_obj.set_status(sota.models.Status.RUNNING)


            f_stat = os.stat(package_obj.pac_file.url)

            self.transaction_id += 1
            self.service_edge.message(calling_service = self.service_id,
                               service_name = destination + "/start",
                               transaction_id = str(self.transaction_id),
                               timeout = int(retry_obj.get_timeout_epoch()),
                               parameters = [{ u'package': package,
                                               u'chunk_size': self.chunk_size,
                                               u'total_size': f_stat.st_size
                                           }])

            index = 0
            while True:
                msg =  f.read(self.chunk_size)
                if msg == "":
                    break
                sota_logger.debug('SOTA Transmission Server: %s: Sending package: %s, chunk: %d, message size: %s', retry_obj, package, index, len(msg))
                self.transaction_id += 1
                self.service_edge.message(calling_service = self.service_id,
                                   service_name = destination + "/chunk",
                                   transaction_id = str(self.transaction_id),
                                   timeout = int(retry_obj.get_timeout_epoch()),
                                   parameters = [
                                       { u'index': index },
                                       { u'msg': base64.b64encode(msg) }])
                time.sleep(0.05)
                index += 1

            f.close()
            
            time.sleep(1.0)

            sota_logger.info('SOTA Transmission Server: %s: Finishing package: %s', retry_obj, package)            
            self.transaction_id += 1
            self.service_edge.message(calling_service = self.service_id,
                               service_name = destination + "/finish",
                               transaction_id = str(self.transaction_id),
                               timeout = int(retry_obj.get_timeout_epoch()),
                               parameters = [ { u'dummy': 0}])


# Callback functions
def initiate_download(package, destination, retry):
    rvi_logger.info('SOTA Callback Server: Initiate download request: retry %s - %s to %s.', retry, package, destination)
    package_queue.put([package, destination, retry])
    return {u'status': 0}

def cancel_download(retry):
    rvi_logger.info('SOTA Callback Server: Cancel download request: retry: %s.', retry)
    retry_obj = None
    update_obj = None
    try:
        retry_obj = sota.models.Retry.objects.filter(pk=retry)[0]
        update_obj = retry_obj.ret_update
    except:
         rvi_logger.error('SOTA Callback Server: Cancel downlaod request: Cannot access database object: %s', retry)
         return {u'status': 0}
    retry_obj.set_status(sota.models.Status.REJECTED)
    update_obj.set_status(sota.models.Status.REJECTED)
    sota_logger.info('SOTA Callback Server: Cancel download request: %s.', retry_obj)
    return {u'status': 0}
    
def download_complete(status, retry):
    rvi_logger.info('SOTA Callback Server: Download complete: retry: %s, status: %s.', retry, status)
    retry_obj = None
    update_obj = None
    try:
        retry_obj = sota.models.Retry.objects.filter(pk=retry)[0]
        update_obj = retry_obj.ret_update
    except:
         rvi_logger.error('SOTA Callback Server: Download complete: Cannot access database object: %s', retry)
         return {u'status': 0}
    if int(status) == 0:
        retry_obj.set_status(sota.models.Status.SUCCESS)
        update_obj.set_status(sota.models.Status.SUCCESS)
    else:
        retry_obj.set_status(sota.models.Status.FAILED)
        update_obj.set_status(sota.models.Status.FAILED)
    sota_logger.info('SOTA Callback Server: Download complete: retry: %s, status: %s.', retry_obj, status)
    return {u'status': 0}
    



class Daemon:
    """
    A generic daemon class.
    Usage: subclass the Daemon class and override the run() method
    """
    def __init__(self, pidfile, stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'):
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        self.pidfile = pidfile
       
    def daemonize(self):
        """
        do the UNIX double-fork magic, see Stevens' "Advanced
        Programming in the UNIX Environment" for details (ISBN 0201563177)
        http://www.erlenstar.demon.co.uk/unix/faq_2.html#SEC16
         """
        try:
            pid = os.fork()
            if pid > 0:
                # exit first parent
                sys.exit(0)
        except OSError, e:
            sys.stderr.write("fork #1 failed: %d (%s)\n" % (e.errno, e.strerror))
            sys.exit(1)
       
        # decouple from parent environment
        os.chdir("/")
        os.setsid()
        os.umask(0)
       
        # do second fork
        try:
            pid = os.fork()
            if pid > 0:
                # exit from second parent
                sys.exit(0)
        except OSError, e:
            sys.stderr.write("fork #2 failed: %d (%s)\n" % (e.errno, e.strerror))
            sys.exit(1)
       
        # redirect standard file descriptors
        sys.stdout.flush()
        sys.stderr.flush()
        si = file(self.stdin, 'r')
        so = file(self.stdout, 'a+')
        se = file(self.stderr, 'a+', 0)
        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())
       
        # write pidfile
        atexit.register(self.delpid)
        pid = str(os.getpid())
        file(self.pidfile,'w+').write("%s\n" % pid)
       
    def delpid(self):
        os.remove(self.pidfile)
 
    def start(self):
         """
         Start the daemon
         """
         # Check for a pidfile to see if the daemon already runs
         try:
             pf = file(self.pidfile,'r')
             pid = int(pf.read().strip())
             pf.close()
         except IOError:
              pid = None
       
         if pid:
             message = "pidfile %s already exist. Daemon already running?\n"
             sys.stderr.write(message % self.pidfile)
             sys.exit(1)
               
         # Start the daemon
         self.daemonize()
         self.run()
 
    def stop(self):
        """
        Stop the daemon
        """
        # Get the pid from the pidfile
        try:
            pf = file(self.pidfile,'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None
       
        if not pid:
            message = "pidfile %s does not exist. Daemon not running?\n"
            sys.stderr.write(message % self.pidfile)
            return # not an error in a restart
 
        # Try killing the daemon process       
        try:
            while 1:
                os.kill(pid, SIGTERM)
                time.sleep(0.1)
        except OSError, err:
            err = str(err)
            if err.find("No such process") > 0:
                if os.path.exists(self.pidfile):
                    os.remove(self.pidfile)
            else:
                print str(err)
                sys.exit(1)
 
    def restart(self):
        """
        Restart the daemon
        """
        self.stop()
        self.start()
 
    def run(self):
        """
        You should override this method when you subclass Daemon. It will be called after the process has been
        daemonized by start() or restart().
        """
        


class RVIServer(Daemon):
    """
    """
    rvi_service_edge = None
    sota_cb_server = None
    sota_tx_server = None
    
    def cleanup(self, *args):
        rvi_logger.info('RVI Server: Caught signal: %d. Shutting down...', args[0])
        if self.sota_cb_server:
            self.sota_cb_server.shutdown()
        if self.sota_tx_server:
            self.sota_tx_server.shutdown()
        sys.exit(0)


    def run(self):
        # Execution starts here
        rvi_logger.info('RVI Server: Starting...')

        # get settings from configuration
        # service edge url
        try:
            rvi_url = settings.RVI_SERVICE_EDGE_URL
        except NameError:
            rvi_logger.error('RVI Server: RVI_SERVICE_EDGE_URL not defined. Check settings!')
            sys.exit(1)
        # chunk size
        try:
            rvi_chunk_size = settings.RVI_SOTA_CHUNK_SIZE
            rvi_chunk_size = int(rvi_chunk_size)
        except NameError:
            rvi_chunk_size = 128*1024
        # SOTA service url
        try:
            rvi_callback_url = settings.RVI_SOTA_CALLBACK_URL
        except NameError:
            rvi_logger.error('RVI Server: RVI_SOTA_CALLBACK_URL not defined. Check settings!')
            sys.exit(1)
        # SOTA service id
        try:
            rvi_service_id = settings.RVI_SOTA_SERVICE_ID
        except NameError:
            rvi_service_id = '/sota'
        # root directory for files
        try:
            media_root = settings.MEDIA_ROOT
        except NameError:
            media_root = '.'

        rvi_logger.info('RVI Server: Configuration: ' + 
            'BASE_DIR: '              + settings.BASE_DIR + ', ' +
            'RVI_SERVICE_EDGE_URL: '  + rvi_url + ', ' +
            'RVI_SOTA_CALLBACK_URL: ' + rvi_callback_url + ', ' +
            'RVI_SOTA_SERVICE_ID: '   + rvi_service_id + ', ' +
            'RVI_SOTA_CHUNK_SIZE: '   + str(rvi_chunk_size) + ', ' +
            'MEDIA_ROOT: '            + media_root
            )

        # start the SOTA callback server
        try:
            rvi_logger.info('RVI Server: Starting SOTA Callback Server on %s with service id %s.', rvi_callback_url, rvi_service_id)
            self.sota_cb_server = SOTACallbackServer(rvi_callback_url, rvi_service_id)
            self.sota_cb_server.start()
            rvi_logger.info('RVI Server: SOTA Callback Server started.')
        except Exception as e:
            rvi_logger.error('RVI Server: Cannot start SOTA Callback Server: %s', e)
            sys.exit(1)

        # wait for RVI server to come up    
        time.sleep(0.5)

        # setup RVI Service Edge
        rvi_logger.info('RVI Server: Setting up outbound connection to RVI Service Edge at %s', rvi_url)
        self.rvi_service_edge = jsonrpclib.Server(rvi_url)
        result = self.rvi_service_edge.register_service(service=rvi_service_id+'/initiate_download',
                                                network_address=rvi_callback_url)
        rvi_logger.info('RVI Server: Initiate download service name: %s', result['service'])
        result = self.rvi_service_edge.register_service(service=rvi_service_id+'/cancel_download',
                                                   network_address=rvi_callback_url)
        rvi_logger.info('RVI Server: Cancel download service name: %s', result['service'])
        result = self.rvi_service_edge.register_service(service=rvi_service_id+'/download_complete',
                                                   network_address=rvi_callback_url)
        rvi_logger.info('RVI Server: Download complete service name: %s', result['service'])
                                          
        # start SOTA Transmission Server
        try:
            rvi_logger.info('RVI Server: Starting SOTA Transmission Server.')
            self.sota_tx_server = SOTATransmissionServer(self.rvi_service_edge, rvi_service_id, rvi_chunk_size)
            self.sota_tx_server.start()
            rvi_logger.info('RVI Server: SOTA Transmission Server started.')
        except Exception as e:
            rvi_logger.error('RVI Server: Cannot start SOTA Transmission Server: %s', e)
            sys.exit(1)
    

        for sig in (SIGABRT, SIGTERM, SIGINT):
            signal(sig, self.cleanup)

        while True:
            try:
                time.sleep(10)
                # if we are idle too long the database server may
                # close the connection on us, ping the server
                # and reconnect if necessary
                if (connection.connection is not None):
                    if (connection.is_usable()): 
                        rvi_logger.debug('RVI Server: Database connection is up.')
                    else:
                        rvi_logger.error('RVI Server: Database connection is down.')
                        connection.close()
                else:    
                    rvi_logger.error('RVI Server: Database connection is closed.')
            except KeyboardInterrupt:
                print ('\n')
                break



def usage():
    print "RVI Server: Usage: %s foreground|start|stop|restart" % sys.argv[0]        
        
if __name__ == "__main__":
    rvi_server = None
    pid_file = None
    if len(sys.argv) == 3:
        pid_file = sys.argv[2]
    else:
        pid_file = '/var/run/rviserver.pid'
    rvi_server = RVIServer(pid_file, stdin='/dev/stdin', stdout='/dev/stdout', stderr='/dev/stderr')
    if len(sys.argv) >= 2:
        if sys.argv[1] in ('foreground', 'fg'):
            # in foreground we also log to the console
            rvi_logger.addHandler(logging._handlers['console'])
            rvi_server.run()
        elif sys.argv[1] in ('start', 'st'):
            rvi_server.start()
        elif sys.argv[1] in ('stop', 'sp'):
            rvi_server.stop()
        elif sys.argv[1] in ('restart', 're'):
            rvi_server.restart()
        else:
            print "RVI Server: Unknown command."
            usage()
            sys.exit(2)
    else:
        usage()
        sys.exit(2)
            




