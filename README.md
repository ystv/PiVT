PiVT
=========

PiVT is a VT playout server for Raspbery Pi, based heavily around Edgar Hucek's OMXPlayer.

Downloading OMXPlayer
---------------------

    git clone git://github.com/YSTV/PiVT.git

Compiling OMXPlayer
-------------------

GCC version 4.7 is required. To do this on a pi, try something like:

    cd /usr/bin
    rm arm-linux-gnueabihf-gcc arm-linux-gnueabihf-g++ arm-linux-gnueabihf-cpp
    ln gcc-4.7 arm-linux-gnueabihf-gcc -s
    ln g++-4.7 arm-linux-gnueabihf-g++ -s
    ln cpp-4.7 arm-linux-gnueabihf-cpp -s

You will need the Boost Asio and System libraries and headers along with 
libpcre++ and freetype 2. Run something like:

    apt-get install libpcre++-dev libasio-dev libboost-system-dev libfreetype6-dev

### Cross Compiling

You need the content of your sdcard somewhere mounted or copied. This is probably
easiest done by NFS mounting the running Pi or using the piimg tool at
https://github.com/alexchamberlain/piimg. Also grab the Raspberry Pi cross compile
toolchain from https://github.com/raspberrypi/tools

Edit Makefile.include and change the settings according your locations.

### Compiling on the Pi

Edit Makefile.include and change NATIVE_BUILD to 1.

Building
-----------------
This needs a custom copy of ffmpeg; either run make ffmpeg to clone and build
or download the binaries from http://ystv.co.uk/static/downloads/PiVTServer.tar.gz

Run:

    make ffmpeg
    make

Using PiVT
---------------
Ensure you are logged in as a member of the video and audio groups, and there is
enough GPU memory set up to play video (64MB seems to work). Then do:

 ./PiVT --videosfolder /path/to/videos/folder/ --stopvideo /path/to/stopvideo.mp4

OMXPlayer
---------------
All credit to Edgar Hucek and Petr Baudis (and others!) for the underlying video playing
software, see http://github.com/huceke/omxplayer
