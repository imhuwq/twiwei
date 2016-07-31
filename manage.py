import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web

from app import create_app

tornado.options.define("mode", default="develop", help="以何种方式运行(develop/test/product)， 默认为 develop")
tornado.options.define("port", default=8000, type=int, help="侦听端口， 默认为 8000")

if __name__ == "__main__":
    tornado.options.parse_command_line()
    mode = tornado.options.options.mode
    port = tornado.options.options.port
    app = create_app(mode)
    app = app
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(8000)
    print('开始以 %s 模式在 %d 端口运行 Tornado 服务...' % (mode, port))
    tornado.ioloop.IOLoop.instance().start()
