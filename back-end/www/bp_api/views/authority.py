from flask import views,request,session,jsonify

from tools.dbControllers.BaseDbController import BaseDbController


class AuthorityView(views.View):
  methods = ['POST']
  decorators = []

  def dispatch_request(self):
    if not session.get('user_info'):
      return jsonify({
        'status': '1',
        'message': '请先登录'
      }), 401

    return_dict = {'status':'1'}
    payload = request.get_json(silent=True) or {}
    type = payload.get('type')
    db = BaseDbController()
    if(type == 'update'):             # 更新数据
      name = payload.get('name')
      menus = payload.get('menus')
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
      name = payload.get('name')
      db.delAuthority(name)
      return_dict['status'] = '0'

    return jsonify(return_dict)
