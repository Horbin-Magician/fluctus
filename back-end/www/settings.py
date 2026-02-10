# app配置
import os
import secrets

def _load_or_generate_secret_key():
  key_path = os.path.join(os.path.dirname(__file__), '..', 'datas', 'secret_key')
  try:
    with open(key_path, 'r') as f:
      return f.read().strip()
  except FileNotFoundError:
    os.makedirs(os.path.dirname(key_path), exist_ok=True)
    key = secrets.token_hex(32)
    with open(key_path, 'w') as f:
      f.write(key)
    return key

class BaseConfig(object):
  DEBUG = True
  SECRET_KEY = _load_or_generate_secret_key()

class ProductionConfig(BaseConfig):
  DEBUG = False
  SESSION_COOKIE_SECURE = True

class DevelopmentConfig(BaseConfig):
  pass

class TestingConfig(BaseConfig):
  pass