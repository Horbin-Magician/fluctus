import os

# app配置
class BaseConfig(object):
  DEBUG = True
  SECRET_KEY = os.urandom(24)

class ProductionConfig(BaseConfig):
  DEBUG = False
  SESSION_COOKIE_SECURE = True

class DevelopmentConfig(BaseConfig):
  pass

class TestingConfig(BaseConfig):
  pass