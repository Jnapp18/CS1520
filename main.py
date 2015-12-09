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
import logging
import time
from operator import itemgetter
import re
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
        lm = lobbyModel.query(lobbyModel.ownerID == "118168406204694893029 ").get()
        if lm:
          publob = lobbyAccessModel(lobbyID=lm.key, userID=users.get_current_user().user_id())
          lobbyAccessModel.put(publob)
        user = accountModel(id=users.get_current_user().user_id(), firstName=fname, lastName=lname, username=email.split("@", 1)[0])
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

# Email handler.
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
        'login_url': users.create_login_url(),
        'logout_url': users.create_logout_url('/'),
        'firstName': fname,
        'lastName': lname,
        'username': username
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

#Create Lobby Handler
class createLobbyHandler(webapp2.RequestHandler):
  def get(self):
    email = get_user_email()
    fname = ""
    lname = ""
    username = ""
    results = challengeModel.query(challengeModel.ownerID == users.get_current_user().user_id())
    resultSize = 0
    if(results.count()>0):
      resultSize = 1
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
      'numchallenges': resultSize
    }
    render_template(self, 'createLobby.html', page_params)
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
      lModel = lobbyModel()
      lModel.ownerID = users.get_current_user().user_id()
      lModel.lobbyName = self.request.get('lobbyname')
      lModel.lobbyPass = self.request.get('lobbypass')
      lModel.put()
      lobbyChallengeList = self.request.get_all('selectedQuestions')
      publob = lobbyAccessModel(lobbyID=lModel.key, userID=users.get_current_user().user_id())
      lobbyAccessModel.put(publob)
      for chals in lobbyChallengeList:
        chalAccModel = challengeAccessModel()
        chalList = re.findall(r"[^\\,\'\W)]+", chals)
        logging.error(chalList[1])
        logging.error(chalList[2])
        chalAccModel.challengeID = ndb.Key(chalList[1], long(chalList[2]))
        chalAccModel.lobbyID = lModel.key
        chalAccModel.put()
      time.sleep(0.2)
      page_params = {
        'login_url': users.create_login_url(),
        'logout_url': users.create_logout_url('/'),
        'user_email': email,
        'firstName': fname,
        'lastName': lname,
        'username': username
      }
      self.redirect('/manageLobbies')
    else:
      self.redirect('/')

#Manage Lobby Handler
class manageLobbyHandler(webapp2.RequestHandler):
  def get(self):
    email = get_user_email()
    fname = ""
    lname = ""
    username = ""
    results = lobbyModel.query(lobbyModel.ownerID == users.get_current_user().user_id())
    results2 = lobbyModel.query()
    resultSize = 0
    if(results.count()>0):
      resultSize = 1
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
      'lobbynum': resultSize,
      'lobbies': results,
      'alllobbies': results2,
      'username': username,
      'login_url': users.create_login_url(),
      'logout_url': users.create_logout_url('/')
    }
    render_template(self, 'manageLobbies.html', page_params)

