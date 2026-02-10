from flask import Blueprint

from .views.login import LoginView
from .views.authority import AuthorityView
from .views.user import UserView
from .views.searcher.baidu import BaiduView
from .views.secret import SecretView
from .views.travel import TravelView

api = Blueprint('api', __name__)
# 基础API
api.add_url_rule('/login', view_func=LoginView.as_view(name='login'))
api.add_url_rule('/authority', view_func=AuthorityView.as_view(name='authority'))
api.add_url_rule('/user', view_func=UserView.as_view(name='user'))
# 搜索API
api.add_url_rule('/search/baidu', view_func=BaiduView.as_view(name='baidu'))
# 秘密树洞API
api.add_url_rule('/secret', view_func=SecretView.as_view(name='secret'))
# 旅行日记API
api.add_url_rule('/travel', view_func=TravelView.as_view(name='travel'))