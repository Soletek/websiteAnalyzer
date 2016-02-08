# implements http server

import BaseHTTPServer
import SocketServer

import os

class HTTPRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):

    @classmethod
    def set_controller(cls, controller):
        HTTPRequestHandler.controller = controller
        return cls

    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

        return

    # handles GET request
    def do_GET(self):
        self.send_response(200)
           
        if (self.path == "/"):
            self.send_header("Content-type", "text/html")
            self.end_headers()

            with open("website\\index.html", "r") as html_file:
                self.wfile.writelines(html_file.readlines())

        elif (self.path.startswith("/log/")):
            filename = HTTPRequestHandler.controller.cache_dir + self.path.split("/")[-1] + "\\.log"
            print filename
            
            if (not os.path.isfile(filename)) or (self.path.count("/") > 2):
                self.send_header("Content-type", "text/plain")
                self.end_headers()
                self.wfile.writelines("404 NOT FOUND")

            else:
                self.send_header("Content-type", "text/plain")
                self.end_headers()
                with open(filename, "r") as html_file:
                    self.wfile.writelines(html_file.readlines())


        elif (self.path.startswith("/page/")):
            filename = HTTPRequestHandler.controller.cache_dir + self.path.split("/")[-1] + "\\.html"

            if (not os.path.isfile(filename)) or (self.path.count("/") > 2):
                self.send_header("Content-type", "text/plain")
                self.end_headers()
                self.wfile.writelines("404 NOT FOUND")

            else:
                self.send_header("Content-type", "text/html")
                self.end_headers()
                with open(filename, "r") as html_file:
                    self.wfile.writelines(html_file.readlines())
            
        
        elif (self.path == "/data"):
            self.send_header("Content-type", "text/html")
            self.end_headers()

            # table header
            self.wfile.write("<table style='width:100%'><tr><td><b>URL</b></td><td><b>Server status</b></td><td><b>Page status</b>" +
                             "</td><td><b>Latency</b></td><td><b>Status message</b></td><td><b>Latest check</b></td><td><b>Currently " +
                             "monitored</b></td><td><b>Check interval</b></td><td><b>Log</b></td><td><b>Page cache</b></td></tr>")

            # list all monitored URLs in the table
            for dir in os.walk(HTTPRequestHandler.controller.cache_dir):
                if os.path.isfile(dir[0] + "\\.meta"):
                    with open(dir[0] + "\\.meta", "r") as f:
                        hash = dir[0].split("\\")[-1]
                        lines = f.readlines()

                        # remove the '\n' at end of every line
                        for i in range(0, len(lines)):
                            if lines[i].endswith("\n"):
                                lines[i] = lines[i][:-1]

                        # parse data into html
                        if (len(lines) >= 7):
                            self.wfile.write("<tr>")

                            # URL
                            self.wfile.write("<td><a href='" + lines[0] + "'>" + lines[0] +"</a></td>")

                            # Server status
                            if lines[1] == "True":
                                self.wfile.write("<td><h3>ONLINE</h3></td>")
                            else:
                                self.wfile.write("<td><h2>OFFLINE</h2></td>")

                            # Page content status
                            if lines[2] == "True":
                                self.wfile.write("<td><h3>OK</h3></td>")
                            else:
                                self.wfile.write("<td><h2>FAILED</h2></td>")

                            # Latency
                            if lines[1] == "True":
                                self.wfile.write("<td>" + lines[3] + "</td>")
                            else:
                                self.wfile.write("<td>-</td>")

                            # Status message
                            self.wfile.write("<td>" + lines[4] + "</td>")

                            # Check date
                            self.wfile.write("<td>" + lines[5] + "</td>")

                            # Currently monitored and iterval
                            if lines[6] == "True":
                                self.wfile.write("<td><b>YES</b></td>")
                                self.wfile.write("<td>" + lines[7] + "</td>")
                            else:
                                self.wfile.write("<td><b>NO</b></td>")
                                self.wfile.write("<td>-</td>")

                            # Log file
                            if os.path.isfile(dir[0] + "\\.log"):
                                self.wfile.write("<td><a href='log/" + hash + "'>View log</a></td>")
                            else:
                                self.wfile.write("<td><i>Log disabled</i></td>")

                            # Cached page
                            if os.path.isfile(dir[0] + "\\.html"):
                                self.wfile.write("<td><a href='page/" + hash + "'>View latest cached page</a></td>")
                            else:
                                self.wfile.write("<td><i>Page caching disabled</i></td>")

            self.wfile.write("</table>")
        
        else:
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.writelines("404 NOT FOUND")

        return


    
class HTTPServer(object):
    
    def __init__(self, main_app, port):
        self.controller = main_app
        self.port = port

        return super(HTTPServer, self).__init__()

    def update(self):
        self.controller.logger.write_line("Opening HTTP server at port: " + str(self.port))
        self.server = SocketServer.TCPServer(("", self.port), HTTPRequestHandler.set_controller(self.controller))
        self.server.serve_forever()

        return