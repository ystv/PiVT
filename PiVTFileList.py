import subprocess
import threading
import os
from time import sleep

class PiVTFileList():
    def __init__(self, videopath, cycletime):
        self._videopath = videopath
        self._cycletime = cycletime

    def get_file_listing(self):
        # Extract the relevant bits of the list and format for output

    def get_file_duration(self, path):
        duration = -1
        try:
            duration = self._filelist[path]
        catch KeyError:
            return -2

        return duration

    def update_list_thread(self):
        while self._runuodates:
            # List files in the directory

            # Remove deleted items

            # Find everything not in the list
        
            # Loop over and grab some durations

            # Limit resource usage
            sleep(self._cycledelay)