#enterLobby
class enterLobbyHandler(webapp2.RequestHandler):
  def get(self):
    email = get_user_email()
    fname = ""
    lname = ""
    username = ""
    resultSize = 0
    lobbyName = ""
    prog = ""
    lobbyID = ""
    results = ""
    PittCTF = self.request.get("lobby")
    if PittCTF == "PittCTF":
      print 'do nothing'
    else:
      lobbyID = self.request.get("lobbyID")
      lobby = ndb.Key(urlsafe=lobbyID).get()
    if PittCTF == "PittCTF" or lobby.lobbyName == "PittCTF Public Lobby":
      if email:
        userQry = accountModel.get_by_id(users.get_current_user().user_id())
      else:
        self.redirect("/")
      pubLobQry = lobbyModel.query(lobbyModel.ownerID == "118168406204694893029").get()
      if userQry:
        fname = userQry.firstName
        lname = userQry.lastName
        username = userQry.username
      if pubLobQry:
        lobbyName = pubLobQry.lobbyName
        lobbyID = pubLobQry.key
        prog = progressTable.query(progressTable.lobbyID == lobbyID, progressTable.userID == users.get_current_user().user_id())
        results = challengeModel.query(challengeModel.ownerID == "118168406204694893029")
        if(results.count()>0):
          resultSize = 1
      page_params = {
      'user_email': email,
      'firstName': fname,
      'lastName': lname,
      'username': username,
      'prog': prog,
      'lobbyName': lobbyName,
      'lobbyID': lobbyID,
      'challenges': results,
      'numchallenges': resultSize,
      'login_url': users.create_login_url(),
      'logout_url': users.create_logout_url('/')
      }
      render_template(self, 'lobby.html', page_params)
    else:
      if email:
        userQry = accountModel.get_by_id(users.get_current_user().user_id())
      else:
        self.redirect("/")
      if userQry:
        fname = userQry.firstName
        lname = userQry.lastName
        username = userQry.username
      if lobbyID:
        lobby = ndb.Key(urlsafe=lobbyID).get()
        lobbyName = lobby.lobbyName
        lobbyID = lobby.key
        lamQ = lobbyAccessModel.query(lobbyAccessModel.lobbyID == lobbyID, lobbyAccessModel.userID == users.get_current_user().user_id()).get()
        #HE HAS ACCESS!
        if lamQ:
          lobbyChalList = challengeAccessModel.query(challengeAccessModel.lobbyID == lobby.key)
          chalList = []
          i = 0
          for l in lobbyChalList:
            chalList.insert(i,l.challengeID)
            i = i + 1
          results = challengeModel.query(challengeModel.key.IN(chalList))
          prog = progressTable.query(progressTable.lobbyID == lobbyID, progressTable.userID == users.get_current_user().user_id())
          if prog == None:
            prog = "none"
          if(results.count()>0):
            resultSize = 1
          page_params = {
          'user_email': email,
          'firstName': fname,
          'lastName': lname,
          'username': username,
          'prog': prog,
          'lobbyName': lobbyName,
          'lobbyID': lobbyID,
          'challenges': results,
          'numchallenges': resultSize,
          'login_url': users.create_login_url(),
          'logout_url': users.create_logout_url('/')
          }
          render_template(self, 'lobby.html', page_params)  
        #promt for password
        else:
          page_params = {
          'user_email': email,
          'firstName': fname,
          'lastName': lname,
          'username': username,
          'lobbyName': lobbyName,
          'lobbyID': lobbyID,
          'login_url': users.create_login_url(),
          'logout_url': users.create_logout_url('/')
          }
          render_template(self, 'lobbySignIn.html', page_params)  
  def post(self):
    email = get_user_email()
    password = self.request.get('password')
    lobbyID = self.request.get('lobbyID')
    lobby = ndb.Key(urlsafe=lobbyID).get()
    user_id = users.get_current_user().user_id()
    if email:
      if lobby.lobbyPass == password:
        #do the lam stuff
        publob = lobbyAccessModel(lobbyID=lobby.key, userID=users.get_current_user().user_id())
        lobbyAccessModel.put(publob)
        time.sleep(1)
        self.response.out.write('Correct')
      else:
        self.response.out.write('Incorrect')

