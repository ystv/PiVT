import logging
import asyncore
import asynchat
import socket
import shlex
from time import sleep

"""Networking code for PiVT system"""

# How often to poll videopath for new files, in seconds
CYCLE_TIME = 10

HELPSTRING = ("PiVT Command Reference: \r\n" 
                "\t p         \t\tPlay loaded file\r\n" 
                "\t l FILENAME\t\tLoad file in background\r\n" 
                "\t s         \t\tStop playing\r\n" 
                "\t i         \t\tDisplay current status\r\n" 
                "\t g         \t\tDisplay list of files and durations\r\n" 
                "\t m         \t\tToggle auto-play of loaded videos\r\n"
                "\t h         \t\tShow this help\r\n" 
                "\t q         \t\tDisconnect\r\n\r\n")

class PiVTClientConn(asynchat.async_chat):
    """Client connection handler with command processing logic"""
    def __init__(self, server, socket, address, controller, filelist):
        asynchat.async_chat.__init__(self, socket)
        self.set_terminator("\r\n")
        self.data = ""
        self.controller = controller
        self.filelist = filelist
        self._server = server
        
        self.push("Welcome to PiVT\r\n")
        
    def collect_incoming_data(self,data):
        self.data = self.data + data

    def found_terminator(self):
        """Handle new incoming data by processing command line"""
        # Split the command up
        line = self.data
        self.data = ""
        try:
            splits = shlex.split(line)
            splits[0] = splits[0].lower()
            logging.debug("Command '%s' from %s:%s", line, self.addr[0], 
                          self.addr[1])
        except IndexError:
            logging.debug("Bad command from %s:%s", self.addr[0], self.addr[1])
            self.push("Bad command\r\n")
            return
    
        # Identify and process as appropriate
        if splits[0] == 'q':
            self.push("Goodbye!\r\n\r\n")
            self.close_when_done()
        elif splits[0] == 'h':
            self.push(HELPSTRING)
        elif splits[0] == 'p':
            res = self.controller.play()
            
            if res == 0:
                active, loaded, duration, remain, auto = self.controller.get_info()
                
                self._server.broadcast("202 Playing \"{0}\" {1} "
                                    "seconds long\r\n".format(active, duration))
            else:
                self.push("500 {0}\r\n".format(res))
        elif splits[0] == 'l':
            # Make sure we got a filename
            if not len(splits) > 1:
                self.push("Bad command\r\n")
                
            else:
                # Check the file exists and grab a duration
                duration = self.filelist.get_file_duration(splits[1])
                
                if duration < 0:
                    self.push("404 File: \"{0}\" not found!\r\n".format(splits[1]))
                else:
                    ret = self.controller.load(splits[1], duration)
                    if ret != 0:
                        self.push("500 {0}\r\n".format(ret))
                    else:
                        self.push('203 Loaded "{0}", {1} seconds long\r\n'.format(splits[1], duration))
        elif splits[0] == 's':
            ret = self.controller.stop()
            if (ret != 0):
                self.push("500 {0}\r\n".format(ret))
            else:
                active, loaded, duration, remain, auto = self.controller.get_info()
                if loaded != None:
                    loadsegment = "Loaded \"{0}\", {1} seconds long".format(loaded, duration)
                else:
                    loadsegment = "No video loaded"

                self._server.broadcast("204 Stopped, {1}, Auto {0}\r\n".format(repr(auto), loadsegment))
                
        elif splits[0] == 'i':
            active, loaded, duration, remain, auto = self.controller.get_info()
            
            resultdata = "200 "
            if active != None:
                resultdata += "Playing \"{0}\", ".format(active)
            else:
                resultdata += "Stopped, "
            
            if loaded != None:
                resultdata += "Loaded \"{0}\", ".format(loaded)
            else:
                resultdata += "No video loaded, "
                
            resultdata += "{0} seconds remain, Auto {1}\r\n".format(remain, auto)
            
            self.push(resultdata)
        elif splits[0] == 'g':
            self.push(self.filelist.get_file_listing())
        elif splits[0] == 'm':
            self.controller.toggle_auto()
            self.push("Auto Enabled set to {0}\r\n".format(repr(self.controller.automode)))
        else:
            self.push("Unknown command\r\n")


class PiVTNetwork(asyncore.dispatcher):
    """Network setup wrapper to open ports etc"""
    def __init__(self, port, controller, filelist):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind(("", port))
        self.listen(5) 
        self.controller = controller
        self.clientlist = []
        
        logging.info("Network interface opened on port %d", port)
        
        self.filelist = filelist
        
    def handle_accept(self):
        try:
            conn, addr = self.accept()
            logging.info("Gained a client from %s:%s", addr[0], addr[1])
            self.clientlist.append(PiVTClientConn(self, conn, addr, self.controller, self.filelist))
        except:
            logging.exception("Client connection from %s:%s failed!", 
                              addr[0], addr[1])
            
    def broadcast(self, message):
        """Send a message to all connected clients"""
        """Purge closed clients"""
        self.clientlist[:] = [client for client in self.clientlist if client.connected]
        
        for client in self.clientlist:
            client.push(message)

    def poll(self):
        """Wrapper so the top-level class doesn't need asyncore"""
        asyncore.poll(0.1)
        
    def shutdown(self):
        """Wrapper so top-level class can kill asyncore"""
        for client in self.clientlist:
            client.push("Shutting down\r\n")
            client.close_when_done()
        
        sleep(0.2)
        asyncore.socket_map.clear()
