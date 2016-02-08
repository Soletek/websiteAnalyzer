import os

class Logger(object):
    """ Class for handling the log output 
        based on observer pattern and can handle multiple channels
    """

    def __init__(self):
        self.channels = {}
        self.channels["_GLOBAL"] = []
        return super(Logger, self).__init__()

    
    def write_line(self, line, channel="_GLOBAL"):
        # broadcast the message to all observers in the channel 
        # if the channel exists
        if channel in self.channels:
            for listener in self.channels[channel]:
                listener(line)

        # also broadcast to the global channel but not twice
        if (channel != "_GLOBAL"):
            for listener in self.channels["_GLOBAL"]:
                listener(line)
        
        return

    
    def add_listener(self, listener, channel="_GLOBAL"):
        # add a new channel if it doesn't exist
        if not self.channels.has_key(channel):
            self.channels[channel] = []

        self.channels[channel].append(listener)

        return

    
    def remove_listener(self, listener, channel="_GLOBAL"):
        try:
            self.channels[channel].remove(listener)

            # delete the channel if its empty
            if (len(self.channels[channel]) == 0):
                pass # TODO

        except (ValueError, KeyError):

            raise

        return

    def remove_channel(self, channel):
        """ removes a channel, deletes all listeners """

        try:
            self.channels[channel] = []
            del self.channels[channel]
        
        except KeyError:
            print "channel doesn't exist"



class FileLog(object):
    """ class used to write the log output into file """
    
    def __init__(self, filename):
        self.filename = filename
        self.mode = "a"

        # create a folder if necessary
        directory = os.path.dirname(self.filename)

        if not os.path.isdir(directory):
            os.makedirs(directory)

        return super(FileLog, self).__init__()

    def write_line(self, line):

        # quite bad implementation because file has to be reopened every time
        with open(self.filename, self.mode) as f:
            f.write(line + "\n")