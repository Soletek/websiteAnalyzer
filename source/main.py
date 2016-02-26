# Website status monitoring tool
# 
# Tuukka Kurtti 2016
# python version 2.7 (tested with 2.7.11)

import time
import sys
from ConfigParser import ConfigParser
from msvcrt import getch
import threading

from logger import Logger, FileLog
from urlcheck import *
from scheduler import *
from httpserver import HTTPServer

# main application class
class WebsiteStatusApp(object):
    """recieves events from threads"""

    instance = None

    def __init__(self):
        self.logger = Logger()
        self.active_checks = []
        WebsiteStatusApp.instance = self

        return super(WebsiteStatusApp, self).__init__()

    @classmethod
    def get_instance(cls):
        if (WebsiteStatusApp.instance == None):
            WebsiteStatusApp.instance = WebsiteStatusApp()

        return WebsiteStatusApp.instance

    
    def run(self):

        self.load_config()

        if self.config.getboolean("configuration", "mainlog"):
            self.logger.add_listener(FileLog(self.log_file).write_line)
        
        if self.config.getboolean("configuration", "checkscheduler"):
            self.start_check_scheduler()

        if self.config.getboolean("configuration", "httpserver"):
            self.start_HTTPServer()
        
        if self.config.getboolean("configuration", "commandpromt"):
            self.start_command_prompt()
            
            # wait for console to exit
            self.console_thread.join()
        else:
            listen_to_log_output(False)

        
        print "Shutting down internal processes..."
        self.stop_check_scheduler()
        self.stop_HTTPServer()

        return

    def load_config(self):
        # load setup from config.ini

        self.config = ConfigParser()
        self.config.read("config\\config.ini")

        self.schedule_file = config.get("checkScheduler", "database")
        self.server_port = config.getint("HTTPServer", "port")
        self.log_file = config.get("log", "dir") + "log.txt"
        self.cache_dir = config.get("log", "pagedir")

        return

    def start_command_prompt(self):
        # create a thread for the console interface

        self.console_thread = threading.Thread(None, update_console, "console")
        self.console_thread.start()
            
        return

    def start_check_scheduler(self):
        # create a thread for automated url checks

        self.scheduler = CheckScheduler(self, self.schedule_file)
        self.check_scheduler_thread = threading.Thread(None, self.scheduler.update, "scheduler")
        self.check_scheduler_thread.start()

        return

    def stop_check_scheduler(self):
        try:
            self.scheduler.running = False;
        except AttributeError:
            pass

        return
            
    def start_HTTPServer(self):
        # create a thread for http server interface

        self.server = HTTPServer(self, self.server_port)
        self.server_thread = threading.Thread(None, self.server.update, "httpServer")
        self.server_thread.start()

        return

    def stop_HTTPServer(self):
        try:
            self.server.server.shutdown()
        except AttributeError:
            pass

        return
            
    def perform_check(self, check_data):
        # initiates a check on a specific url address,
        # the connection and checks runs on seperate thread

        self.active_checks.append(UrlCheck(self, check_data))

        return


    def finalize_check(self, check):
        self.active_checks.remove(check)

        return




# console interface update
def update_console():
    print "type '?' for list of available commands."
    controller = WebsiteStatusApp.get_instance()

    while True:
        command = raw_input("command --> ")

        try:
            if (command == "?"):
                show_help_dialog()
        
            elif (command == "listen"):
                listen_to_log_output()

            elif (command == "status"):
                print "not implemented"

            elif (command == "quit"):
                return

            else:
                print "Unknown command."

        except:
            print "ERROR"
        
# prints list of available commands
def show_help_dialog():
    print "Available commands:"
    print ""
    print "     '?' = show this help"
    print "'listen' = listen to log output"
    print "'status' = view program status"
    print "  'quit' = stop all processes and exit"
    print ""



def listen_to_log_output(interruptable=True):
    # prints log output to screen until Keyboard Interrupt

    log = WebsiteStatusApp.get_instance().logger
    log.add_listener(print_log)

    while (getch() == 0 and interruptable):
        time.sleep(0.1)

    log.remove_listener(print_log)

     
def print_log(line):
    print line



# entry point to the application
if __name__ == "__main__":

    # initialize the main application controller Class
    main_app = WebsiteStatusApp()
    main_app.run()

    sys.exit(0)


