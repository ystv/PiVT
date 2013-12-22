from time import sleep
from pprint import pprint
import argparse
import yaml
import os
import shlex
import logging
import sys

#from OMXControl import OMXControl 
#from PiVTNetwork import PiVTNetwork
from PiVTNetwork import PiVTNetwork

"""PiVT video player system

This is the main file that runs the app - see README.md for more info

"""

LOG_FORMAT = '%(asctime)s:%(levelname)s:%(message)s'

# Helper function so config parsing is easier
def default(x, e, y):
    try:
        return x()
    except e:
        return y
    
def parse_commandline():
    """Configure argparse and read arguments"""
    parser = argparse.ArgumentParser(description='Video player wrapper around OMXPlayer')
    parser.add_argument('--config', help='Configuration file (see config.yaml as an example, overridden by command line)', 
        dest='configfile', nargs='?', default=None)
    parser.add_argument('--stopvideo, -s', action='store', 
        help='Video to show when nothing is playing (ignored if a playlist is set). Relative to --videofolder', 
        dest='stopvideo')
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
    stopvideo = None
    videofolder = None
    playlist = None
    port = None
    omxcommands = ['-s', '--no-osd']
    
    # Read a configuration file
    if argparser.configfile != None:
        try:
            with open(argparser.configfile, 'r') as f:
                configdata = yaml.load(f)
            videofolder = default(lambda: configdata['videofolder'], IndexError, None)
            stopvideo = default(lambda: configdata['stopvideo'], IndexError, None)   
            port = default(lambda: configdata['port'], IndexError, None)
            omxstring = default(lambda: configdata['omxargs'], KeyError, '')
            omxcommands += shlex.split(omxstring)
            playlist = default(lambda: configdata['playlist'], IndexError, None)
    
        except:
            logging.exception('Unable to load requested config file!')
    
    # Handle command line args
    if argparser.folder != None:
        videofolder = argparser.folder
    if argparser.stopvideo != None:
        stopvideo = argparser.stopvideo
    if argparser.port != None:
        port = argparser.port
    if argparser.omxcommands != None:
        omxcommands += shlex.split(argparser.omxcommands)
    
    # Some configuration validation logic
    if port == None and playlist == None:
        logging.error('No port set and no playlist specified.')
        sys.exit(1)
    elif stopvideo == None and playlist == None:
        logging.error('Playlist or stopvideo must be set')
        sys.exit(2)
    elif port == None:
        logging.info('Port not set, network interface disabled')
    if videofolder == None:
        logging.warn('Video folder should probably be set')
    else:
        stopvideo = os.path.join(videofolder, stopvideo)
    if stopvideo != None and playlist != None:
        logging.warn('Ignoring redundant stopvideo as a playlist was set')    
    
        
    # Set up single item playlist for stopvideo if needed
    if playlist == None:
        playlist = [stopvideo, ]
        
    return (videofolder, playlist, port, omxcommands)

if __name__ == '__main__':
    # Startup logger
    logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT)
    logging.info("PiVT starting up")
    
    # Load configuration data
    args = parse_commandline()
    videofolder, playlist, port, omxcommands = parse_config(args)
    logging.info("Configuration loaded")

    if port != None:
        # Network server startup
        network = PiVTNetwork(port, player)
    
    # Load up some video players
    # Main loop
    logging.debug("Begin main loop")
    while True:
        # Service active network connections if up
        if port != None:
            network.poll()
            
        # Sleep 20s to avoid thrashing CPU
        sleep(0.02)
        
    
    sys.exit(0)