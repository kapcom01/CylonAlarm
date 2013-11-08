from twisted.web import server, resource
from twisted.internet import reactor
from twisted.web.static import File

from lib.jsonsockclient import JsonSocketClient

import pickle

class WebApp(resource.Resource):
	#isLeaf = True
	def getChild(self, name, request):
		#if name == '':

		return self

	def render_GET(self, request):
		sock=JsonSocketClient('127.0.0.1',5000)

		if request.prepath[0]=="actdeact":
			d={
				"actdeact" : {
					"domain_id" : str(request.prepath[1])
				}
			}
			print("Sending JSON RPC...")
			return sock.sendJSON(d)
		else:
			return open("webui/index.html").read()

rootResource = WebApp()
rootResource.putChild('bootstrap.css', File('webui/css/bootstrap.css', 'text/css'))
rootResource.putChild('bootstrap.min.css', File('webui/css/bootstrap.min.css', 'text/css'))
rootResource.putChild('jquery-1.10.2.js', File('webui/js/jquery-1.10.2.js', 'application/javascript'))

print("Starting Twisted Reactor...")

site = server.Site(rootResource)
reactor.listenTCP(80, site)
reactor.run()
