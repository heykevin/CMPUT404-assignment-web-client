#!/usr/bin/env python
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
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

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib
import urlparse
from itertools import takewhile, dropwhile


def help():
    print "httpclient.py [GET/POST] [URL]\n"


class HTTPResponse(object):
    def __init__(self, code=200, message="OK", headers="", body=""):
        self.code = code
        self.message = message
        self.body = body
        self.headers = headers


class HTTPClient(object):
    #def get_host_port(self,url):
    def connect(self, host, port=80):
        # use sockets!

        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clientSocket.connect((self.host, port))
        clientSocket.sendall(self.createRequest())
        res = self.recvall(clientSocket)
        if res:
            print res
        return self.createResponse(res)

    def get_code(self):
        return None

    def get_headers(self):
        return None

    def get_body(self):
        return ""

    def createResponse(self, res):
        rawheaders = res.split("\r\n")
        print rawheaders

        # test for empty headers/body
        try:
            print rawheaders[0].split(" ", 2)
            protocol, code, message = rawheaders[0].split(" ", 2)
            headers = dict(item.split(": ", 1) for item in takewhile(lambda s: s != '', rawheaders[1:]))
            body = "".join(list(dropwhile(lambda s: s != '', rawheaders[1:])))
        except ValueError as e:
            print e
        return HTTPResponse(code, message, headers, body)

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return str(buffer)

    def createRequest(self):
        rawheaders = {
            "Host": self.host,
            "User-Agent": "Custom Agent",
            "Accept": "*/*",
            "Connection": "close"
        }
        headers = "".join("%s: %s\r\n" % (k, v) for k, v in rawheaders.iteritems())
        return "%s %s HTTP/1.1\r\n%s\r\n%s" % (self.method, self.path, headers, self.get_body)

    def setPath(self, url):
        prefix = "http://"
        if not url.startswith(prefix):
            url = prefix + url
        tokens = urlparse.urlparse(url)
        print tokens

        self.host = tokens.netloc
        self.path = "/" if tokens.path == "" else tokens.path
        self.params = tokens.params
        self.query = tokens.query

    # Combine GET and POST
    def GET(self, url, args):
        self.setPath(url)
        return self.connect(url, 80)

    def POST(self, url, args=None):
        code = 500
        body = ""
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        print(url, command, args)

        if not (command == "GET" or command == "POST"):
            return "Error"
        self.method = command
        self.GET(url, args)

if __name__ == "__main__":
    client = HTTPClient()
    print sys.argv;
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print client.command(sys.argv[2], sys.argv[1])
    else:
        print client.command(sys.argv[1])
