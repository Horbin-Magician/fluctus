from flask import views,request,session
import json

from tools.dbControllers.BaseDbController import BaseDbController


class AuthorityView(views.View):
  methods = ['POST']
  decorators = []

  def dispatch_request(self):
    return_dict = {'status':'1'}
    if(session.get('user_info')):       # 权限判断
      type = request.json.get('type')
      db = BaseDbController()
      if(type == 'update'):             # 更新数据
        name = request.json.get('name')
        menus = request.json.get('menus')
        db.updateAuthority(name, menus)
        return_dict['status'] = '0'
      elif(type == 'get'):              # 获取数据
        datas = db.getData('AUTHORITY')
        return_datas = []
        for data in datas:
          return_data = {}
          return_data['name'] = data[0]
          return_data['menus'] = data[1]
          return_datas.append(return_data)
        return_dict['status'] = '0'
        return_dict['data'] = return_datas
      elif(type == 'del'):              # 删除数据
        name = request.json.get('name')
        db.delAuthority(name)
        return_dict['status'] = '0'

    return json.dumps(return_dict)
