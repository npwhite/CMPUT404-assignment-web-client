#!/usr/bin/env python3
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

# TODO:
# * when no path passed, errs ex.) https://stackoverflow.com requires https://stackoverflow.com/
# * posting args in form args = {'a':'aaaaaa', 'd':'012345\r67890\n2321321\n\r'}
# * prop licence

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse as prs


def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

    def __str__(self):
        return self.body

# example
#
# GET /wiki/David_H._Turpin HTTP/2
# Host: en.wikipedia.org
# User-Agent: curl/7.54.0
# Accept: */*
""" Modified code from previous assignment """
class Request():

    def __init__(self, method, path, http_version, host, user_agent, accept):
        self.method = method
        self.path = path
        self.http_version = http_version
        self.header_dic = {
        "Host":host,
        "User-Agent":"curl/7.54.0",
        "Accept":"*/*"
        }
        self.body = ''        # optional, but used for posts



    def header_to_string(self):
        """
        Converts header_dic into a formatted sendable string string
        """
        # header_string = self.method + self.path + self.http_version + "\r\n"
        # header_string = b''
        header_string = f"{self.method} {self.path} {self.http_version}\r\n"

        for key, value in self.header_dic.items():
            if value is not None:
                header_string += "{0}: {1}\r\n".format(key, value)
        header_string += "\r\n"
        return header_string


    def request_string(self):
        return self.header_to_string() + self.body





class HTTPClient(object):
    #def get_host_port(self,url):

    def connect(self, host, port):
        # if LOCALHOST:
        #     host = host.split(":")[0]  # needed for localhost connection for now
        # print(host)
        # print(port)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def parse_url(self, url):
        scheme, netloc, path, params, query, fragment = prs.urlparse(url)
        if path == '':
            path = '/'
        if ':' in netloc:
            host, port = netloc.split(':')
        else:
            host, port = netloc, 80 # just default to 80 I think

        return (host, int(port), path)

    """ returns integer """
    def get_code(self, data):
        #print("----- DEBUG ------")
        # print(data)
        header_l1 = data.split('\r\n')[0]
        http_version, code, msg = header_l1.split(' ', 2)
        # print(f"CODE{code}")
        return int(code)

    def get_headers(self,data):
        return None

    def get_body(self, data):
        return None

    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))

    def close(self):
        # print()
        # print("closing socket...")  # TODO: remove this probably
        # print()
        self.socket.close()

    # read everything from the socket
    # def recvall(self, sock):
    def recvall(self):
        buffer = bytearray()
        done = False
        while not done:
            part = self.socket.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def send_request(self, host, port, req_obj):
        # scheme, netloc, path, params, query, fragment = prs.urlparse(url)
        # host, port, path = self.parse_url(url)

        # req_obj = Request(method, path, "HTTP/1.0", host, "curl/7.54.0", "*/*")
        req_str = req_obj.request_string()
        print()
        print("*--- REQUEST STRING ---*")
        print(req_str)
        print()

        self.connect(host, port)
        self.sendall(req_str)
        data = self.recvall()
        print("---- DATA ----")
        print(data)
        self.close()

        code = self.get_code(data)
        # print(code)
        body = data.split("\r\n\r\n")[1]
        return (code, body)

    def dic_to_urlencoded(self, args):
        """
        Converts a key-value dictionary into urlencoded post format a=b&c=d etc
        Arguments:
            * args : dic
        Return
            * undeclared : string
        """
        s = "&"
        l1 = [f"{item[0]}={item[1]}" for item in args.items()]
        return s.join(l1)



    def GET(self, url, args=None):
        host, port, path = self.parse_url(url)
        req_obj = Request("GET", path, "HTTP/1.0", host, "curl/7.54.0", "*/*")

        code, body = self.send_request(host, port, req_obj)
        # print("---GET BODY---")
        # print(body)
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        host, port, path = self.parse_url(url)
        req_obj = Request("POST", path, "HTTP/1.0", host, "curl/7.54.0", "*/*")
        req_obj.header_dic["Content-Type"] = "application/x-www-form-urlencoded"

        if args is not None:
            # body = self.dic_to_urlencoded(args)
            req_body = prs.urlencode(args)  # WARNING: not sure if legal library, need to implement my own percent encoding
            req_obj.body = req_body

        req_obj.header_dic["Content-Length"] = str(len(req_obj.body.encode('utf-8')))


        code, body = self.send_request(host, port, req_obj)
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )


# example get with curl:
# curl -v https://en.wikipedia.org/wiki/David_H._Turpin
#
# GET /wiki/David_H._Turpin HTTP/2
# Host: en.wikipedia.org
# User-Agent: curl/7.54.0
# Accept: */*

# python3 prog GET url
# python3 prog url

if __name__ == "__main__":
    client = HTTPClient()
    # command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)


    if (len(sys.argv) == 3):
        # post requested I think
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        # get requested
        print(client.command( sys.argv[1] ))






























# Anchor
