import cherrypy, array
from ws4py.server.cherrypyserver import WebSocketPlugin, WebSocketTool
from ws4py.websocket import WebSocket


class cavemanWebSocket(WebSocket):
	""" the WebSocket handler for Caveman """
	def opened(self):
		""" Called by the server when the upgrade handshake has succeeeded.
			We use this to add ourselves to the list of active clients. """
		print 'client connected!'
		clients.append(self)

	def closed(self, code, reason=None):
		""" Called by the server when the connection is close from either end.
			We use this to remove ourselves from the list of active clients. """
		print 'client disconnected!'
		clients.remove(self)

	def received_message(self, message):
		""" Called by the server when the client sends a message.
			We use this to relay the message to everybody else."""
		print 'message recieved: '+str(message)
		for client in clients:
			client.send(message)
    	

cherrypy.config.update({'server.socket_port': 1337})
WebSocketPlugin(cherrypy.engine).subscribe()
cherrypy.tools.websocket = WebSocketTool()

global clients
clients = []

class Root(object):
    @cherrypy.expose
    def index(self):
        handler = cherrypy.request.ws_handler

    @cherrypy.expose
    def ws(self):
        # you can access the class instance through
        handler = cherrypy.request.ws_handler

cherrypy.quickstart(Root(), '/', config={'/ws': {'tools.websocket.on': True,
                                                 'tools.websocket.handler_cls': cavemanWebSocket}})
