PiVT
=========

PiVT is a VT playout server for Raspbery Pi, based heavily around Edgar Hucek's OMXPlayer.

Downloading OMXPlayer
---------------------

    git clone git://github.com/YSTV/PiVT.git

Compiling OMXPlayer
-------------------

GCC version 4.7 is required.
You will need the Boost Asio and System libraries and headers.

### Cross Compiling

You need the content of your sdcard somewhere mounted or copied. This is probably
easiest done by NFS mounting the running Pi. Also grab the Raspberry Pi cross compile
toolchain from https://github.com/raspberrypi/tools

Edit Makefile.include and change the settings according your locations.

### Compiling on the Pi

Edit Makefile.include and change NATIVE_BUILD to 1.

Building
-----------------
This needs a custom copy of ffmpeg; either run make ffmpeg to clone and build
or download the binaries from http://ystv.co.uk/static/downloads/PiVT_Server_1.0.0.tar.gz

Run make to build.

Using PiVT
---------------

 ./PiVT -f /path/to/videos/folder/ -v /path/to/stopvideo.mp4

OMXPlayer
---------------
All credit to Edgar Hucek and Petr Baudis (and others!) for the underlying video playing
software, see http://github.com/huceke/omxplayer
