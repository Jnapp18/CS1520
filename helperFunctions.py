import os

from google.appengine.api import users
from google.appengine.ext.webapp import template


################## Helper Functions ####################
def render_template(handler, templatename, templatevalues={}):
  path = os.path.join(os.path.dirname(__file__), 'templates/' + templatename)
  html = template.render(path, templatevalues)
  handler.response.out.write(html)


def get_user_email():
  result = None
  user = users.get_current_user()
  if user:
    result = user.email()
  return result

################## End Helper Functions ####################
