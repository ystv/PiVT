import logging
import asyncore
import asynchat
import socket
import shlex

class PiVTClientConn(asynchat.async_chat):
    def __init__(self, server, socket, address):
        asynchat.async_chat.__init__(self, socket)
        self.set_terminator("\r\n")
        self.data = ""
        
    def collect_incoming_data(self,data):
        self.data = self.data + data
        
    def found_terminator(self):
        # Split the command up
        splits = shlex.split(self.data)
        splits[0] = splits[0].lower()
        self.data = ""
        
        # Identify and process as appropriate
        if splits[0] == 'q':
            self.close_when_done()

class PiVTNetwork(asyncore.dispatcher):
    def __init__(self, port):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.bind(("", port))
        self.listen(5)
        
    def handle_accept(self):
        conn, addr = self.accept()
        logging.debug("Gained a client from {0}", repr(addr))
        PiVTClientConn(self, conn, addr)
    