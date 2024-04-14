from flask import views, request, session
from datetime import datetime
import json

from tools.dbControllers.SecretDbController import SecretDbController

class SecretView(views.View):
    methods = ['POST']
    decorators = []
    def dispatch_request(self):
        return_dict = {'status': '1'}
        type = request.json.get('type')
        if(session.get('user_info')):# 权限判断
            db = SecretDbController()
            now = datetime.now() # 获取当前日期和时间
            formatted_date = now.strftime('%Y%m%d') # 格式化日期
            print("当前日期是：", formatted_date)
            if(type == 'get'): # 获取
                data = db.getSecret(formatted_date)
                return_dict['status'] = '0'
                return_dict['data'] = data
            if(type == 'update'): # 更新
                state = request.json.get('state')
                message = request.json.get('message')
                db.updateState(formatted_date, state, message)
                return_dict['status'] = '0'
        return json.dumps(return_dict)
