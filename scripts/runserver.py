import argparse
from flask import Flask

parser = argparse.ArgumentParser(description="Start potent potables in dev mode")
parser.add_argument("--no-debug", default=False, action="store_true",
                    help="Turn off debuging mode")
parser.add_argument("--port", dest='port', default=18092, type=int,
                    help="Specify port to listen on")
args = parser.parse_args()

import logging
logging.basicConfig(level=logging.DEBUG)

from potables.api import app
application = Flask(__name__)
application.wsgi_app = app
application.run(debug=not args.no_debug, port=args.port)
