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


class MyWebServer(SocketServer.BaseRequestHandler):

    def handle(self):
        self.data = self.request.recv(1024).strip()
        print ("Got a request of: %s\n" % self.data)
        
        rel_path = self.get_root()
        html_content = self.get_indexhtml(rel_path)
        for line in html_content:
            self.request.sendall(line)

        css_content = self.get_css(html_content, rel_path)
#        print (css_content)
#        for line in css_content:
#            self.request.sendall(line)
        

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
            else:
                if (".css" in part) or (".html" in part):
                    pass
                else:
                    rel_path += part + "/"
        
        return rel_path

    def get_indexhtml(self, rel_path):
        try:
            index = open(rel_path+"index.html")
            html_content = []
            for line in index:
                html_content.append(line)
            index.close()
            return html_content
        except:
            print ("404 error")
            return "404"

    def get_css(self, html_content, rel_path):
        try:
            for line in html_content:
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
                            css_content = []
                            for css_line in file:
                                css_content.append(css_line)
                            file.close()
                            return css_content
        except:
            return "404-css" 

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    SocketServer.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 9999
    server = SocketServer.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