# manageChallenge Handler
class manageChallengeHandler(webapp2.RequestHandler):
  def get(self):
    email = get_user_email()
    fname = ""
    lname = ""
    username = ""
    results = challengeModel.query(challengeModel.ownerID == users.get_current_user().user_id())
    resultSize = 0
    if(results.count()>0):
      resultSize = 1
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
      'numchallenges': resultSize,
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
    lobbyID = self.request.get('lobbyID')
    chal_id = self.request.get('chal_id')

    challenge = ndb.Key(urlsafe=chal_id).get()
    lobby = ndb.Key(urlsafe=lobbyID).get()
    user_id = users.get_current_user().user_id()

    solved = 0 #not yet solved
    if email:
      qry = accountModel.get_by_id(users.get_current_user().user_id())
      if qry:
        fname = qry.firstName
        lname = qry.lastName
        username = qry.username
      chalObject = challengeModel.query(challengeModel.name == challenge.name).get()
      progTable = progressTable.query(progressTable.userID == user_id, progressTable.challengeID == challenge.key, progressTable.lobbyID == lobby.key).get()
      if progTable:
        #if query exists where userID and ChallengeID already exist, then we know they have solved this one
        solved = 1
      else:
        solved = 0
    page_params = {
      'solved': solved,
      'lobbyID': lobby.key,
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
    lobbyID = self.request.get('lobbyID')
    challenge = ndb.Key(urlsafe=chal_id).get()
    lobby = ndb.Key(urlsafe=lobbyID).get()
    userAnswer = self.request.get('userAnswer')
    user_id = users.get_current_user().user_id()
    if email:
      chalScore = challenge.score
      if userAnswer == challenge.answer:
        progTable = progressTable.query(progressTable.userID == user_id, progressTable.lobbyID == lobby.key, progressTable.challengeID == challenge.key).get()
        if progTable:
          self.response.out.write('Correct')
          #because you not be able to get to this method if the question is already
          # answered you cannot submit again. If a user is sneaky with the url
          #This will prevent the user from gaining points
        else:
          AccountQry = accountModel.get_by_id(users.get_current_user().user_id())
          AcctModel = accountModel(id=users.get_current_user().user_id())
          AcctModel.firstName = AccountQry.firstName
          AcctModel.lastName = AccountQry.lastName
          AcctModel.username = AccountQry.username
          AcctModel.put()
          progTableUpdate = progressTable()
          progTableUpdate.userID = user_id
          progTableUpdate.lobbyID = lobby.key
          progTableUpdate.score = chalScore
          progTableUpdate.challengeID = challenge.key
          progTableUpdate.put()
          Challenge = challengeModel()
          Challenge.ownerID = users.get_current_user().user_id()
          Challenge.question = challenge.question
          Challenge.answer = challenge.answer
          Challenge.attachments = challenge.attachments
          Challenge.score = challenge.score
          Challenge.name = challenge.name
          Challenge.put()
          self.response.out.write('Correct')
          time.sleep(0.2)
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
      Challenge.ownerID = users.get_current_user().user_id()
      Challenge.question = self.request.get('question')
      Challenge.answer = self.request.get('answer')
      Challenge.attachments = uploaded_file
      Challenge.score = int(self.request.get('points'))
      Challenge.name = self.request.get('name')
      Challenge.put()
      time.sleep(0.2)
      page_params = {
        'login_url': users.create_login_url(),
        'logout_url': users.create_logout_url('/'),
        'user_email': email,
        'firstName': fname,
        'lastName': lname,
        'username': username
      }
      self.redirect('/manageChallenges')
    else:
      self.redirect('/')

#Edit Challenge
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
      challenge = ndb.Key(urlsafe=challengeId).get()
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
        Challenge = ndb.Key(urlsafe=challengeId).get()
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

# Leaderboard Handler
class leaderboardHandler(webapp2.RequestHandler):
  def get(self):
    email = get_user_email()
    fname = ""
    lname = ""
    username = ""
    rank = 0
    pubLobQry = lobbyModel.query(lobbyModel.ownerID == "118168406204694893029").get()
    lobbyID = self.request.get('lobbyID')

    if lobbyID:
      logging.error("hehehasjdflkjadf")
      lobby = ndb.Key(urlsafe=lobbyID).get()
    else:
      logging.error(pubLobQry.key)
      lobbyID = pubLobQry.key
      lobby = pubLobQry
    progTable = progressTable.query(progressTable.lobbyID == lobby.key)
    # userID 
    # score 
    leaderboardList = []
    for p in progTable:
      qry = accountModel.get_by_id(p.userID)
      if (len(leaderboardList) == 0):
        leaderboardList.append((qry.username, p.score))
      else:
        try:
          index = [x[0] for x in leaderboardList].index(qry.username)
          leaderboardList[index] = ( (qry.username, ( p.score + leaderboardList[index][1] )))
        except ValueError:
          thing_index = -1
          leaderboardList.append((qry.username, p.score))
    leaderboardList = sorted(leaderboardList,key=itemgetter(1))
    leaderboardList.reverse()
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
        'lobby': lobby,
        'login_url': users.create_login_url(),
        'logout_url': users.create_logout_url('/'),
        'board': leaderboardList,
        'rank': rank
      }
      render_template(self, 'leaderboard.html', page_params)
    else:
      self.redirect('/')
################## End Page Handlers ####################

################## url Mappings. ####################
# When a URL is clicked, goes to the function to take care of the specific request.
mappings = [
  ('/', MainHandler),
  ('/index', MainHandler),
  ('/email', EmailHandler),
  ('/createLobby', createLobbyHandler),
  ('/manageLobbies', manageLobbyHandler),
  ('/enterLobby', enterLobbyHandler),
  ('/manageChallenges', manageChallengeHandler),
  ('/editChallenge', editChallengeHandler),
  ('/uploadChallenge', uploadChallengeHandler),
  ('/solveChallenge', solveChallengeHandler),
  ('/acctManage', accountManagementHandler),
  ('/acctManageInfo', accountManageDisplay),
  ('/leaderboard', leaderboardHandler)
]
app = webapp2.WSGIApplication(mappings, debug=True)
