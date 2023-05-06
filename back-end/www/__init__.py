from flask import Flask
from flask_cors import CORS

from .bp_api import api

app = Flask(__name__) # 创建app
cors = CORS(app) # 允许跨域
app.config.from_object("www.settings.DevelopmentConfig") # 配制app
app.register_blueprint(api, url_prefix='/api') # 注册蓝图api