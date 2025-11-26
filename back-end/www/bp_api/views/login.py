from flask import views,request,session,jsonify
import json

from tools.dbControllers.BaseDbController import BaseDbController
from www.decorators import rate_limit


class LoginView(views.View):
  methods = ['POST']
  decorators = [rate_limit(max_attempts=5, time_window=60)]

  def dispatch_request(self):
    return_dict = {'status':'1'}
    username = request.json.get('username')
    password = request.json.get('password')

    db = BaseDbController()
    data = db.getUserData(username)
    if(len(data) == 1):
      userData = data[0]
      if(username == userData[0] and password == userData[1]):
        session['user_info'] = username
        return_dict['status'] = '0'
        return_dict['username'] = username
        return_dict['authority'] = userData[2]
    return jsonify(return_dict)
