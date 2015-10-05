#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import os
import webapp2
from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.ext import ndb


class MainHandler(webapp2.RequestHandler):
    def get(self):
        # images = get_images()
        email = get_user_email()
        # if email:
        #   for image in images:
        #     image.voted = image.is_voted(email)

        page_params = {
          'user_email': email,
          'login_url': users.create_login_url(),
          'logout_url': users.create_logout_url('/')
        }
        render_template(self, 'index.html', page_params)


    # def get(self):
    #     path = os.path.join(os.path.dirname(__file__), 'index.html')
    #     user = users.get_current_user()
    #     if user:
    #         greeting = ('Welcome, %s! (<a href="%s">sign out</a>)' % (user.nickname(), users.create_logout_url('/')))
    #     else:
    #         greeting = ('<a href="%s">Sign in or register</a>.' % users.create_login_url('/'))


    #     self.response.out.write('<html><body><p align="right">%s</p></body></html>' % greeting)
    #     self.response.out.write('<html><body><p align="right">%s</p></body></html>' % user)
    #     self.response.out.write(template.render(path, {}))
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
class accountManagementHandler(webapp2.RequestHandler):
  def get(self):
    email = get_user_email()
    if email:
      upload_url = blobstore.create_upload_url('/upload_complete')
      page_params = {
        'user_email': email,
        'login_url': users.create_login_url(),
        'logout_url': users.create_logout_url('/'),
        'upload_url': upload_url
      }
      render_template(self, 'upload.html', page_params)
    else:
      self.redirect('/')
app = webapp2.WSGIApplication([
    ('/', MainHandler)
], debug=True)
