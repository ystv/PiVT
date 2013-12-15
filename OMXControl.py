import threading
import re
import logging
import pexpect

class OMXControl(object):

    _PLAY_TOGGLE = 'p'
    _STOP_COMMAND = 'q'
    _POSITION_REGEX = re.compile(r'M:\s*([\d.]+)')
    _PLAYER_COMMAND = '/usr/bin/omxplayer'
    
    # Status options: 1 - Play, 0 - Pause, -1 - Not loaded, -2 - Loading
    _status = -1
    

    def __init__(self, fileargs):
        logging.basicConfig(level=logging.DEBUG)
        logging.info("Starting OMXControl...")
        
        self._omxinstance = pexpect.spawn(self._PLAYER_COMMAND, fileargs, timeout=None)

        # Set up some state vars
        self._position = 0
        self._status = -2
        
        # Spin up the monitoring thread and let it monitor
        logging.debug("Spinning up monitor thread")
        self._monitorthread = threading.Thread(target=self._monitor_player, args=(self._omxinstance,))
        self._monitorthread.start()
        
    def __del__(self):
        logging.debug("Destructing")
        if self._omxinstance.isalive():
            self._omxinstance.kill(0)
            
        
    def pause(self):
        if self._status == 1:
            self._status = 0
            self._omxinstance.write(self._PLAY_TOGGLE)

    def play(self):
        if self._status == 0:
            self._status = 1
            self._omxinstance.write(self._PLAY_TOGGLE)
    
    # End playback and shutdown the player        
    def stop(self):
        if self._status != -1 and self._omxinstance.isalive():
            self._omxinstance.write(self._STOP_COMMAND)
    
    # Return the current play position in fractional seconds    
    def get_position(self):
        return self._position
    
    # Returns true when ready for playback
    def get_ready(self):
        if self._status == 0:
            return True

    # Internally monitor the player and update status
    def _monitor_player(self, instance):
        logging.debug("Startup of monitor thread")
        while True:
            # Try and catch the process' death
            if instance.isalive() == False:
                logging.debug("Dead player!")
                self._status = -1
                break

            matchline = instance.expect(['Video codec', 'have a nice day', self._POSITION_REGEX, pexpect.EOF, pexpect.TIMEOUT])
            if matchline > 3:
                logging.debug("No data")
                # Zero length means something almost certainly went wrong. Die
                if instance.isalive():
                    instance.write(self._STOP_COMMAND)
                self._status = -1
                break
            
            # Try and work out what the data was
            # Was it the shutdown message?
            if 1 == matchline:
                self._status = -1
                instance.kill(0)
                break
            
            # If we're still waiting on startup, it might be the startup complete line
            elif 0 == matchline:
                logging.debug("Pausing")
                # Issue a pause command
                instance.write(self._PLAY_TOGGLE)
                self._status = 0
            
            else:    
                # Ok, probably the position state then
                statusmatch = instance.match.group(1)
                
                if statusmatch != None:
                    self._position = float(statusmatch.strip()) / 1000000
        
        