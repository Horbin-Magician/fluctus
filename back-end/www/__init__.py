from flask import Flask

from .bp_api import api
from .bp_web import web

app = Flask(__name__) # 创建app
app.config.from_object("www.settings.DevelopmentConfig") # 配制app

app.register_blueprint(api, url_prefix='/api') # 注册蓝图api
app.register_blueprint(web) # 注册蓝图web