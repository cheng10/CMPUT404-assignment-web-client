#!/usr/bin/env python
# coding: utf-8
# Copyright 2016 Abram Hindle, Cheng Chen.
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#	  http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

# The socket part contains contents from:
# http://effbot.org/zone/effnews.htm#sending-an-http-request

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib

def help():
	print "httpclient.py [GET/POST] [URL]\n"

class HTTPResponse(object):
	def __init__(self, code=200, body=""):
		self.code = code
		self.body = body

class HTTPClient(object):
	def get_host_port(self,url):
			if "http" in url:
				url=url[7:]
			#generlize url i.e. get rid of the "http://" header if exists
			csplist=url.split(":")
			if (len(csplist)==2):
				port=int(csplist[-1])
			else:
				port=80
			host_path=csplist[0]
			if (host_path[-1]=='/'):
				host_path=host_path[0:-1]
			#get rid of the endding "/" if exists
			ssplit=host_path.split("/",1)
			host=ssplit[0]
			if (len(ssplit)==1):
				path="/"
			else:
				path="/"+ssplit[1]
			return host, port, path

	def connect(self, host, port):
		# use sockets!
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.connect((host,port))
		return sock

	def get_code(self, data):
		code=data.split(" ")[1]
		return code

	def get_headers(self,data):
		blocks=data.split("\r\n\r\n")
		header=blocks[0].split("\r\n",1)[1]
		return header

	def get_body(self, data):
		blocks=data.split("\r\n\r\n")
		body=blocks[1]
		return body

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

	def GET(self, url, args=None):
		code = 500
		body = ""
		path = "/"
		host, port, path = self.get_host_port(url)
		sock = self.connect(host, port)
		sock.send("GET %s HTTP/1.0\r\nHost: %s\r\n\r\n" % (path, host))
		data = self.recvall(sock)
		sock.close()
		print data
		code = self.get_code(data)
		header = self.get_headers(data)
		body = self.get_body(data)
		return HTTPResponse(code, body)

	def POST(self, url, args=None):
		code = 500
		body = ""
		path = "/"
		host, port, path = self.get_host_port(url)
		sock = self.connect(host, port)
		sock.send("POST %s HTTP/1.0\r\nHost: %s\r\n\r\n" % (path, host))
		data = self.recval(sock)
		sock.close()
		print data
		code = self.get_code(data)
		header = self.get_header(data)
		body = self.get_body(data)

		return HTTPResponse(code, body)

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
		print client.command( sys.argv[2], sys.argv[1] )
	else:
		print client.command( sys.argv[1] )   
