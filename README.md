PiVT
=========

PiVT is a VT playout server for Raspbery Pi, which wraps OMXPlayer to provide
seamless(-ish) playback and network control.

Written in Python, two modes are provided, either network-controlled or playlist
mode. In network-controlled mode, a video is looped continuously until commands
are received from a simple telnet interface (connect and press `h <ENTER>` for
a list of the commands). A .NET client, PiVTDesktop is available at
https://github.com/YSTV/PiVTDesktop

Playlist mode takes a simple playlist from the configuration file and loops it,
for example for digital signage applications.

Downloading OMXPlayer
---------------------

    git clone git://github.com/YSTV/PiVT.git

Configuration
-----------------
Configuration can either be supplied on the command line or within a YAML
configuration file. A sample, config.yaml, is provided.

To specify arguments with the command line, say `python PiVT.py --help`

For a full listing of command line options. It is not possible to set some
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

OMXPlayer
---------------
All credit to Edgar Hucek and Petr Baudis (and others!) for the underlying video playing
software, see http://github.com/popcornmix/omxplayer
