from flask import views, request, session
import json

from tools.dbControllers.FavouritesDbController import FavouritesDbController


class FavItemView(views.View):
    methods = ['POST']
    decorators = []

    def dispatch_request(self):
        return_dict = {'status': '1'}
        type = request.json.get('type')
        db = FavouritesDbController()
        if(type == 'get'):                # 获取
            favType = request.json.get('favType')
            datas = db.getItemDataFromType(favType)
            return_datas = []
            for data in datas:
                return_data = {}
                return_data['url'] = data[0]
                return_data['type'] = data[1]
                return_data['title'] = data[2]
                return_data['rank'] = data[3]
                return_data['iconUrl'] = data[4]
                return_data['description'] = data[5]
                return_datas.append(return_data)
            return_dict['status'] = '0'
            return_dict['data'] = return_datas
        if(session.get('user_info')):# 权限判断
            if(type == 'update'):         # 更新
                url = request.json.get('url')
                favType = request.json.get('favType')
                title = request.json.get('title')
                rank = request.json.get('rank')
                iconUrl = request.json.get('iconUrl')
                description = request.json.get('description')
                oldUrl = request.json.get('oldUrl')
                if(oldUrl):
                    db.updateItem(url, favType, title, rank,
                                  iconUrl, description, oldUrl)
                else:
                    db.updateItem(url, favType, title, rank,
                                  iconUrl, description)
                return_dict['status'] = '0'
            if(type == 'del'):            # 删除
                url = request.json.get('url')
                db.delItem(url)
                return_dict['status'] = '0'
        return json.dumps(return_dict)
