from flask import views,request,session
import json

from tools.dbControllers.FavouritesDbController import FavouritesDbController


class FavTypeView(views.View):
  methods = ['POST']
  decorators = []

  def dispatch_request(self):
    return_dict = {'status':'1'}
    type = request.json.get('type')

    db = FavouritesDbController()
    if(type == 'get'):                      # 获取type数据
      datas = db.getTypeData()
      return_datas = []
      for data in datas:
        return_data = {}
        return_data['title'] = data[0]
        return_data['rank'] = data[1]
        return_datas.append(return_data)
      return_dict['status'] = '0'
      return_dict['data'] = return_datas
    if(session.get('user_info')):       # 权限判断
      if(type == 'update'):               # 更新type数据
        title = request.json.get('title')
        rank = request.json.get('rank')
        oldTitle = request.json.get('oldTitle')
        db.updateType(title, rank, oldTitle)
        return_dict['status'] = '0'
      if(type == 'del'):                  # 删除type数据
        title = request.json.get('title')
        db.delType(title)
        return_dict['status'] = '0'
      if(type == 'move'):                 # 移动type
        fType = request.json.get('fType')
        tType = request.json.get('tType')
        db.moveTypeData(fType, tType)
        return_dict['status'] = '0'
    return json.dumps(return_dict)