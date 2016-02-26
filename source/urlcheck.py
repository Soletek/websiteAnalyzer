import threading
import urllib
import time
import abc
import hashlib
import os
import codecs

from logger import FileLog

class UrlCheck(object):
    """handles a status check for a single http url"""

    def __init__(self, main_app, check_data):
        from scheduler import TimedCheck

        self.controller = main_app
        self.log = main_app.logger

        self.check_data = check_data
        self.url = check_data.target_url
        self.predicates = check_data.check_predicates
        
        self.thread = threading.Thread(None, self.update)
        self.thread.start()
        
        return super(UrlCheck, self).__init__()


    def update(self):
        self.server_status = False
        self.check_status = False

        #  hash from url, collisions are not currently checked
        self.hash = self.get_hash(self.url)
        self.dirname = self.controller.cache_dir + self.hash

        # configure logger
        if not self.check_data.disable_log:
            self.log.add_listener(FileLog(self.dirname + "\\.log").write_line, self.hash)

        self.message = "-"

        # create a folder if necessary
        if not os.path.isdir(self.dirname):
            os.makedirs(self.dirname)

        self.start_datetime = time.asctime()
        self.log.write_line (self.start_datetime + " -- starting a website check: " + self.url, self.hash)

        try:
            # get the web page and measure latency
            self.start_time = time.time()   # get a value in start_time in case urlopen fails
            self.web = urllib.urlopen(self.url)
            self.start_time = time.time()   # the real latency measurement start_time
            self.page = self.web.read()
            self.end_time = time.time()

        except Exception as e:
            # something went wrong with connection
            self.end_time = time.time()
            self.latency = self.end_time - self.start_time

            self.log.write_line ("exception when connectiong to the url: " + self.url, self.hash)
            self.message = str(e)
            self.log.write_line (self.message, self.hash)

        else:
            # connection succesfull
            self.server_status = True
            self.web.close()
            
            # calculate latency
            self.latency = self.end_time - self.start_time
            self.log.write_line ("Connected to " + self.url + " -- latency " + ('%.3f' % self.latency) + " s", self.hash)

            # cache page
            if not self.check_data.disable_page_caching:
                with open(self.dirname + "\\.html", "w") as f:
                    f.writelines(self.page)

            # change page encoding to ascii
            self.page = self.page.decode("ascii", "replace")
            self.content_check()
            

        self.write_meta()

        # finalize
        self.log.remove_channel(self.hash)
        self.controller.finalize_check(self)
        
        return


    def content_check(self):
        page_content_ok = True

        if (len(self.predicates) > 0):
            # iterate through all check predicates analyzing if page contents fulfills the conditionals
            for predicate in self.predicates:
                page_content_ok = page_content_ok and apply_predicate(predicate)

            if page_content_ok:
                self.message = "Check succesful."
                self.log.write_line (self.message, self.hash)

        else:
            self.message = "No content checks exist for this web page."
            self.log.write_line (self.message, self.hash)

        self.check_status = page_content_ok


    def apply_predicate(self, check_predicate):
        check_status = predicate.check_data(self.page)

        if not check_status:
            self.message = check_predicate.fail_message()
            self.log.write_line (self.message, self.hash)

        return check_status
                

    def write_meta(self):
        """ Writes meta data in file to be displayed in a web site """
        
        with open(self.dirname + "\\.meta", "w") as f:
            f.write(self.url + "\n")
            f.write(str(self.server_status) + "\n")
            f.write(str(self.check_status) + "\n")
            f.write(('%.3f' % self.latency) + " s\n")
            f.write(self.message + "\n")
            f.write(self.start_datetime + "\n")
            f.write("True\n")
            f.write(str(self.check_data.interval) + " s\n")

        return
            

    def get_hash(self, url):
        h = hashlib.new("md5")
        h.update(url)
        return h.hexdigest()




class SiteContentCheckBase(object):
    """abstract base class for all website content validity checks"""

    def __init__(self):
        return super(SiteContentCheckBase, self).__init__()

    @abc.abstractmethod
    def check_data(self, data):
        return

    def fail_message(self):
        return "Content check failed"


class ContainsStringCheck(SiteContentCheckBase):
    """checks if the page contains a certain phrase"""

    def __init__(self, data):
        self.__dict__ = data
        return super(ContainsStringCheck, self).__init__()

    def check_data(self, data):
        return data.find(self.phrase) != -1

    def fail_message(self):
        return "Content check failed: Phrase '" + self.phrase + "' not found."


class TitleCheck(SiteContentCheckBase):
    """checks if the web page title is correct"""

    def __init__(self, data):
        self.__dict__ = data
        return super(TitleCheck, self).__init__()

    def check_data(self, data):
        return data.find("<title>" + self.title + "</title>") != -1

    def fail_message(self):
        return "Content check failed: Web page title doesn't match '" + self.title + "'."




