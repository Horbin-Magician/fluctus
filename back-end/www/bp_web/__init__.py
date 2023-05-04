from flask import render_template
from flask import Blueprint
from flask import url_for


web = Blueprint('web', __name__, template_folder='templates', static_folder="static")

@web.route('/', defaults={'path': ''})
@web.route('/<path:path>')
def index(path):
  return render_template('index.html')