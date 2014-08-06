import logging
import os
import pivtfilelist
import sys
from time import sleep

from omxcontrol import OMXControl

"""Gapless playback classes"""

# Time left at which to start next video
REMAINING_THRESHOLD = 0.12

class PiVTGaplessVideo(object):
    """Load up a series of video players and handle seamless playback

    Loads a trio of omxcontrol interfaces and exposes functions to service video
    ending and playlist advancement, start and stop of network playback
    
    Public methods:
    load(filename) -- Load a new video to be played next
    play() -- Play the next video (loaded or next in playlist)
    unload() -- Unload whatever was loaded with load(), so next video is from list
    stop() -- Immediately return to the playlist item running before play(). 
              Ignored where current video is playlist anyway

    poll() -- Allow class to update internal status and handle starting of new video
    get_status() -- Return a status line of currently playing and loaded video
    
    """
    
    _playing = None
    _loader = None
    _nextvideo = None
    
    playingduration = 0
    nextduration = 0
    automode = False

    
    def __init__(self, videofolder, omxargs, omxpath):
        """Player setup
        
        Grabs durations for playlist contents, loads players, starts playback
        
        Keyword arguments:
        playlist -- List of files to play in order
        videofolder -- Root folder for video file relative paths
        omxargs -- List of arguments to supply to OMXPlayer (filename will be
                   added)
                   
        """
        
        self._omxpath = omxpath
        self._omxargs = omxargs
        self._videofolder = videofolder
        

    def fullpath(self, stub):
        """Join a video path onto self._videofolder"""
        return os.path.join(self._videofolder, stub)
    
    def load(self, filename, duration=None):
        """Load a video file in the background for playback next"""
        # Grab a duration if needed
        if duration == None:
            duration = pivtfilelist.get_omx_duration(self.fullpath(filename))
        
        if duration == 0:
            return "File could not be opened"
        
        if self._loader != None:
            if (safekill(self._loader) == False):
                return "Failed to shut down existing"
            
        # Is there another video playing now? Do we need to hide this one?
        if self._playing != None:
            hvideo = True
        else:
            hvideo = False
        
        self._loader = self._load_internal(filename, duration, hidevideo=hvideo)

        if self._loader != None:            
            timeout = 500  
              
            while (self._loader.get_ready() == False):
                if (timeout > 0):
                    timeout -= 1
                else:
                    return "Loading timed out"
                sleep(0.01)
            
            return 0
        else:
            return "Loading failed"
    
    def play(self, filename=None):
        """Play a previously loaded file immediately or complain."""
        
        #Is a video a) loaded? and b) ready? Complain if not
        if self._loader == None:
            logging.info("Ordered to play but no video loaded")
            return "No video is loaded"
        
        if (self._loader.get_ready == False):
            logging.info("Ordered to %s play but video not ready", 
                         self._loader.filename)
            return "Video is still loading. Try again in a second"
        
        #If a filename was given, verify it matched the loaded file
        if filename != None:
            if (self._loader.filename != filename):
                    resp = "%s not loaded, I have %s".format(filename, 
                                                        self._loader.filename)
                    logging.warn(resp)
                    return resp
        
        # Deal with the current file if we have one
        if (self._playing != None):
            if (safekill(self._playing) == False):
                return "Unable to stop current playing video!"
            
        self._loader.play()
        self._playing = self._loader
        self._loader = None
        
        return 0
            
    def pause(self):
        self._playing.pause()

    def resume(self):
        self._playing.play()
                    
    def stop(self):
        if (safekill(self._playing) == False):
            return "Stop failed!"
        
        self._playing = None
        
        if (self._loader != None):
            self._loader.runtofirstframe()
        
        return 0
        
    def get_info(self):
        active = None
        duration = None
        remain = None
        loaded = None
        
        try:
            active = self._playing.filename
            duration = self._playing.duration
            remain = self._playing.get_remaining()
        except AttributeError:
            active = None
            
        try:
            loaded = self._loader.filename
            
            if duration == None:
                duration = self._loader.duration
                remain = duration
        except AttributeError:
            loaded = None
            
        return active, loaded, duration, remain, self.automode
    
    def toggle_auto(self):
        self.automode = not self.automode
    
    def poll(self):
        """Check if the current file has ended, and start next if it has"""
        if (self._playing != None):
            if (self._playing.get_remaining() <= REMAINING_THRESHOLD or
                self._playing.get_alive() == False):
                
                logging.debug("Stopped %s", self._playing.filename)
                
                safekill(self._playing)
                self._playing = None
                
                if (self.automode == True and self._loader != None):
                    logging.info("Auto-advancing")
                    self.play()
                elif (self._loader != None):
                    self._loader.runtofirstframe()
                
                # Marker that something happened
                return True
        return False
       
    def _load_internal(self, filename, duration, extraflags=[], hidevideo = False):
        """Wrap up the boilerplate to open a new file and wait for readiness"""
        argsline = self._omxargs + [self.fullpath(filename)] + extraflags        
        newvideo = OMXControl(argsline, duration, self._omxpath, hidevideo)
        newvideo.filename = filename
        
        return newvideo
            
    def shutdown(self):
        try:
            self._playing.kill()
            logging.info("Killed player")
        except AttributeError:
            logging.debug("Cannot kill playing as not running!")
            
        try:
            self._loader.kill()
            logging.info("Killed loader")
        except AttributeError:
            logging.debug("Cannot kill loader as not running!")

def safekill(instance):
    """Attempt to kill an instance or timeout"""
    if (instance == None):
        return True
    
    timeout = 10
    while (instance.get_alive()):
        instance.kill();
        if (timeout > 0):
            timeout -= 1
        else:
            return False
        sleep(0.01)
    return True
