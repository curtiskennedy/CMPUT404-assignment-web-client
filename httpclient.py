#!/usr/bin/env python3
# coding: utf-8
# Copyright 2023 Abram Hindle, https://github.com/tywtyw2002, https://github.com/treedust, Curtis Kennedy
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
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    def get_host_port(self,url):
        # get host and port from url
        # port defaults to 80 unless specified
        # will terminate if host is missing
        self.parse_res = urllib.parse.urlparse(url)
        host = self.parse_res.hostname
        port = self.parse_res.port
        if port is None:
            port = 80
        if host is None:
            print("INVALID URL: MISSING HOST")
            return
        return host, port

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        # code should be after the first space
        return data.split()[1]

    def get_headers(self,data):
        split_res = data.split("\r\n")
        print("RESPONSE CODE AND HEADERS\n")
        res = []
        for item in split_res:
            if item == '':
                break
            else:
                res.append(item)
                print(item)
        print("##################################### END RESPONSE CODE AND HEADERS")
        return res

    def get_body(self, data):
        # body should be after the \r\n\r\n
        return data.split("\r\n\r\n",1)[1]
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

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
        return buffer.decode('utf-8')

    def build_request(self, type, host, args=None):
        # print("PARSED URL:\n")
        # print([i for i in self.parse_res])
        path = self.parse_res[2]
        if path == '':
            path = '/'
        if self.parse_res.query != '':
            path = path + "?" + self.parse_res.query
        content_type = "application/x-www-form-urlencoded"
        if args is not None:
            # print("ARGS = ")
            # print(args)
            args = urllib.parse.urlencode(args, quote_via = urllib.parse.quote)
        else:
            args = ''
        request = f"{type} {path} HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\nUser-Agent: me\r\nAccept: */*;charset=utf-8\r\nContent-Type: {content_type}\r\nContent-Length: {len(args)}\r\n\r\n{args}"
        print("#####################################")
        print(f"REQUEST\n\n{request}")
        print("##################################### END REQUEST")
        return request

    def GET(self, url, args=None):
        # send and get response
        host, port = self.get_host_port(url)
        # print(f"CONNECTING ON HOST: {host} and PORT: {port}")
        self.connect(host, port)

        request = self.build_request("GET", host, args)
        self.sendall(request)
        response = self.recvall(self.socket)
        self.close()

        code = self.get_code(data=response)
        headers = self.get_headers(data=response)
        body = self.get_body(data=response)

        # print(f"CODE --> {code}")
        print(f"BODY\n\n{body}")
        print("##################################### END BODY")
        return HTTPResponse(int(code), body)

    def POST(self, url, args=None):
        # send and get response
        host, port = self.get_host_port(url)
        # print(f"CONNECTING ON HOST: {host} and PORT: {port}")
        self.connect(host, port)

        request = self.build_request("POST", host, args)
        self.sendall(request)
        response = self.recvall(self.socket)
        self.close()

        code = self.get_code(data=response)
        headers = self.get_headers(data=response)
        body = self.get_body(data=response)

        # print(f"CODE --> {code}")
        print(f"BODY\n\n{body}")
        print("##################################### END BODY")
        return HTTPResponse(int(code), body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
