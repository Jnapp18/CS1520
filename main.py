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

from helperFunctions import *
from models import *
import webapp2
import random
import time
from google.appengine.api import users, mail
from google.appengine.ext.webapp import blobstore_handlers


################## Page Handlers ####################
# Here we basically gather information, and send that information into a template so a page can be rendered.
# Home page handler.
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
      else:  # THIS IS WHERE I DID WORK. IF FIRST TIME USER, ADD THEM TO THE NDB, SEND THEM AN EMAIL -sk
        user = accountModel(id=users.get_current_user().user_id(), firstName=fname, lastName=lname, username=email.split("@", 1)[0], score=0)
        accountModel.put(user)
    page_params = {
      'user_email': email,
      'firstName': fname,
      'lastName': lname,
      'username': username,
      'login_url': users.create_login_url(),
      'logout_url': users.create_logout_url('/')
    }
    render_template(self, 'index.html', page_params)

class EmailHandler(webapp2.RequestHandler):
  def post(self):
    email = get_user_email()
    if email:
      subject = self.request.get('subject')
      body = self.request.get('body')
      mail.send_mail(email, 'jnapp18@gmail.com', subject, body)
      self.redirect('/')
    self.redirect('/')

# "My Account" page handler for editing information
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

# Handler for "My Account" information. Displays information and updates ndb accountModel with new info.
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
      # updating the database with account information
      AccountQry = accountModel.get_by_id(users.get_current_user().user_id())
      AcctModel = accountModel(id=users.get_current_user().user_id())
      AcctModel.firstName = fname
      AcctModel.lastName = lname
      AcctModel.username = username
      AcctModel.score = AccountQry.score
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

# Lobby Handler
class LobbyHandler(webapp2.RequestHandler):
  def get(self):
    email = get_user_email()
    fname = ""
    lname = ""
    username = ""
    results = challengeModel.query()
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
      'logout_url': users.create_logout_url('/'),
      'challenges': results
    }
    render_template(self, 'lobbies.html', page_params)

# Challenge Handler
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

# manageChallenge Handler
class manageChallengeHandler(webapp2.RequestHandler):
  def get(self):
    email = get_user_email()
    fname = ""
    lname = ""
    username = ""
    results = challengeModel.query(challengeModel.ownerID == users.get_current_user().user_id())
    publicResults = challengeModel.query()
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
      'logout_url': users.create_logout_url('/'),
      'challenges': results,
      'pChallenges': publicResults
    }
    render_template(self, 'manageChallenges.html', page_params)

#Solve Challenge Handler
class solveChallengeHandler(webapp2.RequestHandler):
  def get(self):
    email = get_user_email()
    fname = ""
    lname = ""
    username = ""
    chal_id = self.request.get('chal_id')
    user_id = users.get_current_user().user_id()
    solved = 0 #not yet solved
    if email:
      qry = accountModel.get_by_id(users.get_current_user().user_id())
      if qry:
        fname = qry.firstName
        lname = qry.lastName
        username = qry.username
      chalObject = challengeModel.query(challengeModel.name == str(chal_id)).get()
      progTable = progressTable.query(progressTable.userID == user_id, progressTable.challengeID == chal_id).get()
      if progTable:
        #if query exists where userID and ChallengeID already exist, then we know they have solved this one
        solved = 1
      else:
        solved = 0
    page_params = {
      'solved': solved,
      'user_email': email,
      'firstName': fname,
      'lastName': lname,
      'username': username,
      'chalObject': chalObject,
      'login_url': users.create_login_url(),
      'logout_url': users.create_logout_url('/')
    }
    render_template(self, 'solveChallenge.html', page_params)
  def post(self):
    email = get_user_email()
    chal_id = self.request.get('chal_id')
    userAnswer = self.request.get('userAnswer')
    user_id = users.get_current_user().user_id()
    if email:
      chalObject = challengeModel.query(challengeModel.name == str(chal_id)).get()
      chalScore = chalObject.score
      if userAnswer == chalObject.answer:
        self.response.out.write('Correct')
        progTable = progressTable.query(progressTable.userID == user_id, progressTable.challengeID == chal_id).get()
        if progTable:
          print "should not be in here"#because you not be able to get to this method if the question is already
                                      # answered you cannot submit again. If a user is sneaky with the url
                                      #This will prevent the user from gaining points
        else:
          AccountQry = accountModel.get_by_id(users.get_current_user().user_id())
          AcctModel = accountModel(id=users.get_current_user().user_id())
          AcctModel.score = AccountQry.score + chalScore
          AcctModel.firstName = AccountQry.firstName
          AcctModel.lastName = AccountQry.lastName
          AcctModel.username = AccountQry.username
          AcctModel.put()
          progTableUpdate = progressTable()
          progTableUpdate.userID = user_id
          progTableUpdate.lobbyID = 1
          progTableUpdate.challengeID = chal_id
          progTableUpdate.put()
      else:
        self.response.out.write('Incorrect')
      
    else:
      self.redirect('/')

