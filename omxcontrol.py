import threading
import re
import logging
import pexpect
import os
import datetime
from time import sleep
from time import mktime

class OMXControl(object):

    _PLAY_TOGGLE = 'p'
    _STOP_COMMAND = 'q'
    _POSITION_REGEX = re.compile(r'M:\s*([\d.]+)')
    _LOG_OMX = False
    _DATA_TIMEOUT = 0.1
    
    # Status options: 1 - Play, 0 - Pause, -1 - Not loaded, -2 - Loading, -3 - Hidden video loading
    _status = -2
    
    # Name of playing file, stored to help calling class
    filename = ""
    
    # Expected time video will end, used in timeout detection
    _endtime = -1
    

    def __init__(self, fileargs, duration = None, binpath = '/usr/bin/omxplayer',
                 hidevideo = False):
        
        cwd = os.getcwd()
        os.chdir(os.path.dirname(binpath))
        
        self._omxinstance = pexpect.spawn(binpath, fileargs, timeout=self._DATA_TIMEOUT)

        if self._LOG_OMX == True:
            os.chdir(cwd)
            self._omxinstance.logfile = open("omxlog-{0}.log".format(datetime.datetime.now()), 'w+')
        
        if (hidevideo == True):
            self._status = -3
        else:
            self._status = -2
        
        # Spin up the monitoring thread and let it monitor
        logging.debug("Spinning up monitor thread")
        self._monitorthread = threading.Thread(target=self._monitor_player, 
                args=(fileargs,binpath,duration))
        self._monitorthread.start()
            
    def kill(self):
        self._omxinstance.terminate(force=True)
        
    def pause(self):
        if self._status == 1:
            self._status = 0
            self._omxinstance.write(self._PLAY_TOGGLE)

    def play(self):
        if self._status == 0:
            self._status = 1
            self._omxinstance.write(self._PLAY_TOGGLE)
            self._endtime = get_current_time() + self.get_remaining()
            
    def runtofirstframe(self):
        """Run the player ahead from not playing to frozen on the first frame"""
        if (self.get_ready() == True and self._position <= 0):
            self.play()
            self._status = -2
    
    # End playback and shutdown the player        
    def stop(self):
        timeout = 10
        while (self._status != -1 and self._omxinstance.isalive()):
            self._omxinstance.write(self._STOP_COMMAND)
            timeout -= 1
            sleep(0.005)

        if (self._status != -1 and self._omxinstance.isalive()):
            self.kill()
    
    # Return the current play position in fractional seconds    
    def get_position(self):
        return self._position
    
    def get_remaining(self):
        if self.duration != None:
            return self.duration - self._position
        else:
            raise ValueError
    
    def get_ready(self):
        """Returns true when ready for playback"""
        if self._status == 0:
            return True
	return False

    def get_alive(self):
        """Returns true if the player has not crashed"""
        if self._status != -1:
            return True
	return False

    # Internally monitor the player and update status
    def _monitor_player(self, fileargs, binpath, duration):
        logging.debug("Startup of monitor thread")
        
        logging.debug("Starting OMXControl with args %s", repr(fileargs))
        
        # Set up some state vars
        self.duration = duration
        self._position = 0
        
        while True:
            # Try and catch the process' death
            if self._omxinstance.isalive() == False:
                logging.debug("Dead player!")
                self._status = -1
                self.kill()
                break

            sleep(0.01)
            matchline = self._omxinstance.expect(['Video codec', 
                                'have a nice day', self._POSITION_REGEX, 
                                pexpect.EOF, pexpect.TIMEOUT],
                                                 timeout=self._DATA_TIMEOUT)
            
            if matchline == 3:
                logging.debug("EOF reached")
                self._status = -1
                self.kill()
                break
            elif matchline == 4:
                # If we should be playing and have passed the end time, die
                if (self._status == 1 and self._endtime < get_current_time() 
                        and self._endtime != -1):
                    logging.debug("Shutting down player")
                    self.kill()
                    self._status = -1
                    break
            
            # Handle graceful shutdown
            elif 1 == matchline:
                self._status = -1
                self._position = self.duration
                logging.debug("Player shutdown itself")
                self._omxinstance.terminate(force=True)
                break
            
            # If we're still waiting on startup, it might be the startup complete line
            elif 0 == matchline:
                logging.debug("Started")
                # Issue a pause command if required
                
                if (self._status == -3):
                    self._omxinstance.write(self._PLAY_TOGGLE)
                    self._status = 0
                    self._position = 0
            
            else:    
                # Ok, probably the position state then
                statusmatch = self._omxinstance.match.group(1)
                
                if statusmatch != None and self._status != 0:
                    self._position = float(statusmatch.strip()) / 1000000
                    
                    if (self._position < 0):
                        self._position = 0
                    
                    if (self._status == -2 and self._position > 0):
                        # Pause the video on an early frame
                        self._omxinstance.write(self._PLAY_TOGGLE)
                        self._status = 0
                    elif (self._status == 1):
                        self._endtime = get_current_time() + self.get_remaining()
        
def get_current_time():
    dt = datetime.datetime.now()
    return mktime(dt.timetuple()) + dt.microsecond/1000000.0
