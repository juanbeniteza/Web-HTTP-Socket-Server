import tornado.web
import tornado.httpserver
import tornado.ioloop
from tornado.httpclient import AsyncHTTPClient
from dotenv import load_dotenv
from tornado.options import define, options
from socket_server import WebSocket
from opencage.geocoder import OpenCageGeocode
import os

load_dotenv()
define('port', default=4041, help='port to listen on')
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
            response = await http_client.fetch(f"{DARK_SKY_ENDPOINT}/{DARK_SKY_API_KEY}/{lat},{lon}", validate_cert=False)
            return response.body
        except Exception as e:
            print("Error: %s" % e)

    async def get(self, query):
        city = query
        geocoder = OpenCageGeocode(OPEN_CAGE_API_KEY)
        lat = lon = 0
        try:
            results = geocoder.geocode(city)
            lat, lon = (results[0]['geometry']['lat'], results[0]['geometry']['lng'])
        except Exception as ex:
            print(ex)

        data = await self.get_weather(lat, lon)
        self.write(data)
        

def main():

    handlers = [
            (r"/", MainHandler),
            (r"/weather/(.*)", WeatherHandler),
            (r"/ws/", WebSocket)
    ]

    # Creates a tornado application and provide the urls
    app = tornado.web.Application(handlers)
    
    # Setup the server
    server = tornado.httpserver.HTTPServer(app)
    server.listen(options.port)
    
    # Start io/event loop
    io_loop = tornado.ioloop.IOLoop.instance()
    io_loop.start()


if __name__ == '__main__':
    main()