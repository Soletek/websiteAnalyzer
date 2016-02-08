
import time
import json
import os

from urlcheck import *


class CheckScheduler(object):
    """ Performs periodical checks on web pages """

    def __init__(self, main_app, filename):
        # the main application, handles events
        self.controller = main_app

        # a list of checks scheduled to be performed
        self.scheduled_checks = self.get_scheduled_checks(filename)
        
        self.running = True
        return super(CheckScheduler, self).__init__()


    def get_scheduled_checks(self, filename):
        """ Reads scheduled checks from json file """

        checks = []

        with open(filename, "r") as f:
            checks = json_deserialize(json.loads(f.read()))

        return checks

    
    def update(self):
        """ Runs scheduled checks on web pages """

        self.update_sites_monitored_status()

        while self.running:
            for check in self.scheduled_checks:
                if check.update( time.time() ):
                    self.controller.perform_check(check)

                    # small wait between connections because the simultaneous 
                    # fetching was affecting the latency measurement
                    time.sleep(0.5)

            time.sleep(2.0)

        return

    
    def save_current_check_schedule(self):
        """ Saves the currently running scheduled check configuration to a file """

        with open("config\\schedule.json", "w") as f:
            f.write(json.dumps(self.scheduled_checks, default=json_serialize, sort_keys=True, indent=2))

        return

    
    def update_sites_monitored_status(self):
        """ Update the currently monitored attribute in meta file for every site 
            This operation might be costly with a lot of saved pages
        """

        # fetch all URLs from file system
        all_urls = []
        for dir in os.walk(self.controller.cache_dir):
            if os.path.isfile(dir[0] + "\\.meta"):
                with open(dir[0] + "\\.meta", "r") as f:
                    all_urls.append((f.readline()[:-1], dir[0] + "\\.meta"))

        # construct a dict of all currently monitored URLs and check intervals
        monitored_urls = {}
        for check in self.scheduled_checks:
            monitored_urls[check.target_url] = check.interval

        # update the currently monitored status and interval value
        for page in all_urls:
            with file(page[1], "r") as f:
                lines = f.readlines()

                try:
                    if monitored_urls.has_key(page[0]):
                        lines[6] = "True\n"
                        lines[7] = str(monitored_urls[page[0]]) + " s\n"
                        del monitored_urls[page[0]]

                    else:
                        lines[6] = "False\n"
                        lines[7] = "-\n"

                except IndexError:
                    # file contents are not valid
                    pass

            with file(page[1], "w") as f:
                f.writelines(lines)

        return


class TimedCheck(object):
    """class for scheduled checks"""
    
    def __init__(self, data):
        self.__dict__ = data
        self.last_check = time.time()

        return super(TimedCheck, self).__init__()

    
    def set(self, url, interval = 0, predicates = []):
        self.interval = interval
        self.target_url = url
        self.check_predicates = predicates
        self.last_check = time.time()
        self.disable_log = False
        self.disable_page_caching = False

        return

 
    def update(self, time):
        """ returns true if the check is to be performed """
        
        if (self.last_check + self.interval < time):
            self.last_check = time
            return True

        return False


def json_serialize(obj):
    """returns json serializable interpretation of an object"""

    typename = type(obj).__name__

    # ignore Thread objects
    if (typename != "Thread"):
        dict = obj.__dict__.copy()
        dict["_class_name"] = typename
    else:
        dict = None
    
    return dict


def json_deserialize(data):
    """ Recusively deserializes json and constructs an object tree
        param data: data structure returned by json.read()
        returns: the
    """

    if type(data) is list:
        list_object = []

        # recurisvely deserialize all indexes
        for list_element in data:
            list_object.append(json_deserialize(list_element))

        return list_object
    
    elif type(data) is dict:
        # check all indexes for possible hierarchies
        for key in data:
            data[key] = json_deserialize(data[key])

        # if dict represents an object deserialize and construct it
        # for a class to be deserializable, it has to have an constructor
        # with dict parameter
        try:
            class_object = eval(data["_class_name"])

            # delete the obsolete class name attribute 
            del data["_class_name"]
            return class_object(data)
            
        # the dict doesn't represent an object
        except KeyError:
            return data

        except NameError:
            print "Invalid class name: " + data["_class_name"]

    else:
        # data is neither list or dict, do nothing
        return data


