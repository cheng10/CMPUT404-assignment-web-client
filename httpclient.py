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
	def parse_url(self,url):
		#the syntax of a generic URI, from wikipedia
		#scheme:[//[user:password@]host[:port]][/]path[?query][#fragment]
		url = url.strip("/")
		url = url.strip("http://")
		splited = url.split("/",1)
		host_port = splited.pop(0)
		path_query = "/"+"/".join(splited)
		hps = host_port.split(":")
		host = hps[0]
		if (len(hps) > 1):
			port = int(hps[1])
		else:
			port = 80
		#print host, port, path_query
		return host, port, path_query

	def connect(self, host, port):
		# use sockets!
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.connect((host,port))
		return sock

	def get_code(self, data):
		code=int(data.split(" ")[1])
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
		host, port, path = self.parse_url(url)
		sock = self.connect(host, port)
		sock.sendall("GET "+path+" HTTP/1.1\r\nHost: "+host+"\r\nConnection: close\r\n\r\n" )
		#Why should I have to add the "Connection: close" sentence???
		#Some servers have "Connection: keep-alive" in the http response header by default,
		#This will keep the socket open.
		#And script would never end. It will stuck in the recall() step forever.
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
		if (args!=None):
			args = urllib.urlencode(args)
		host, port, path = self.parse_url(url)
		sock = self.connect(host, port)
		message="POST %s HTTP/1.0\r\nHost: %s\r\n" 
		if (args==None): 
			message+="Content-Length: 0\r\n"
		else:
			message+="Content-Length: "+str(len(args))+"\r\n"
		message+="Content-Type: application/x-www-form-urlencoded\r\n\r\n"
		message+="%s\r\n"
		sock.send(message % (path, host, args))
		data = self.recvall(sock)
		sock.close()
		print data
		code = self.get_code(data)
		header = self.get_headers(data)
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
