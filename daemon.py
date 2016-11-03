
import os
import sys
import getopt
import logging
import logging.handlers
import resource

class Daemon:
    BACKGROUND = False
    PIDFILE = None
    LOGFILE = None
    LOGDIR = "/tmp"
    APPNAME = None
    CONFIGFILE = None
    LOGLVL = logging.INFO

    def __init__(self):
        self.logger = None

    def usage(self):
        print """Usage: %s [-b] [-p pidfile] [-l logfile]
""" % sys.argv[0]
        sys.exit(1)

    def run(self):
        pass

    def log(self, message, lvl=logging.INFO):
        self.logger.log(lvl, message)
    def log_debug(self, message):
        self.logger.debug(message)
    def log_info(self, message):
        self.logger.info(message)
    def log_err(self, message):
        self.logger.error(message)
    def log_exc(self, message):
        self.logger.exception(message)

    def daemonize(self):
        # run in the background
        try:
            pid = os.fork()
        except OSError, e:
            raise Exception("%s [%d]" % (e.strerror, e.errno))
        if pid == 0:
            os.setsid()
            try:
                pid = os.fork()
            except OSError, e:
                raise Exception("%s [%d]" % (e.strerror, e.errno))

            if pid == 0:
                os.chdir("/")
                os.umask(0)
            else:
                os._exit(0)
        else:
            os._exit(0)
        # we're now double-forked, clean up
        maxfd = resource.getrlimit(resource.RLIMIT_NOFILE)[1]
        if maxfd == resource.RLIM_INFINITY:
            maxfd = 1024
        for fd in range(0, maxfd):
            try:
                os.close(fd)
            except OSError:
                pass
        # redirect std handles to /dev/null
        os.open("/dev/null", os.O_RDWR)
        os.dup2(0, 1)
        os.dup2(0, 2)

    def main(self):
        if self.APPNAME is None:
            self.APPNAME = __name__

        try:
            opts, files = getopt.getopt(sys.argv[1:], "bp:l:c:v")
        except getopt.GetoptError:
            self.usage()
            sys.exit(127)

        for opt, arg in opts:
            if opt == '-b':
                self.BACKGROUND = True
            elif opt == '-p':
                self.PIDFILE = arg
            elif opt == '-l':
                self.LOGFILE = arg
            elif opt == '-c':
                self.CONFIGFILE = arg
            elif opt == '-v':
                self.LOGLVL = logging.DEBUG

        if self.BACKGROUND:
            self.daemonize()
        if self.PIDFILE:
            fp = open(self.PIDFILE,'w')
            fp.write("%d\n" % os.getpid())
            fp.close()

        ## Set up logging
        self.logger = logging.getLogger('log')
        self.logger.setLevel(self.LOGLVL)

        # Destination file
        if self.BACKGROUND or self.LOGFILE:
            filename = os.path.join(self.LOGDIR, self.APPNAME)
            if self.LOGFILE:
                filename = self.LOGFILE
            handler = logging.handlers.RotatingFileHandler(filename,
                                                           maxBytes=1048576,
                                                           backupCount=5)
        else:
            # not backgrounded
            handler = logging.StreamHandler()

        # Set up formatting
        formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
        handler.setFormatter(formatter)

        self.logger.addHandler(handler)

        # go!
        self.run()
