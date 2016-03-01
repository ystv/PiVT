import subprocess
import threading
import logging
import os
import re
import datetime
from time import sleep

_OMX_COMMAND = "/usr/bin/omxplayer"
_DURATION_REXP = re.compile(r".*Duration: (\d\d:\d\d:\d\d.\d\d)")


class PiVTFileList(object):
    def __init__(self, videopath, cycletime):
        self._videopath = videopath
        self._cycletime = cycletime
        self._runupdates = True
        self._filelist = dict()
        
        self._updatethread = threading.Thread(target=self._update_list_thread)
        self._updatethread.start()

    def get_file_listing(self):
        """Extract the relevant bits of the list and format for output"""
        resulttemplate = '206 "{0}" {1} seconds \r\n'
        resultstring = ''
        for item in self._filelist:
            resultstring += resulttemplate.format(item, self._filelist[item])
        resultstring += '205 File listing complete\r\n'
        return resultstring
    
    def get_file_duration(self, path):
        """Get duration of a single file
        
        Returns -1 if duration not yet available or -2 if file does not exist
        
        """
        duration = -1
        try:
            duration = self._filelist[path]
        except KeyError:
            return -2

        return duration

    def kill_updates(self):
        self._runupdates = False
        self._updatethread.join()

    def _update_list_thread(self):
        logging.info("Launching file list update thread for %s", self._videopath)
        while self._runupdates:
            # List files in the directory
            matches = []
            for root, dirs, files in os.walk(self._videopath):
                for filename in files:
                    matches.append(os.path.join(root.replace(self._videopath, '', 1), filename))
            # Remove missing items
            for item in (set(self._filelist) - set(matches)):
                self._filelist.pop(item)
                
            # Add new items and get some durations
            for item in (set(matches) - set(self._filelist)):
                duration = get_omx_duration(os.path.join(self._videopath, item))
                self._filelist[item] = duration             
            # Limit resource usage
            sleep(self._cycletime)

def get_omx_duration(item):
    # Call the player with the offending command
    try:
        data = subprocess.check_output([_OMX_COMMAND, '-i', item], shell=False, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as err:
        logging.warning('Non-zero exit status while getting duration for {0}'.format(item))
        data = err.output
    
    # Try and grab a duration by regex
    matchgroup = _DURATION_REXP.search(data)
    
    if matchgroup != None:
        try:
            x = datetime.datetime.strptime(matchgroup.group(1), '%H:%M:%S.%f')
            duration = datetime.timedelta(hours=x.hour,minutes=x.minute,seconds=x.second,
                           microseconds=x.microsecond).total_seconds()
            logging.info('Got file {0} duration {1} seconds'.format(item, duration))
            return duration
        except ValueError:
            # Bad duration...
            logging.debug('Got bad duration {0}'.format(data))
            return 0
    else:
        logging.debug('Unable to match duration from data:\r\n {0}'.format(data))
        return 0    
