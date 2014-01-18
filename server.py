import SocketServer
# coding: utf-8

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/

import os
class MyWebServer(SocketServer.BaseRequestHandler):

    def handle(self):
        self.data = self.request.recv(1024).strip()
        print ("Got a request of: %s\n" % self.data)
        if "favicon" in self.data:
            return
        
        # getting dir path and html file name from request
        rel_path, file_name = self.get_root()
        if rel_path == None:
            display_404()
            return

        # getting html content either from html page user requested,
        # or if none was specified, gets index.html
        file_content = ""
        if file_name != None:
            file_content = self.get_page_content(rel_path, file_name)
        else:
            file_name = "index.html"
            file_content = self.get_page_content(rel_path, file_name)
        if file_content == None:
            display_404()
            return

        # sending html content to client
        response = "HTTP/1.1\r\n" \
            + "Content-Type:text/html\r\n\r\n" \
            + file_content
        self.request.sendall(response)
        
        if ".html" in file_name:
            # sending css content to client
            css_content = self.get_css(file_content, rel_path)
            response = "HTTP/1.1\r\n" \
                + "Content-Type:text/css\r\n\r\n" \
                + css_content
            self.request.sendall(response)
 
    def get_root(self):
        """
        Assuming there is always atleast one / after GET in the request string
        """
        rel_path = "www/"

        lines = self.data.split("\n")
        first_line = lines[0]
        words = first_line.split(" ")
        url_string = words[1]

        # ignoring first element (empty space)
        path_parts = url_string.split("/")[1:] 
        
        for part in path_parts:
            if part == "":
                pass
            elif ".html" in part or ".css" in part:
                rel_path += "/"
                return rel_path, part
            else:
                rel_path += part + "/"
        if os.path.exists(rel_path):
            return rel_path, None
        else:
            return None, None

    def get_page_content(self, rel_path, name):
        """
        Retrieves the content of an html page or a css page and returns it as
        a string, or, if there was an error, returns None.
        """
        try:
            page = open(rel_path+name)
            file_content = ""
            for line in page:
                file_content += line
            page.close()
            return file_content
        except:
            return None

    def get_css(self, html_string, rel_path):
        """
        Returns the css content to style the html page that the client wants to
        view. If there is no css file, or if there was an error, then None is 
        returned.
        """
        file_content = html_string.split('\n')
        try:
            for line in file_content:
                if ("text/css" in line):
                    line = line.strip()
                    line = line.replace('<', '')
                    line = line.replace('>','')
                    line = line.replace('"', '')
                    elements = line.split()[1:]
                    
                    tags = {}
                    for e in elements:
                        values = e.split("=")
                        tags[values[0]] = values[1]

                    for tag, value in tags.iteritems():
                        if tag == "href":
                            file = open(rel_path+value)
                            css_content = ""
                            for css_line in file:
                                css_content += css_line
                            file.close()
                            return css_content
        except:
            return None

    def display_404():
        """
        Sends an HTTP 404 error for the web browser to display
        """
        self.request.sendall("HTTP/1.1 404\r\n\r\nThe file you" \
                                 + " requested was not found :)")

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    SocketServer.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 9999
    server = SocketServer.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
