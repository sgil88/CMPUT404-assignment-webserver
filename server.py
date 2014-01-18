import SocketServer
# coding: utf-8

# Copyright 2013 Abram Hindle, Eddie Antonio Santos, Bronte Lee, Stephanie Gil
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
#
# 

import os
class MyWebServer(SocketServer.BaseRequestHandler):

    def handle(self):
        """
        Handles the GET request from the client. If there are any errors,
        just sends 404 error.
        """
        self.data = self.request.recv(1024).strip()
        print ("Got a request of: %s\n" % self.data)
        
        # Getting directory path and file name from request
        rel_path, file_name = self.get_root()

        # If the directory path does not exist, display 404
        if rel_path == None:
            self.display_404()
            return

        # Getting html content either from html page user requested,
        # If no file in the directory was specified, from the GET 
        # request, gets index.html
        file_content = ""
        if file_name == None:
            file_name = "index.html"

        # Get the file content. If it doesn't exist, display 404
        file_content = self.get_page_content(rel_path, file_name)

        if file_content == None:
            self.display_404()
            return
       
        # Sending file content to client depending on whether it's .html or .css
        if ".html" in file_name:
            response = "HTTP/1.1 200 OK\r\nContent-Type:text/html\r\n\r\n"+ \
                file_content
            self.request.sendall(response)
        elif ".css" in file_name:
            response = "HTTP/1.1 200 OK\r\nContent-Type:text/css\r\n\r\n"+ \
                file_content
            self.request.sendall(response)
        else:
            self.display_404()
 
    def get_root(self):
        """
        Assuming there is always atleast one / after GET in the request string.
        Will return the directory path and the filename from the GET reqtuest.
        If the directory path doesn't exists, returns None. If the file name 
        was not given, returns None.
        """
        rel_path = "www/"

        lines = self.data.split("\n")
        first_line = lines[0]
        words = first_line.split(" ")
        directory_string = words[1]

        # Ignoring first element (empty space)
        path_parts = directory_string.split("/")[1:] 
        
        # Construct the path to the directory. If the file name was also given
        # in the GET request, return those from the function 
        for part in path_parts:
            if ".html" in part or ".css" in part:
                rel_path += "/"
                return rel_path, part
            else:
                rel_path += part + "/"

        # We just have a directory path, so check to see if the directory exists
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

    def display_404(self):
        """
        Sends an HTTP 404 error for the web browser to display
        """
        self.request.sendall("HTTP/1.1 404\r\n\r\n" + \
                             "<h1 style='text-align:center'>404 NOT FOUND </h1> " + \
                             "<p style='text-align:center'>The page you" + \
                             " requested was not found :)</p>")

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    SocketServer.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 9999
    server = SocketServer.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
