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

        email = get_user_email()
        fname = ""
        lname = ""
        alias = ""
        if email:
          qry1 = accountModel.query()
          qry2 = qry1.filter(accountModel.userID == users.get_current_user().user_id()).fetch(1)
          for q in qry2:
            if q.userID == users.get_current_user().user_id():
              fname = q.firstName
              lname = q.lastName
              alias = q.alias
        page_params = {
          'user_email': email,
          'firstName': fname,
          'lastName': lname,
          'alias': alias,
          'login_url': users.create_login_url(),
          'logout_url': users.create_logout_url('/')
        }
        render_template(self, 'index.html', page_params)


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


###############################################################################
class InfoUploadHandler(webapp2.RequestHandler):
  def post(self): 
    email = get_user_email()
    if email:
      self.redirect('/')


class accountModel(ndb.Model):
  userID = ndb.StringProperty()
  firstName = ndb.StringProperty()
  lastName = ndb.StringProperty()
  alias = ndb.StringProperty()

########################################################################################
class accountManagementHandler(webapp2.RequestHandler):
  def get(self):
    email = get_user_email()
    if email:
      acctManage_url = '/acctManageInfo'
      page_params = {
        'user_email': email,
        'login_url': users.create_login_url(),
        'logout_url': users.create_logout_url('/'),
        'acctManage_url': acctManage_url
      }
      render_template(self, 'acctManage.html', page_params)
    else:
      self.redirect('/')
  def post(self):
    email = get_user_email()
    if email: 
      fname = self.request.get('fname')
      lname = self.request.get('lname')
      alias = self.request.get('alias')
      AcctModel = accountModel()
      AcctModel.userID = users.get_current_user().user_id()
      AcctModel.firstName = fname
      AcctModel.lastName = lname
      AcctModel.alias = alias
      AcctModel.put()
      page_params = {
        'login_url': users.create_login_url(),
        'logout_url': users.create_logout_url('/'),
        'user_email': email,
        'fname': fname,
        'lname': lname,
        'alias': alias
      }
      render_template(self, 'acctManageInfo.html', page_params)
    else:
      self.redirect('/')

########################################################################################
mappings = [
  ('/', MainHandler),
  ('/index', MainHandler),
  ('/acctManage', accountManagementHandler),
  ('/acctManageInfo', InfoUploadHandler)
]
app = webapp2.WSGIApplication(mappings, debug=True)
