import sys
import time
import signal
import logging

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web

from app import create_app
from test import Test
from deploy import deploy

cmd = sys.argv[1]

if cmd == 'deploy':
    tornado.options.define("server", default="", type=str, help="服务器域名")
    tornado.options.parse_command_line(sys.argv[1:])
    server = tornado.options.options.server
    deploy(server)

elif cmd == 'runserver':
    tornado.options.define("mode", default="develop", help="以何种方式运行(develop/test/product)， 默认为 develop")
    tornado.options.define("port", default=8000, type=int, help="侦听端口， 默认为 8000")
    tornado.options.parse_command_line(sys.argv[1:])

    if __name__ == "__main__":

        def sig_handler(sig, frame):
            logging.warning('Caught signal: %s', sig)
            tornado.ioloop.IOLoop.instance().add_callback(shutdown)


        def shutdown():
            logging.info('正在关闭服务器...')
            http_server.stop()

            logging.info('将在%s秒后彻底关闭服务器 ...', 3)
            io_loop = tornado.ioloop.IOLoop.instance()

            deadline = time.time() + 3

            def stop_loop():
                now = time.time()
                if now < deadline and (io_loop._callbacks or io_loop._timeouts):
                    io_loop.add_timeout(now + 1, stop_loop)
                else:
                    logging.info('正在关闭 IO Loop...')
                    io_loop.stop()

            stop_loop()


        mode = tornado.options.options.mode
        port = tornado.options.options.port
        if mode == 'develop' or mode == 'product':
            app = create_app(mode)

            global http_server
            http_server = tornado.httpserver.HTTPServer(app)
            http_server.listen(port)

            signal.signal(signal.SIGQUIT, sig_handler)
            signal.signal(signal.SIGTERM, sig_handler)
            signal.signal(signal.SIGINT, sig_handler)

            print('开始以 %s 模式在 %d 端口运行 Tornado 服务...' % (mode, port))
            tornado.ioloop.IOLoop.instance().start()

            logging.info("Tornado 服务已经彻底关闭")

        elif mode == 'test':
            test = Test()
            test.run()
