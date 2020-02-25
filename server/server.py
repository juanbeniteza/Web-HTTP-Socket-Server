import tornado.web
import tornado.httpserver
import tornado.ioloop
from tornado.httpclient import AsyncHTTPClient
from dotenv import load_dotenv
from tornado.options import define, options
from socket_server import WebSocket
from opencage.geocoder import OpenCageGeocode
from parser import parser
import os
import json

load_dotenv()
PORT = 4041
DARK_SKY_API_KEY = os.getenv("DARK_SKY_API_KEY")
DARK_SKY_ENDPOINT = os.getenv("DARK_SKY_ENDPOINT")
OPEN_CAGE_API_KEY = os.getenv("OPEN_CAGE_API_KEY")


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, world")

class WeatherHandler(tornado.web.RequestHandler):

    async def get_weather(self, lat, lon):
        http_client = AsyncHTTPClient()
        try:
            response = await http_client.fetch(f"{DARK_SKY_ENDPOINT}/{DARK_SKY_API_KEY}/{lat},{lon}/?units=si&exclude=minutely,hourly,alerts,flags", validate_cert=False)
            return response.body
        except Exception as ex:
            raise tornado.web.HTTPError(400)

    async def get(self, uuid, query):
        city = query
        geocoder = OpenCageGeocode(OPEN_CAGE_API_KEY)
        lat = lon = 0
        try:
            results = geocoder.geocode(city)
            lat, lon = (results[0]['geometry']['lat'], results[0]['geometry']['lng'])
        except Exception as ex:
            raise tornado.web.HTTPError(404)

        data = await self.get_weather(lat, lon)
        data = json.loads(data.decode('utf8'))
        data['address'] = results[0]['formatted']
        data = parser(data)
        WebSocket.update_client(uuid, lat, lon)
        self.write(data)

class WeatherLatLonHandler(tornado.web.RequestHandler):

    async def get_weather(self, lat, lon):
        http_client = AsyncHTTPClient()
        try:
            response = await http_client.fetch(f"{DARK_SKY_ENDPOINT}/{DARK_SKY_API_KEY}/{lat},{lon}/?units=si&exclude=minutely,hourly,alerts,flags", validate_cert=False)
            return response.body
        except Exception as ex:
            raise tornado.web.HTTPError(400)

    async def get(self, lat, lon):
        
        # TODO use geocode to validate lat, lon
        geocoder = OpenCageGeocode(OPEN_CAGE_API_KEY)

        try:
            results = geocoder.reverse_geocode(lat, lon)    
            address = results[0]['formatted']
        except Exception as ex:
            raise tornado.web.HTTPError(404)

        data = await self.get_weather(lat, lon)
        data = json.loads(data.decode('utf8'))
        data['address'] = address
        data = parser(data)
        self.write(data)
         

def main():

    handlers = [
            (r"/", MainHandler),
            (r"/weather/(.*)/(.*)", WeatherHandler),
            (r"/lat-lon/(.*)/(.*)", WeatherLatLonHandler),
            (r"/ws/", WebSocket)
    ]

    # Creates a tornado application and provide the urls
    app = tornado.web.Application(handlers)
    
    # Setup the server
    server = tornado.httpserver.HTTPServer(app)
    server.listen(PORT)
    
    # Start io/event loop
    io_loop = tornado.ioloop.IOLoop.instance()
    io_loop.start()


if __name__ == '__main__':
    main()