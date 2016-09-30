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
        self.code = int(code)
        self.message = message
        self.body = body
        self.headers = headers


class HTTPClient(object):
    #def get_host_port(self,url):
    def connect(self, host, args):
        # use sockets!
        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clientSocket.connect((self.host, self.port))
        clientSocket.sendall(self.createRequest(args))
        print self.createRequest(args)
        res = self.recvall(clientSocket)
        return self.createResponse(res)

    def createResponse(self, res):
        rawheaders = res.split("\r\n")
        # test for empty headers/body
        try:
            protocol, code, message = rawheaders[0].split(" ", 2)
            headers = dict(item.split(": ", 1) for item in takewhile(lambda rawres: rawres != '', rawheaders[1:]))
            body = "".join(list(dropwhile(lambda rawres: rawres != '', rawheaders[1:])))
        except ValueError as e:
            print "ValueError: %s" % e
        # print "response is "
        # print [protocol, code, message, headers, body]
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

    def createRequest(self, args=None):
        rawheaders = {
            "Host": "%s:%i" % (self.host, self.port),
            "User-Agent": "Custom Agent",
            "Accept": "*/*",
            "Connection": "close" 
        }
        body = None
        if self.method == "GET":
            if args:
                self.path += "&" if self.query else "?" + urllib.urlencode(args)
            elif self.query:
                self.path += "?" + self.query

        #encode arguments and path?
        if self.method == "POST":
            rawheaders["Content-Type"] = "application/x-www-form-urlencoded"
            body = urllib.urlencode(args) if args else ""
            rawheaders["Content-Length"] = len(body)
        headers = "".join("%s: %s\r\n" % (k, v) for k, v in rawheaders.iteritems())
        return "%s %s HTTP/1.1\r\n%s\r\n%s" % (self.method, self.path, headers, body or "")

    def setPath(self, url):
        prefix = "http://"
        if not url.startswith(prefix):
            url = prefix + url
        tokens = urlparse.urlparse(url)
        # print tokens
        try:
            self.host = tokens.netloc.split(":")[0]
            self.port = int(tokens.netloc.split(":")[1])
        except:
            self.host = tokens.netloc
            self.port = 80

        self.path = "/" if tokens.path == "" else tokens.path
        self.params = tokens.params
        self.query = tokens.query

    # Combine GET and POST
    def GET(self, url, args=None):
        self.method = "GET"
        self.setPath(url)
        return self.connect(url, args)

    def POST(self, url, args=None):
        self.method = "POST"
        self.setPath(url)
        return self.connect(url, args)


    def command(self, url, command="GET", args=None):
        if not (command == "GET" or command == "POST"):
            return "Error"
        if (command == "POST"):
            return self.POST(url, args)
        else:
            return self.GET(url, args)

if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    if (len(sys.argv) == 3):
        print client.command(sys.argv[2], sys.argv[1])
    else:
        print client.command(sys.argv[1])