# UploadChallenge Handler
class uploadChallengeHandler(blobstore_handlers.BlobstoreUploadHandler):
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
      render_template(self, 'uploadChallenge.html', page_params)
    else:
      self.redirect('/')

  def post(self):
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
      # updating the database with challenge information
      uploaded_file = self.get_uploads()
      Challenge = challengeModel()
      Challenge.challengeID = random.randint(1, 1000)
      Challenge.ownerID = users.get_current_user().user_id()
      Challenge.question = self.request.get('question')
      Challenge.answer = self.request.get('answer')
      Challenge.attachments = uploaded_file
      Challenge.score = int(self.request.get('points'))
      Challenge.name = self.request.get('name')
      Challenge.put()
      page_params = {
        'login_url': users.create_login_url(),
        'logout_url': users.create_logout_url('/'),
        'user_email': email,
        'firstName': fname,
        'lastName': lname,
        'username': username
      }
      render_template(self, 'challenges.html', page_params)
    else:
      self.redirect('/')

# Leaderboard Handler
class leaderboardHandler(webapp2.RequestHandler):
  def get(self):
    email = get_user_email()
    fname = ""
    lname = ""
    username = ""
    rank = 0
    results = accountModel.query()
    results = results.order(-accountModel.score)

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
      'logout_url': users.create_logout_url('/'),
      'board': results,
      'rank': rank
    }
    render_template(self, 'leaderboard.html', page_params)
	
class editChallengeHandler(blobstore_handlers.BlobstoreUploadHandler):
	def get(self):
	  email = get_user_email()
	  fname = ""
	  lname = ""
	  username = ""
	  challengeName = ""
	  challengeQuestion = ""
	  challengeAnswer = ""
	  challengePoints = 0
	  challengeId = self.request.get("challengeId")
	  
	  if email:
	    userQry = accountModel.get_by_id(users.get_current_user().user_id())
	    if userQry:
	      fname = userQry.firstName
	      lname = userQry.lastName
	      username = userQry.username
	  
	  if challengeId:
	    challengeNum = challengeId[22:-1]
	    challenge = ndb.Key(challengeModel, int(challengeNum)).get()
	    #qry = challengeModel.query(challengeModel.key == ndb.Key(challengeModel, challengeNum))
	    #if challenge:
	    challengeName = challenge.name
	    challengeQuestion = challenge.question
	    challengeAnswer = challenge.answer
	    challengePoints = challenge.score
	    
	  
	  page_params = {
 	   'user_email': email,
        'firstName': fname,
        'lastName': lname,
        'username': username,
		'challengeName': challengeName,
		'challengeQuestion': challengeQuestion,
		'challengeAnswer': challengeAnswer,
		'challengePoints': challengePoints,
        'login_url': users.create_login_url(),
        'logout_url': users.create_logout_url('/')
      }
	  render_template(self, 'editChallenge.html', page_params)
	  
	def post(self):
	  email = get_user_email()
	  fname = ""
	  lname = ""
	  username = ""
	  challengeId = self.request.get("challengeId")
	  if email:
	    qry = accountModel.get_by_id(users.get_current_user().user_id())
	    if qry:
	      fname = qry.firstName
	      lname = qry.lastName
	      username = qry.username
        # updating the database with updated challenge information
	    uploaded_file = self.get_uploads()
	    if challengeId:
	      challengeNum = challengeId[22:-1]
	      Challenge = ndb.Key(challengeModel, int(challengeNum)).get()
	      Challenge.question = self.request.get('question')
	      Challenge.answer = self.request.get('answer')
	      Challenge.attachments = uploaded_file
	      Challenge.score = int(self.request.get('points'))
	      Challenge.name = self.request.get('name')
	      Challenge.put()
	      page_params = {
        'login_url': users.create_login_url(),
        'logout_url': users.create_logout_url('/'),
        'user_email': email,
        'firstName': fname,
        'lastName': lname,
        'username': username
        }
	      time.sleep(0.2)  #There is a sleep timer here because the change will not appear when you redirect to manageChallenges.html unless you wait for 0.2 milliseconds
	      self.redirect('/manageChallenges')
	  else:
	    self.redirect('/manageChallenges')
################## End Page Handlers ####################



################## url Mappings. ####################
# When a URL is clicked, goes to the function to take care of the specific request.
mappings = [
  ('/', MainHandler),
  ('/index', MainHandler),
  ('/email', EmailHandler),
  ('/publicLobby', LobbyHandler),
  ('/Challenges', ChallengeHandler),
  ('/manageChallenges', manageChallengeHandler),
  ('/uploadChallenge', uploadChallengeHandler),
  ('/solveChallenge', solveChallengeHandler),
  ('/acctManage', accountManagementHandler),
  ('/acctManageInfo', accountManageDisplay),
  ('/leaderboard', leaderboardHandler),
  ('/editChallenge', editChallengeHandler)
]
app = webapp2.WSGIApplication(mappings, debug=True)
