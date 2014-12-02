"""
Copyright (C) 2014, Jaguar Land Rover

This program is licensed under the terms and conditions of the
Mozilla Public License, version 2.0.  The full text of the 
Mozilla Public License is at https://www.mozilla.org/MPL/2.0/

Maintainer: Rudolf Streif (rstreif@jaguarlandrover.com) 
"""

"""
JSON RPC to interact with RVI middleware framwork.
"""

from jsonrpclib.SimpleJSONRPCServer import SimpleJSONRPCServer


class RVIJSONRPCServer(SimpleJSONRPCServer):
    """
    RVI RPC Server Class
    """

    def _dispatch(self, method, params):
        """
        Dispatch RVI 'message'.
        Check if method is 'message', if so dispatch on
        name 'service_name' instead.
        """
        # print "dispatch:", params
        if method == 'message':
            # print "Will dispatch message to: " + params['service_name']
            dict_param = {}
            # Extract the 'parameters' element from the top level JSON-RPC
            # 'param'. 
            # Convert 'parameters' from [{'vin': 1234}, {hello: 'world'}] to
            # a regular dictionary: {'vin': 1234, hello: 'world'}

            #print "Service:", params['service_name']
            #print "Parameters:", params['parameters']
            msg_params = params['parameters']
            for i in range(0, len(msg_params)):
                for j in range(0, len(msg_params[i].keys())):
                    #print "params", msg_params[i].keys()[j], "=", msg_params[i].values()[j]
                    dict_param[msg_params[i].keys()[j]] = msg_params[i].values()[j]

            # print "Parameter dictionary: ", dict_param
            # print 
            # Ship the processed dispatch info upward.
            return SimpleJSONRPCServer._dispatch(self, params['service_name'], dict_param)           
        return SimpleJSONRPCServer._dispatch(self,message, params)
        
