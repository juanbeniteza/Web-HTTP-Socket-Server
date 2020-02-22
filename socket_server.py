import tornado.websocket as ws
import uuid
import logging

logging.basicConfig(level=logging.INFO)

class WebSocket(ws.WebSocketHandler):
    
    clients = {}

    def __init__(self, application, request, *args, **kwargs):
        super().__init__(application, request, *args, **kwargs)
        self.uuid = None
    
    def open(self):

        self.uuid = str(uuid.uuid4())
        logging.info(f"New client connected with uuid {self.uuid}")
        self.add_client()
        self.write_message("You are connected")
        
    def on_message(self, message):

        logging.info(f"New message from {self.uuid} : {message}")
        self.write_message(f"You said {message}")
    
    def on_close(self):
        self.remove_client()
        logging.info("Connection is closed")
    
    def check_origin(self, origin):
        return True

    def add_client(self):
        self.clients[self.uuid] = {"obj": self, "query": None}

    def remove_client(self):
        self.clients.pop(self.uuid, None)