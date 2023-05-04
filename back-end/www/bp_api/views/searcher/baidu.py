from flask import views,request
import json
import requests

from tools.dbControllers.BaseDbController import BaseDbController


class BaiduView(views.View):
  methods = ['POST']
  decorators = []

  def dispatch_request(self):
    return_dict = {'status':'1'}
    word = request.json.get('word')
    response = requests.get('https://www.baidu.com/sugrec?prod=pc&wd=' + word)
    return_dict['data'] = response.json()['g']
    return json.dumps(return_dict)
