import logging
import os
import pivtfilelist
import sys

from omxcontrol import OMXControl

"""Gapless playback classes"""

# Time left at which to start next video
REMAINING_THRESHOLD = 0.1

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
    _stopvideo = None
    _nextvideo = None
    
    _playlist = []
    _index = 0
    playingduration = 0
    nextduration = 0

    
    def __init__(self, playlist, videofolder, omxargs):
        """Player setup
        
        Grabs durations for playlist contents, loads players, starts playback
        
        Keyword arguments:
        playlist -- List of files to play in order
        videofolder -- Root folder for video file relative paths
        omxargs -- List of arguments to supply to OMXPlayer (filename will be
                   added)
                   
        """
        
        self._omxargs = omxargs
        self._videofolder = videofolder
        
        # Get durations for everything in the playlist
        logging.info("Getting playlist item durations...")
        for item in playlist:
            duration = pivtfilelist.get_omx_duration(self.fullpath(item))
            if duration > 0:
                self._playlist.append([item, duration])

        try:
            # Load the main and second videos
            self._playing = OMXControl(self._omxargs + [self.fullpath(self._playlist[0][0])],
                                       self._playlist[0][1])
            self._advance_playlist()
            self._stopvideo = OMXControl(self._omxargs + 
                                         [self.fullpath(self._playlist[self._index][0])],
                                         self._playlist[self._index][1])
            self._nextvideo = self._stopvideo
            self._advance_playlist()
            
            # Wait for player ready
            while (self._playing.get_ready() != True):
                pass
                    
            # Launch off the current video
            self._playing.play()
        except:
            logging.exception("Startup failed! This is definitely not good!")
            sys.exit(1)
        

    def fullpath(self, stub):
        """Join a video path onto self._videofolder"""
        return os.path.join(self._videofolder, stub)
    
    def load(self, filename, duration=None):
        """Load a video file in the background for playback next"""
        # Grab a duration if needed
        if duration == None:
            duration = pivtfilelist.get_omx_duration(self.fullpath(filename))
        
        if duration == 0:
            return "File could not be loaded"
        
        if self._loader != None:
            self._loader.stop()
            
        self._loader = OMXControl(self._omxargs + [self.fullpath(filename)], duration)
        
        self._nextvideo = self._loader
        
        return 0
    
    def unload(self):
        """Unload a previously loaded file so the playlist continues"""
        if self._loader != None:
            self._loader.stop()
            self._nextvideo = self._stopvideo
            
            self._loader = None
    
    def play(self):
        """Play a previously loaded file immediately"""
        if self._loader != None:
            self._nextvideo = self._playing
            self._playing = self._loader
            
            self._playing.play()
            self._nextvideo.pause()
            self._nextvideo.stop()
            self._nextvideo = self._stopvideo
            
    def pause(self):
        self._playing.pause()

    def resume(self):
        self._playing.play()
                    
    def stop(self):
        preserve = self._playing
        self._stopvideo = self._playing
        
        self._playing.play()
        preserve.pause()
        preserve.stop()
        
        # Load another video
        argsline = self._omxargs + [self.fullpath(self._playlist[self._index][0])]
        self._stopvideo = OMXControl(argsline, self._playlist[self._index][1])
        while(self._stopvideo.get_ready() != True):
            pass
        self._nextvideo = self._stopvideo
    
    def poll(self):
        """Check if the current file has ended, and start next if it has"""
        if self._playing.get_remaining() <= REMAINING_THRESHOLD or self._playing.get_ready < 0:
            logging.info("Advancing. Loading %s as next", self._playlist[self._index][0])
            
            # Update internal state machine
            self._stopvideo = self._playing
            self._playing = self._nextvideo
            
            # Send player instructions
            self._playing.play()
                      
            # Load another video
            argsline = self._omxargs + [self.fullpath(self._playlist[self._index][0])]
            self._stopvideo = OMXControl(argsline, self._playlist[self._index][1])
            while(self._stopvideo.get_ready() != True):
                pass
            self._nextvideo = self._stopvideo
            self._advance_playlist()
        else:
            pass
       
    def _advance_playlist(self):  
        """Advance playlist to next item, looping if needed"""   
        logging.debug("Current index %d of total %d", self._index, len(self._playlist))
        if self._index + 1 >= len(self._playlist):
            self._index = 0
        else:
            self._index += 1
            
    def shutdown(self):
        try:
            self._playing.stop()
            del self._playing
        except:
            pass  
        
        try:
            self._stopvideo.stop()
            del self._stopvideo
        except:
            pass  
         
        try:
            self._loader.stop()
            del self._loader
        except:
            pass             