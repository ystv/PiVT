PiVT
=========

PiVT is a VT playout server for Raspbery Pi, which wraps OMXPlayer to provide
seamless(-ish) playback and network control.

Written in Python, two modes are provided, either network-controlled or playlist
mode. In network-controlled mode, a video is looped continuously until commands
are received from a simple telnet interface (connect and press `h <ENTER>` for
a list of the commands). A client, PiVTDesktop is available at
https://github.com/YSTV/PiVTDesktop

Playlist mode takes a simple playlist from the configuration file and loops it,
for example for digital signage applications.

Downloading PiVT
---------------------

    git clone git://github.com/YSTV/PiVT.git
    
Prerequisites
------------------
The YAML and pexpect modules for Python are required for PiVT. For Raspbian,
run something like this to install them:

    sudo apt-get install python-pexpect python-yaml

For smooth video playback, at least 128MB RAM must be assigned to the GPU, use
`raspi-config` to configure this.

Configuration
-----------------
Configuration can either be supplied on the command line or within a YAML
configuration file. A sample, config.yaml, is provided. At least one valid
playlist item or stopvideo is required so something is always played.

To specify arguments with the command line, say `python PiVT.py --help` 
for a full listing of command line options. It is not possible to set some
options (such as playlists) from the command line

Using PiVT
---------------
Ensure you can launch OMXPlayer and play a video correctly. Then do:

    python PiVT.py --config config.yaml

Clean Loop Mode
---------------
As an additional feature, cleanloop mode can be enabled when an OMXPlayer
build that implements the `--loop` flag is available, for example at
https://github.com/stewiem2000/omxplayer/tree/seamless-looping
This can be a little temperamental, but means the stopvideo will seamlessly
restart at the end provided the source video is seamless, by continually
looping it in the background.

Daemonise
-----------
    sudo python PiVTDaemon.py start --config /absolute/path/to/file.yaml
This will start PiVT as a daemon and return immediately, it will run in the 
background

Changelog
------------

### v2.0.1 (18/01/2014) ###
- Added a more helpful error message when no stopvideo/playlist video could be 
loaded at all
- Version number now shown as part of help output

### v2.0 (16/01/2014) ###
- Complete rewrite to hook OMXPlayer using pexpect and Python
- Significantly increased stability and reduced random crashes, added error 
handling and recovery
- Playlist can be set in config file in place of a single stop video - will 
loop continuously for digital signage applications unless overridden by network
- Added auto mode to play next loaded video immediately instead of 
returning to playlist
- Added seamless loop mode for stop videos which line up exactly, provided 
suitable OMXPlayer version installed (see above)
- Added daemonisation system to run PiVT with console disconnected
- File list now maintained internally and updated periodically, retrieval 
of list for clients is much faster
- Bugs when changing file types now resolved
- Configuration can be loaded from text file or set on command line
- Reduced delays switching between videos
- Added option to log to file


OMXPlayer
---------------
All credit to Edgar Hucek and Petr Baudis (and others!) for the underlying video playing
software, see http://github.com/popcornmix/omxplayer
