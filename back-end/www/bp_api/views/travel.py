from flask import views, request, session, jsonify

from tools.dbControllers.TravelDbController import TravelDbController


class TravelView(views.View):
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
        username = session['user_info']
        db = TravelDbController()

        if type == 'get_diaries':
            data = db.getDiaries(username)
            return_dict['status'] = '0'
            return_dict['data'] = data

        elif type == 'create_diary':
            name = payload.get('name', '').strip()
            trip_time = payload.get('trip_time', '').strip()
            summary = payload.get('summary', '').strip()
            if name:
                diary_id = db.createDiary(username, name, trip_time, summary)
                return_dict['status'] = '0'
                return_dict['id'] = diary_id

        elif type == 'update_diary':
            diary_id = payload.get('diary_id')
            name = payload.get('name', '').strip()
            trip_time = payload.get('trip_time', '').strip()
            summary = payload.get('summary', '').strip()
            if diary_id and name:
                if db.updateDiary(diary_id, username, name, trip_time, summary):
                    return_dict['status'] = '0'

        elif type == 'delete_diary':
            diary_id = payload.get('diary_id')
            if diary_id:
                if db.deleteDiary(diary_id, username):
                    return_dict['status'] = '0'
                else:
                    return_dict['message'] = '仅创建者可删除日记'

        elif type == 'get_diary_sharers':
            diary_id = payload.get('diary_id')
            if diary_id and db.isDiaryOwner(diary_id, username):
                sharers = db.getDiarySharers(diary_id)
                candidates = [name for name in db.getAllUsers() if name != username]
                return_dict['status'] = '0'
                return_dict['data'] = {
                    'sharers': sharers,
                    'candidates': candidates
                }

        elif type == 'update_diary_sharers':
            diary_id = payload.get('diary_id')
            sharers = payload.get('sharers')
            if diary_id and isinstance(sharers, list):
                result = db.replaceDiarySharers(diary_id, username, sharers)
                if result.get('ok'):
                    return_dict['status'] = '0'
                else:
                    return_dict['invalid_users'] = result.get('invalid_users', [])
                    if result.get('reason') == 'forbidden':
                        return_dict['message'] = '仅创建者可管理共享者'
                    elif result.get('reason') == 'invalid_users':
                        return_dict['message'] = '存在无效共享用户名'

        elif type == 'get_places':
            diary_id = payload.get('diary_id')
            if diary_id:
                data = db.getPlaces(diary_id, username)
                view = db.getDiaryView(diary_id, username)
                if db.canAccessDiary(diary_id, username):
                    return_dict['status'] = '0'
                    return_dict['data'] = data
                    return_dict['view'] = view

        elif type == 'get_diary_view':
            diary_id = payload.get('diary_id')
            if diary_id:
                data = db.getDiaryView(diary_id, username)
                if db.canAccessDiary(diary_id, username):
                    return_dict['status'] = '0'
                    return_dict['data'] = data

        elif type == 'update_diary_view':
            diary_id = payload.get('diary_id')
            center = payload.get('center')
            zoom = payload.get('zoom')
            if diary_id and isinstance(center, list) and len(center) == 2 and zoom is not None:
                try:
                    lng = float(center[0])
                    lat = float(center[1])
                    zoom = float(zoom)
                except (TypeError, ValueError):
                    lng = lat = zoom = None
                if lng is not None and lat is not None and zoom is not None:
                    if db.updateDiaryView(diary_id, username, lng, lat, zoom):
                        return_dict['status'] = '0'

        elif type == 'add_place':
            diary_id = payload.get('diary_id')
            place = payload.get('place')
            if diary_id and place:
                place_id = db.addPlace(diary_id, username, place)
                if place_id:
                    return_dict['status'] = '0'
                    return_dict['id'] = place_id

        elif type == 'delete_place':
            diary_id = payload.get('diary_id')
            place_id = payload.get('place_id')
            if diary_id and place_id:
                if db.deletePlace(place_id, diary_id, username):
                    return_dict['status'] = '0'

        elif type == 'update_place_typecode':
            diary_id = payload.get('diary_id')
            place_id = payload.get('place_id')
            typecode = payload.get('typecode', '')
            if diary_id and place_id:
                if db.updatePlaceTypecode(place_id, diary_id, username, typecode):
                    return_dict['status'] = '0'

        elif type == 'update_place_note':
            diary_id = payload.get('diary_id')
            place_id = payload.get('place_id')
            note = payload.get('note', '')
            if diary_id and place_id:
                if db.updatePlaceNote(place_id, diary_id, username, note):
                    return_dict['status'] = '0'

        return jsonify(return_dict)
