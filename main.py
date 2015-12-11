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
from google.appengine.api import memcache
from google.appengine.api import users, mail
from google.appengine.ext import blobstore
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
	
    if memcache_usage():
      fname = memcache.get("user_fname")
      lname = memcache.get("user_lname")
      username = memcache.get("user_username")

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
    if memcache_usage():
        fname = memcache.get("user_fname")
        lname = memcache.get("user_lname")
        username = memcache.get("user_username")
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
    if memcache_usage():
        fname = memcache.get("user_fname")
        lname = memcache.get("user_lname")
        username = memcache.get("user_username")
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
    if memcache_usage():
        fname = memcache.get("user_fname")
        lname = memcache.get("user_lname")
        username = memcache.get("user_username")
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
    if memcache_usage():
        fname = memcache.get("user_fname")
        lname = memcache.get("user_lname")
        username = memcache.get("user_username")
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
      if memcache_usage():
        fname = memcache.get("user_fname")
        lname = memcache.get("user_lname")
        username = memcache.get("user_username")
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
    resultSize2 = 0
    if(results2.count()>0):
      resultSize2 = 1
    if email:
      if memcache_usage():
        fname = memcache.get("user_fname")
        lname = memcache.get("user_lname")
        username = memcache.get("user_username")
    page_params = {
      'user_email': email,
      'firstName': fname,
      'lastName': lname,
      'lobbynum': resultSize,
      'lobbynum2': resultSize2,
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
    lobbyID = ""
    lobbyName = ""
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
        if memcache_usage():
          fname = memcache.get("user_fname")
          lname = memcache.get("user_lname")
          username = memcache.get("user_username")
      else:
        self.redirect("/")
      pubLobQry = lobbyModel.query(lobbyModel.ownerID == "118168406204694893029").get()
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
      if memcache_usage():
        fname = memcache.get("user_fname")
        lname = memcache.get("user_lname")
        username = memcache.get("user_username")
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
    logging.error("asdfsdfsadf")
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
        time.sleep(0.5)
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
    if memcache_usage():
        fname = memcache.get("user_fname")
        lname = memcache.get("user_lname")
        username = memcache.get("user_username")
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
      if memcache_usage():
        fname = memcache.get("user_fname")
        lname = memcache.get("user_lname")
        username = memcache.get("user_username")
      chalObject = challengeModel.query(challengeModel.key == challenge.key).get()

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
          Challenge.blob_key = challenge.blob_key
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
    if memcache_usage():
      fname = memcache.get("user_fname")
      lname = memcache.get("user_lname")
      username = memcache.get("user_username")
      page_params = {
        'user_email': email,
        'firstName': fname,
        'lastName': lname,
        'username': username,
        'login_url': users.create_login_url(),
        'logout_url': users.create_logout_url('/'),
        'upload_url': blobstore.create_upload_url('/upload_file')
      }
      render_template(self, 'uploadChallenge.html', page_params)
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
    challenge = ""
    challengeId = self.request.get("challengeId")

    logging.error(challengeId)
    logging.error(challengeId)
    logging.error(challengeId)
    logging.error(challengeId)
    logging.error(challengeId)
    if email:
      if memcache_usage():
        fname = memcache.get("user_fname")
        lname = memcache.get("user_lname")
        username = memcache.get("user_username")
    
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
    'challengeId': self.request.get('challengeId'),
    'challengeName': challengeName,
    'challengeQuestion': challengeQuestion,
    'challengeAnswer': challengeAnswer,
    'challengePoints': challengePoints,
    'login_url': users.create_login_url(),
    'upload_url': blobstore.create_upload_url('/upload_fil'),
    'logout_url': users.create_logout_url('/')
    }
    render_template(self, 'editChallenge.html', page_params)


# Leaderboard Handler
class leaderboardHandler(webapp2.RequestHandler):
  def get(self):
    email = get_user_email()
    fname = ""
    lname = ""
    username = ""
    lobby = lobbyModel()
    rank = 0
    pubLobQry = lobbyModel.query(lobbyModel.ownerID == "118168406204694893029").get()
    lobbyID = self.request.get('lobbyID')

    if lobbyID:
      lobby = ndb.Key(urlsafe=lobbyID).get()
    else:
      if not pubLobQry:
        pubLobQry = 'break'
      else:
        lobbyID = pubLobQry.key
        lobby = pubLobQry
    if pubLobQry == 'break':
      self.redirect('/')
    else:
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
        if memcache_usage():
          fname = memcache.get("user_fname")
          lname = memcache.get("user_lname")
          username = memcache.get("user_username")
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
########################################################################################################################
#############################################START SAM TESTING##########################################################
########################################################################################################################

