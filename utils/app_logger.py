import os
import time
import gzip
import shutil
import logging
from logging.handlers import RotatingFileHandler


class CompressedRotatingFileHandler(RotatingFileHandler):
    def doRollover(self):
        """
        Do a rollover, as described in __init__().
        """
        if self.stream:
            self.stream.close()
        if self.backupCount > 0:
            for i in range(self.backupCount - 1, 0, -1):
                sfn = "%s.%d.gz" % (self.baseFilename, i)
                dfn = "%s.%d.gz" % (self.baseFilename, i + 1)
                if os.path.exists(sfn):
                    # print ("sfn-%s, dfn -> %s" % (sfn, dfn))
                    if os.path.exists(dfn):
                        os.remove(dfn)
                    os.rename(sfn, dfn)
            dfn = self.baseFilename + ".1.gz"
            # print (self.baseFilename, "<<<<<<< ")
            if os.path.exists(dfn):
                os.remove(dfn)
            # These two lines below are the only new lines. I commented out the os.rename(self.baseFilename, dfn) and
            #  replaced it with these two lines.
            with open(self.baseFilename, 'rb') as f_in, gzip.open(dfn, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
            # os.rename(self.baseFilename, dfn)
            # print "%s -> %s" % (self.baseFilename, dfn)
        self.mode = 'w'
        self.stream = self._open()

class _Logger:


    def __init__(self, app_name, log_dir, conf):
        self.log_path = log_dir
        self.log_format = conf.get("format", '%(asctime)s %(filename)s [line:%(lineno)d] %(levelname)s %(message)s')
        self.logformatter = logging.Formatter(fmt=self.log_format, datefmt='%Y-%m-%dT%H:%M:%S%z')
        print ("Log Path : %s" % self.log_path)
        if not os.path.exists(self.log_path): 
            try:
                os.makedirs(self.log_path)
            except:
                print ("Cannot create Log Directory - %s" % self.log_path)
        self.logger = logging.getLogger(app_name)
        self.logger.setLevel(conf.get("level", "INFO"))
        self.log_to_file = 1
        if self.log_to_file:
            file_logHandler = CompressedRotatingFileHandler(self.log_path + '%s.log' % app_name.lower(), 'a', maxBytes=1024*1024*int(conf.get("rotation", 20)), backupCount=int(conf.get("filecount", 20)))
            file_logHandler.setFormatter(self.logformatter)
            self.logger.addHandler(file_logHandler)
        self.log_to_console = int(conf.get("log_to_console", 0))
        if self.log_to_console:
            stream_handler = logging.StreamHandler()
            stream_handler.setFormatter(self.logformatter)
            self.logger.addHandler(stream_handler)
        
def initLogger(app_name, log_dir, conf):
    if "__logger" not in globals():
        logger = _Logger(app_name, log_dir, conf)
        globals()["__logger"] = logger.logger
    return globals()["__logger"]

def getLogger():
    try:
        return globals()["__logger"]
    except KeyError:
        return logging.getLogger(__file__)


if __name__ == '__main__':
    initLogger("test", "testlog", {})
    _logger = getLogger()
    tmp = "test msg test msg test msg test msg test msg test msg test msg "
    [_logger.info("%s XXXXXXXXXXXXXXXX %s - %s" % (x, time.time(), tmp)) for x in range(0,100)]