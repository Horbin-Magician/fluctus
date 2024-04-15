import os
from flask import Flask
from flask_cors import CORS

from .bp_api import api

app = Flask(__name__) # 创建app

# 配制app
is_debug_mode = os.environ.get('FLASK_DEBUG', 'true').lower() == 'true'
if is_debug_mode: app.config.from_object("www.settings.DevelopmentConfig")
else: app.config.from_object("www.settings.ProductionConfig")

app.register_blueprint(api, url_prefix='/api') # 注册蓝图api
cors = CORS(app, supports_credentials=True) # 允许跨域