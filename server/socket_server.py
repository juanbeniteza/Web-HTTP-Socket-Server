import tornado.websocket as ws
import uuid
import logging
import threading
from tornado.httpclient import HTTPClient
import time
import asyncio

logging.basicConfig(level=logging.INFO)

class WebSocket(ws.WebSocketHandler):
    
    clients = {}

    def __init__(self, application, request, *args, **kwargs):
        super().__init__(application, request, *args, **kwargs)
        self.uuid = None
        thread = threading.Thread(target=self.send_update)
        thread.start()
    
    def open(self):

        self.uuid = str(uuid.uuid4())
        logging.info(f"New client connected with uuid {self.uuid}")
        self.add_client()
        self.write_message("You are connected")
        self.write_message(f"uuid: {self.uuid}")
        
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

    @classmethod
    def update_client(cls, uuid, lat, lon):
        try:
            obj = cls.clients[uuid]
            obj["query"] = (lat, lon)
        except Exception as ex:
            print(ex)
            pass
    
    def send_update(self):
        asyncio.set_event_loop(asyncio.new_event_loop())
        while True:
            for uuid, value in self.clients.items():
                if value['query']:
                    lat, lon = value['query']
                    http_client = HTTPClient()
                    response = http_client.fetch(f"http://localhost:4041/lat-lon/{lat}/{lon}", validate_cert=False)
                    value['obj'].write_message(response.body)
            time.sleep(10)


        