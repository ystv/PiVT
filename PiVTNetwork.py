import logging
import sys
import asyncore
import asynchat
import socket
import shlex

"""Networking code for PiVT system"""

class PiVTClientConn(asynchat.async_chat):
    """Client connection handler with command processing logic"""
    def __init__(self, server, socket, address, controller):
        asynchat.async_chat.__init__(self, socket)
        self.set_terminator("\r\n")
        self.data = ""
        self.controller = controller
        
        self.push("Welcome to PiVT\r\n")
        
    def collect_incoming_data(self,data):
        self.data = self.data + data
        
    def found_terminator(self):
        logging.debug("Command '%s' from %s:%s", self.data, self.addr[0], 
                      self.addr[1])
        # Split the command up
        splits = shlex.split(self.data)
        splits[0] = splits[0].lower()
        self.data = ""
    
        # Identify and process as appropriate
        if splits[0] == 'q':
            self.push("Goodbye!")
            self.close_when_done()
            


class PiVTNetwork(asyncore.dispatcher):
    """Network setup wrapper to open ports etc"""
    def __init__(self, port, controller):
        try:
            asyncore.dispatcher.__init__(self)
            self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
            self.bind(("", port))
            self.listen(5)
        except:
            logging.exception("Failed to setup network server")
            sys.exit(3)    
        self.controller = controller
        
        logging.info("Network interface opened on port %d", port)
        
    def handle_accept(self):
        try:
            conn, addr = self.accept()
            logging.info("Gained a client from %s:%s", addr[0], addr[1])
            PiVTClientConn(self, conn, addr, self.controller)
        except:
            logging.exception("Client connection from %s:%s failed!", 
                              addr[0], addr[1])
    
    def poll(self):
        asyncore.poll(0.1)