# -- coding: utf-8 --
import os
import sys
import signal
import time

from tornado import ioloop
from tornado.options import options

from common.init import *
from common.loader import load_url_handlers
from logger import logger
from settings import *

class iApplication(web.Application):
    def __init__(self):
        settings = {
            'static': os.path.join(os.path.dirname(__file__), "static"),
            'template_path': os.path.join(os.path.dirname(__file__), "templates"),
        }
    
        handlers = [
            (r"^/$", SigninHandler),
            (r"^/display", DisplayHandler),
            (r"^/signin", SigninHandler),
            (r"^/static/(.*)", web.StaticFileHandler, dict(path=settings['static'])),
        ]
        
        apps = load_url_handlers()
        handlers.extend(apps)
        # custom http error handler
        handlers.append((r"/aaa", PageNotFound))
        web.Application.__init__(self, handlers, **settings)

class DisplayHandler(WiseHandler):
    def get(self):
        self.render("display/demo.html")

class SigninHandler(WiseHandler):
    def get(self):
        self.render("pages-signin.html")

    def post(self):
        username = self.get_argument("signin_username", None, strip=True)
        password = self.get_argument("signin_password", None, strip=True)
        if username == "admin" and password == "123456":
            self.redirect('/attack/attacking_hosts', permanent=True)
        else:
            self.redirect('/signin', permanent=True)

class Watcher:
    def __init__(self):
        self.child = os.fork()
        if self.child == 0:
            return
        else:
            self.watch()

    def watch(self):
        try:
            os.wait()
        except (KeyboardInterrupt, SystemExit):
            # I put the capital B in KeyBoardInterrupt so I can
            # tell when the Watcher gets the SIGINT
            print "Server exit at %s." % time.ctime()
            self.kill()
        sys.exit()

    def kill(self):
        try:
            os.kill(self.child, signal.SIGKILL)
        except OSError:
            pass
    

if __name__ == '__main__':
    port = SERVER_API_PORT
    
    options.parse_command_line()
    
    app = iApplication()
    app.listen(port, xheaders=True)
    logger.info("Start server on %d OK." % port)
    
    try:
        ioloop = ioloop.IOLoop.instance()
        ioloop.start()
    except (KeyboardInterrupt, SystemExit):
        ioloop.close()

