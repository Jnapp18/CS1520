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
################## NDB Models ####################
#Account management table
class accountModel(ndb.Model):
  firstName = ndb.StringProperty()
  lastName = ndb.StringProperty()
  username = ndb.StringProperty()
#Lobby management table
class lobbyModel(ndb.Model):
  lobbyID = ndb.IntegerProperty()
  lobbyName = ndb.TextProperty()
  publicBool = ndb.BooleanProperty()
  ownerID = ndb.IntegerProperty()
#Lobby Access table
class lobbyAccessModel(ndb.Model):
  lobbyID = ndb.IntegerProperty()
  userID = ndb.IntegerProperty()
#Challenge management table
class challengeModel(ndb.Model):
  challengeID = ndb.IntegerProperty()
  ownerID = ndb.IntegerProperty()
  question = ndb.TextProperty()
  answer = ndb.TextProperty()
  attachments = ndb.BlobProperty
  score = ndb.IntegerProperty()
#Challenge Access table
class challengeAccessModel(ndb.Model):
  challengeID = ndb.IntegerProperty()
  lobbyID = ndb.IntegerProperty()
#progress tracking table
class progressTable(ndb.Model):
  userID = ndb.IntegerProperty()
  lobbyID = ndb.IntegerProperty()
  challengeID = ndb.IntegerProperty()
################## End NDB Models ####################

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

################## Page Handlers ####################
#Here we basically gather information, and send that information into a template so a page can be rendered.
#Home page handler.
class MainHandler(webapp2.RequestHandler):
    def get(self):
        email = get_user_email()
        fname = ""
        lname = ""
        username = ""
        if email:
          qry = accountModel.get_by_id(users.get_current_user().user_id())
          if qry:
            fname = qry.firstName
            lname = qry.lastName
            username = qry.username
        page_params = {
          'user_email': email,
          'firstName': fname,
          'lastName': lname,
          'username': username,
          'login_url': users.create_login_url(),
          'logout_url': users.create_logout_url('/')
        }
        render_template(self, 'index.html', page_params)
#"My Account" page handler for editing information
class accountManageDisplay(webapp2.RequestHandler):
  def get(self):
    email = get_user_email()
    fname = ""
    lname = ""
    username = ""
    if email:
      qry = accountModel.get_by_id(users.get_current_user().user_id())
      if qry:
        fname = qry.firstName
        lname = qry.lastName
        username = qry.username
    page_params = {
      'user_email': email,
      'firstName': fname,
      'lastName': lname,
      'username': username,
      'login_url': users.create_login_url(),
      'logout_url': users.create_logout_url('/')
    }
    render_template(self, 'acctManageInfo.html', page_params)
#Handler for "My Account" information. Displays information and updates ndb accountModel with new info.
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
      username = self.request.get('username')
      #updating the database with account information
      AcctModel = accountModel(id=users.get_current_user().user_id())
      AcctModel.firstName = fname
      AcctModel.lastName = lname
      AcctModel.username = username
      AcctModel.put()
      page_params = {
        'login_url': users.create_login_url(),
        'logout_url': users.create_logout_url('/'),
        'user_email': email,
        'firstName': fname,
        'lastName': lname,
        'username': username
      }
      render_template(self, 'acctManageInfo.html', page_params)
    else:
      self.redirect('/')
#Lobby Handler
class LobbyHandler(webapp2.RequestHandler):
    def get(self):
        email = get_user_email()
        fname = ""
        lname = ""
        username = ""
        if email:
          qry = accountModel.get_by_id(users.get_current_user().user_id())
          if qry:
            fname = qry.firstName
            lname = qry.lastName
            username = qry.username
        page_params = {
          'user_email': email,
          'firstName': fname,
          'lastName': lname,
          'username': username,
          'login_url': users.create_login_url(),
          'logout_url': users.create_logout_url('/')
        }
        render_template(self, 'lobbies.html', page_params)
class ChallengeHandler(webapp2.RequestHandler):
    def get(self):
        email = get_user_email()
        fname = ""
        lname = ""
        username = ""
        if email:
          qry = accountModel.get_by_id(users.get_current_user().user_id())
          if qry:
            fname = qry.firstName
            lname = qry.lastName
            username = qry.username
        page_params = {
          'user_email': email,
          'firstName': fname,
          'lastName': lname,
          'username': username,
          'login_url': users.create_login_url(),
          'logout_url': users.create_logout_url('/')
        }
        render_template(self, 'challenges.html', page_params)
################## End Page Handlers ####################





################## url Mappings. ####################
#When a URL is clicked, goes to the function to take care of the specific request.
mappings = [
  ('/', MainHandler),
  ('/index', MainHandler),
  ('/Lobbies', LobbyHandler),
  ('/Challenges', ChallengeHandler),
  ('/acctManage', accountManagementHandler),
  ('/acctManageInfo', accountManageDisplay)
]
app = webapp2.WSGIApplication(mappings, debug=True)
