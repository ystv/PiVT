from time import sleep
import argparse
import yaml
import os
import shlex
import logging
import sys
import atexit

from pivtgapless import PiVTGaplessVideo
from pivtnetwork import PiVTNetwork
from pivtfilelist import PiVTFileList

"""PiVT video player system

This is the main file that runs the app - see README.md for more info

"""

VERSION = "2.0.1"

LOG_FORMAT = "%(asctime)s:%(levelname)s:%(message)s"
LOG_LEVEL = logging.INFO

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
    omxpath = '/usr/bin/omxplayer'
    cycletime = 30
    cleanloop = False
    logfile = None
    
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
            omxpath = default(lambda: configdata['omxplayer'], IndexError, '/usr/bin/omxplayer')
            cycletime = default(lambda: configdata['listcycletime'], IndexError, 30)
            cleanloop = default(lambda: configdata['cleanloop'], IndexError, False)
            logfile = default(lambda: configdata['logfile'], IndexError, None)
    
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
    if cleanloop == True and playlist != None:
        logging.warn('Ignoring cleanloop as playlist set')
        cleanloop = False
        
    # Set up single item playlist for stopvideo if needed
    if playlist == None:
        playlist = [stopvideo, ]
        
    # Standardise video folder path
    videofolder = os.path.normpath(videofolder) + os.sep
        
    return (videofolder, playlist, port, omxcommands, omxpath, cycletime, 
            cleanloop, logfile)

def main():
    # Startup logger
    logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)
    logging.info("PiVT starting up")
    
    # Load configuration data
    args = parse_commandline()
    videofolder, playlist, port, omxcommands, omxpath, cycletime, cleanloop, logfile = parse_config(args)
    
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
    player = PiVTGaplessVideo(playlist, videofolder, omxcommands, omxpath, cleanloop)
    atexit.register(player.shutdown)

    if port != None:
        # Network server startup
        try:
            filelist = PiVTFileList(videofolder, cycletime)
            atexit.register(filelist.kill_updates)
            network = PiVTNetwork(port, player, filelist)
            atexit.register(network.shutdown)
        except:
            logging.exception("Failed to start network server!")
            player.shutdown()
            filelist.kill_updates()
            sys.exit(1)
    
    # Main loop
    logging.debug("Begin main loop")
    
    try:
        while True:
            # Poll video end status and handle update
            if player.poll() == True:
                active, loaded, duration, remain, auto = player.get_info()
                if active != None:
                    network.broadcast("204 Playing \"{0}\" {1} seconds long Auto {2}\r\n".format(active, remain, repr(auto)))
                else:
                    network.broadcast("204 Stopped Auto {0}\r\n".format(repr(auto)))
            
            # Service active network connections if up
            if port != None:
                network.poll()
            
            # Sleep 20ms to avoid thrashing CPU
            sleep(0.02)
    except KeyboardInterrupt:
        player.shutdown()
        if network != None:
            filelist.kill_updates()
            network.shutdown()        
    
    
if __name__ == '__main__':
    main()
    sys.exit(0)
    