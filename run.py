import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web

from app import create_app

app = create_app()

if __name__ == "__main__":
    tornado.options.parse_command_line()
    app = app
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(8000)
    tornado.ioloop.IOLoop.instance().start()
