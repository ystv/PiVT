from OMXControl import OMXControl
from time import sleep

if __name__ == '__main__':
    # Launch a simple player
    test1 = OMXControl(['/videos/Monday_Evening_Live_Titles_HD.mp4', '-s', '--no-osd'])
    
    while (test1.get_ready() != True):
        pass
    
    test1.play()
    
    sleep(2)
    
    test2 = OMXControl(['/videos/James_Bungee_Jump_Export.mp4', '-s', '--no-osd'])
    
    while (test1.get_position() < 12):
        print test1.get_position()
    
    test1.pause()
    test2.play()
    test1.stop()
    
    sleep(10)
    del test1
    test1 = OMXControl(['/videos/FreshersLookback.mp4', '-s', '--no-osd'])
    while (test1.get_ready() != True):
        pass
    test1.play()
    test2.pause()
    test2.stop()
    
    sleep(50)
    test1.stop()
    del test1
    del test2
    