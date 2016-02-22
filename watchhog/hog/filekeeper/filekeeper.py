import os
import logging
import unittest


def readall(fd):
    data = ''
    while True:
        chunk = os.read(fd, 4096)
        if chunk == '': return data
        data += chunk

class FileKeeper(object):
    def __init__(self):
        self.filehandles = {}

    def read(self, filename):

        if filename in self.filehandles:
            logging.debug('[FileKeeper] file "%s" metadata found in cache' % filename)
            (stat, fd) = self.filehandles[filename]

            logging.debug('[FileKeeper] SAVED STAT "%s" ino=%d size=%d' % (filename, stat.st_ino, stat.st_size))

            # At this point nothing could happen with already opened file even if someone deleted it.
            # Read it to the end
            try:
                data = readall(fd)
            except OSError as e:
                logging.debug('[FileKeeper] Error reading file "%s": %s' % (filename, str(e)))
                return ''
            except IOError as e:
                logging.debug('[FileKeeper] Error reading file "%s": %s' % (filename, str(e)))
                return ''

            try:
                new_stat = os.stat(filename)
            except:
                logging.error('[FileKeeper] Error stating file "%s": %s' % (filename, str(e)))
                return data

            logging.debug('[FileKeeper] REAL STAT "%s" ino=%d size=%d' % (filename, new_stat.st_ino, new_stat.st_size))

            self.filehandles[filename] = (new_stat, fd)
            logging.debug('[FileKeeper] File handle for "%s" was saved' % filename)

            if new_stat.st_ino != stat.st_ino or new_stat.st_size < stat.st_size:
                # We reach here after logrotate for example:
                # file was moved or deleted and another one is in his place or file was truncated
                os.close(fd)
                del(self.filehandles[filename])
                if new_stat.st_ino != stat.st_ino:
                    logging.debug('[FileKeeper] file "%s" inode was changed' % filename)
                else:
                    logging.debug('[FileKeeper] file "%s" was truncated' % filename)

                try:
                    fd = os.open(filename, os.O_RDONLY)
                except OSError as e:
                    logging.error('[FileKeeper] Error opening file "%s": %s' % (filename, str(e)))
                    return data

                try:
                    data += readall(fd)
                except OSError as e:
                    logging.debug('[FileKeeper] Error reading file "%s": %s' % (filename, str(e)))
                    return data
                except IOError as e:
                    logging.debug('[FileKeeper] Error reading file "%s": %s' % (filename, str(e)))
                    return data

            return data

        else:
            logging.debug('[FileKeeper] First time file access for "%s"' % filename)
            try:
                fd = os.open(filename, os.O_RDONLY)
                stat = os.stat(filename)
                logging.debug('[FileKeeper] file "%s" stat: %s' % (filename, str(stat)))
            except OSError as e:
                logging.error('[FileKeeper] Error opening file "%s": %s' % (filename, str(e)))
                return ''

            # First time we're not reading the file contents, just seeking the end of file
            # to read the new data the next iteration
            os.lseek(fd, 0, os.SEEK_END)
            self.filehandles[filename] = (stat, fd)
            logging.debug('[FileKeeper] File handle for "%s" was saved' % filename)
            return ''

filekeeper = FileKeeper()

class FileKeeperTest(unittest.TestCase):
    def test_filekeeper(self):
        logging.basicConfig(level=logging.DEBUG)
        import tempfile

        keeper = FileKeeper()
        fname = tempfile.mkstemp()[1]
        LOGLINES = [
            'Feb 19 11:35:11 37 softwareupdate_notify_agent[21275]: Running for UpdatesAvailable',
            'Feb 19 11:35:11 37 softwareupdate_notify_agent[21275]: AssertionMgr: Take com.apple.softwareupdate.NotifyAgentAssertion assertion with type BackgroundTask for pid 21275',
            'Feb 19 11:35:11 37 softwareupdate_notify_agent[21275]: Waiting 120 seconds before sending the notification to App Store'
        ]

        writer = open(fname, "w")
        writer.write(LOGLINES[0]+"\n")
        writer.flush()


        data = keeper.read(fname)
        self.assertEqual(data, '')

        writer.write(LOGLINES[1]+"\n")
        writer.flush()
        data = keeper.read(fname)
        self.assertEqual(data, LOGLINES[1]+"\n")

        logging.debug("[Test]: Writing file from the begining")
        writer = open(fname, "w")
        writer.truncate(0)
        writer.write(LOGLINES[2]+"\n")
        writer.flush()
        data = keeper.read(fname)
        self.assertEqual(data, LOGLINES[2]+"\n")

if __name__ == '__main__':
    unittest.main()

