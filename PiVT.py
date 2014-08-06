from time import sleep
import argparse
import yaml
import os
import shlex
import logging
import sys
import atexit
import signal

from pivtgapless import PiVTGaplessVideo
from pivtnetwork import PiVTNetwork
from pivtfilelist import PiVTFileList

"""PiVT video player system

This is the main file that runs the app - see README.md for more info

"""

VERSION = "2.1.0"

LOG_FORMAT = "%(asctime)s:%(levelname)s:%(message)s"
LOG_LEVEL = logging.DEBUG

player = None
network = None
filelist = None

def handle_pdb(sig, frame):
    import pdb
    pdb.Pdb().set_trace(frame)

# Helper function so config parsing is easier
def default(x, e, y):
    try:
        return x()
    except e:
        return y
    
def parse_commandline():
    """Configure argparse and read arguments"""
    parser = argparse.ArgumentParser(description='Video player wrapper around OMXPlayer. Version: ' + VERSION)
    parser.add_argument('--config', help='Configuration file (see config.yaml as an example, overridden by command line)', 
        dest='configfile', nargs='?', default=None)
    parser.add_argument('--videofolder, -f', action='store', 
        help='Root path for video files', dest='folder')
    parser.add_argument('--port, -p', action='store', 
        help='Communications port for network interface', dest='port')
    parser.add_argument('--omxargs', dest='omxcommands',
                        help='Additional arguments to OMXPlayer, in single quotes')
    return parser.parse_args()


def parse_config(argparser):
    """Configuration loading and validation
    
    Loads configuration from specified file, overwrites with command line
    args and checks we got everything we needed
    
    """
    videofolder = None
    port = None
    omxcommands = ['-s', '--no-osd']
    omxpath = '/usr/bin/omxplayer'
    cycletime = 30
    logfile = None
    
    # Read a configuration file
    if argparser.configfile != None:
        try:
            with open(argparser.configfile, 'r') as f:
                configdata = yaml.load(f)
            videofolder = default(lambda: configdata['videofolder'], IndexError, None)  
            port = default(lambda: configdata['port'], IndexError, None)
            omxstring = default(lambda: configdata['omxargs'], KeyError, '')
            omxcommands += shlex.split(omxstring)
            omxpath = default(lambda: configdata['omxplayer'], IndexError, '/usr/bin/omxplayer')
            cycletime = default(lambda: configdata['listcycletime'], IndexError, 30)
            logfile = default(lambda: configdata['logfile'], IndexError, None)
    
        except:
            logging.exception('Unable to load requested config file!')
    
    # Handle command line args
    if argparser.folder != None:
        videofolder = argparser.folder
    if argparser.port != None:
        port = argparser.port
    if argparser.omxcommands != None:
        omxcommands += shlex.split(argparser.omxcommands)
    
    # Some configuration validation logic
    if port == None:
        logging.error('No port set.')
        sys.exit(1)
    elif port == None:
        logging.info('Port not set, network interface disabled')
    if videofolder == None:
        logging.warn('Video folder should probably be set')
        
    # Standardise video folder path
    videofolder = os.path.normpath(videofolder) + os.sep
        
    return (videofolder, port, omxcommands, omxpath, cycletime, 
            logfile)

def interrupt(signal, frame):
    if player != None:
        player.shutdown()
    
    if network != None:
        network.shutdown()
    
    if filelist != None:
        filelist.kill_updates()
    os._exit(0)

def main():
    # Register handler so SIGUSR1 drops into the debugger
    signal.signal(signal.SIGUSR1, handle_pdb)

    # Startup logger
    logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)
    logging.info("PiVT starting up")
    
    # Load configuration data
    args = parse_commandline()
    videofolder, port, omxcommands, omxpath, cycletime, logfile = parse_config(args)
    
    # Reconfigure logging if needed
    if logfile != None:
        filehandler = logging.FileHandler(logfile)
        filehandler.setLevel(LOG_LEVEL)
        formatter = logging.Formatter(LOG_FORMAT)
        filehandler.setFormatter(formatter)
        logging.getLogger('').addHandler(filehandler)
        logging.info("Setting up logging to %s", logfile)
    
    logging.info("Configuration loaded")

    # Load up the gapless video player class
    try:
        global player
        player = PiVTGaplessVideo(videofolder, omxcommands, omxpath)
        signal.signal(signal.SIGINT, interrupt)    
        atexit.register(player.shutdown)
    except Exception:
        logging.error("Exception caught, shutting down")
        sys.exit(2)
        

    if port != None:
        # Network server startup
        try:
            global filelist
            filelist = PiVTFileList(videofolder, cycletime)
            atexit.register(filelist.kill_updates)
            
            global network
            network = PiVTNetwork(port, player, filelist)
            atexit.register(network.shutdown)
        except:
            logging.exception("Failed to start network server!")
            player.shutdown()
            filelist.kill_updates()
            sys.exit(1)
    
    # Main loop
    logging.debug("Begin main loop")
    
    while True:
        # Poll video end status and handle update
        if player.poll() == True:
            active, loaded, duration, remain, auto = player.get_info()

            if active != None:
                network.broadcast("204 Playing \"{0}\" {1} seconds long Auto {2}\r\n".format(active, remain, repr(auto)))
            else:
                if loaded != None:
                    loadsegment = "Loaded \"{0}\", {1} seconds long".format(loaded, duration)
                else:
                    loadsegment = "No video loaded"

                network.broadcast("204 Stopped, {1}, Auto {0}\r\n".format(repr(auto), loadsegment))
        
        # Service active network connections if up
        if port != None:
            network.poll()
        
        # Sleep 20ms to avoid thrashing CPU
        sleep(0.02)

if __name__ == '__main__':
    main()
    sys.exit(0)
    
