from flask import Flask

from rfid4xmms2.config import Config

config = Config()
application = Flask(__name__)
application.config.from_object(config)

from rfid4xmms2 import routes
