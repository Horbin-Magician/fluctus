from flask import views, request, session, jsonify
from datetime import datetime

from tools.dbControllers.SecretDbController import SecretDbController

class SecretView(views.View):
    methods = ['POST']
    decorators = []
    def dispatch_request(self):
        if not session.get('user_info'):
            return jsonify({
                'status': '1',
                'message': '请先登录'
            }), 401

        return_dict = {'status': '1'}
        payload = request.get_json(silent=True) or {}
        type = payload.get('type')
        db = SecretDbController()
        now = datetime.now() # 获取当前日期和时间
        formatted_date = now.strftime('%Y%m%d') # 格式化日期
        if(type == 'get'): # 获取
            data = db.getSecret(formatted_date)
            return_dict['status'] = '0'
            return_dict['data'] = data
        if(type == 'update'): # 更新
            state = payload.get('state')
            message = payload.get('message')
            db.updateState(formatted_date, state, message)
            return_dict['status'] = '0'
        return jsonify(return_dict)
