# app配置
class BaseConfig(object):
  DEBUG = True
  SECRET_KEY = '4sa56df4hf5g4hv132sd4f6'

class ProductionConfig(BaseConfig):
  DEBUG = False

class DevelopmentConfig(BaseConfig):
  pass

class TestingConfig(BaseConfig):
  pass