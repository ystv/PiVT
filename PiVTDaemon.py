import sys

from daemon import Daemon
import PiVT

class PiVTDaemon(Daemon):
    def run(self):
        PiVT.main()

    
if __name__ == "__main__":
    daemon = PiVTDaemon('/tmp/pivt.pid')
    if len(sys.argv) >= 2:
        command = sys.argv[1]
        opts = sys.argv
        opts.pop(1)
        sys.argv = opts
        
        if 'start' == command:
            daemon.start()
        elif 'stop' == command:
            daemon.stop()
        else:
            print "Unknown command"
            sys.exit(2)
        sys.exit(0)
    else:
        print "usage: %s start|stop" % sys.argv[0]
        sys.exit(2)