class FileUploadHandler(blobstore_handlers.BlobstoreUploadHandler):
  def post(self):
    email = get_user_email()
    if email:
      try:
        if len(self.get_uploads()) == 1:
          upload = self.get_uploads()[0]
          file_upload = challengeModel(
            ownerID=users.get_current_user().user_id(),
            blob_key=upload.key(),
            name=self.request.get('name'),
            question=self.request.get('question'),
            answer=self.request.get('answer'),
            score=int(self.request.get('points'))
          )
        else:
          file_upload = challengeModel(
            ownerID=users.get_current_user().user_id(),
            name=self.request.get('name'),
            question=self.request.get('question'),
            answer=self.request.get('answer'),
            score=int(self.request.get('points'))
          )
        file_upload.put()
        self.redirect('/uploaded/')
        time.sleep(0.3)
        # self.redirect('/view_photo/%s' % upload.key())
      except:
        self.error(500)
    else:
      self.redirect('/')

class FileUploadHandler2(blobstore_handlers.BlobstoreUploadHandler):
  def post(self):
    email = get_user_email()
    if email:
      try:
        challengeId = self.request.get("challengeId")
        if len(self.get_uploads()) == 1:
          upload = self.get_uploads()[0]
          challenge = ndb.Key(urlsafe=challengeId).get()
          challenge.ownerID = users.get_current_user().user_id()
          challenge.blob_key = upload.key()
          challenge.name = self.request.get('name')
          challenge.question = self.request.get('question')
          challenge.answer = self.request.get('answer')
          challenge.score = int(self.request.get('points'))
          challenge.put()
        else:
          challenge = ndb.Key(urlsafe=challengeId).get()
          challenge.ownerID = users.get_current_user().user_id()
          challenge.blob_key = challenge.blob_key
          challenge.name = self.request.get('name')
          challenge.question = self.request.get('question')
          challenge.answer = self.request.get('answer')
          challenge.score = int(self.request.get('points'))
          challenge.put()
        self.redirect('/uploaded/')
        time.sleep(0.3)
        # self.redirect('/view_photo/%s' % upload.key())
      except:
        self.error(500)
    else:
      self.redirect('/')

class ViewFileHandler(blobstore_handlers.BlobstoreDownloadHandler):
  def get(self, file_key):
    email = get_user_email()
    if email:
      if not blobstore.get(file_key):
        self.error(404)
      else:
        self.send_blob(blobstore.BlobInfo.get(file_key), save_as=True)
    else:
      self.redirect('/')


class uploadedHandler(webapp2.RequestHandler):
  def get(self):
    email = get_user_email()
    fname = ""
    lname = ""
    username = ""
    if email:
      if memcache_usage():
        fname = memcache.get("user_fname")
        lname = memcache.get("user_lname")
        username = memcache.get("user_username")
      page_params = {
        'user_email': email,
        'login_url': users.create_login_url(),
        'logout_url': users.create_logout_url('/'),
        'firstName': fname,
        'lastName': lname,
        'username': username,
      }
      self.redirect('/manageChallenges')
    else:
      self.redirect('/')


def memcache_usage():
	email = get_user_email()
	fname = ''
	lname = ''
	username = ''
	if email:
		if memcache.get("user_"):
			return True
		else:
			qry = accountModel.get_by_id(users.get_current_user().user_id())
			if qry:
				fname = qry.firstName
				lname = qry.lastName
				username = qry.username
			else:  
				lm = lobbyModel.query(lobbyModel.ownerID == "118168406204694893029 ").get()
				if lm:
					publob = lobbyAccessModel(lobbyID=lm.key, userID=users.get_current_user().user_id())
					lobbyAccessModel.put(publob)
				user = accountModel(id=users.get_current_user().user_id(), firstName=fname, lastName=lname, username=email.split("@", 1)[0])
				accountModel.put(user)
				
			memcache.set_multi({"fname": fname,
						"lname": lname,
						"username": username},
						key_prefix="user_", time=3600)
			return True
	return False
	
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
  ('/leaderboard', leaderboardHandler),
  ('/upload_file', FileUploadHandler),
  ('/upload_fil', FileUploadHandler2),
  ('/view_file/([^/]+)?', ViewFileHandler),
  ('/uploaded*', uploadedHandler),
  ('/uploaded/*', uploadedHandler)
]
app = webapp2.WSGIApplication(mappings, debug=True)
