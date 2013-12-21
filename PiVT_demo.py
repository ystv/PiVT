from OMXControl import OMXControl 
from time import sleep
if __name__ == '__main__':
    # Launch a simple player
    test1 = OMXControl(['/videos/Monday_Evening_Live_Titles_HD.mp4', '-s', '--no-osd', '--win', "0 0 1920 1080"])
    
    while (test1.get_ready() != True):
        pass
    
    test1.play()
    
    sleep(2)
    
    test2 = OMXControl(['/videos/James_Bungee_Jump_Export.mp4', '-s', '--no-osd', '--win', "0 0 1920 1080"])
    while (test2.get_ready() != True):
        pass
    test3 = OMXControl(['/videos/shortclock.mp4', '-s', '--no-osd', '--win', "0 0 1920 1080"])

    while (test1.get_position() < 11.9):
        print test1.get_position()

    test1.pause()
    test2.play()
    print test1.get_position()

    test1.stop()
    
    sleep(3)
    del test1
    sleep(1)
    test4 = OMXControl(['/videos/FreshersLookback.mp4', '-s', '--no-osd', '--win', "0 0 1920 1080"])
    while (test4.get_ready() != True):
        pass
    test2.pause()
    test4.play()
    test2.stop()

    while (test4.get_position() < 10):
        pass
    test4.pause()
    test3.play()
    
    sleep(10)
    test4.stop()
    test3.stop()
    del test4
    del test2
    del test3
    
