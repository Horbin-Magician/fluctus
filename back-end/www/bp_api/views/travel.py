from flask import views, request, session, jsonify

from tools.dbControllers.TravelDbController import TravelDbController


class TravelView(views.View):
    methods = ['POST']
    decorators = []

    def dispatch_request(self):
        return_dict = {'status': '1'}
        type = request.json.get('type')
        if session.get('user_info'):
            username = session['user_info']
            db = TravelDbController()

            if type == 'get_diaries':
                data = db.getDiaries(username)
                return_dict['status'] = '0'
                return_dict['data'] = data

            elif type == 'create_diary':
                name = request.json.get('name', '').strip()
                if name:
                    diary_id = db.createDiary(username, name)
                    return_dict['status'] = '0'
                    return_dict['id'] = diary_id

            elif type == 'update_diary':
                diary_id = request.json.get('diary_id')
                name = request.json.get('name', '').strip()
                if diary_id and name:
                    db.updateDiary(diary_id, username, name)
                    return_dict['status'] = '0'

            elif type == 'delete_diary':
                diary_id = request.json.get('diary_id')
                if diary_id:
                    db.deleteDiary(diary_id, username)
                    return_dict['status'] = '0'

            elif type == 'get_places':
                diary_id = request.json.get('diary_id')
                if diary_id:
                    data = db.getPlaces(diary_id, username)
                    return_dict['status'] = '0'
                    return_dict['data'] = data

            elif type == 'add_place':
                diary_id = request.json.get('diary_id')
                place = request.json.get('place')
                if diary_id and place:
                    place_id = db.addPlace(diary_id, username, place)
                    if place_id:
                        return_dict['status'] = '0'
                        return_dict['id'] = place_id

            elif type == 'delete_place':
                diary_id = request.json.get('diary_id')
                place_id = request.json.get('place_id')
                if diary_id and place_id:
                    if db.deletePlace(place_id, diary_id, username):
                        return_dict['status'] = '0'

            elif type == 'update_place_typecode':
                diary_id = request.json.get('diary_id')
                place_id = request.json.get('place_id')
                typecode = request.json.get('typecode', '')
                if diary_id and place_id:
                    if db.updatePlaceTypecode(place_id, diary_id, username, typecode):
                        return_dict['status'] = '0'

        return jsonify(return_dict)
