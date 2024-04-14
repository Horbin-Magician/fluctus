from flask import Blueprint

from .views.login import LoginView
from .views.authority import AuthorityView
from .views.user import UserView
from .views.favourites.favType import FavTypeView
from .views.favourites.favItem import FavItemView
from .views.searcher.baidu import BaiduView
from .views.secret import SecretView

api = Blueprint('api', __name__)
# 基础API
api.add_url_rule('/login', view_func=LoginView.as_view(name='login'))
api.add_url_rule('/authority', view_func=AuthorityView.as_view(name='authority'))
api.add_url_rule('/user', view_func=UserView.as_view(name='user'))
# 收藏夹API
api.add_url_rule('/favourites/favtype', view_func=FavTypeView.as_view(name='favtype'))
api.add_url_rule('/favourites/favitem', view_func=FavItemView.as_view(name='favitem'))
# 搜索API
api.add_url_rule('/search/baidu', view_func=BaiduView.as_view(name='baidu'))
# 秘密树洞API
api.add_url_rule('/secret', view_func=SecretView.as_view(name='secret'))