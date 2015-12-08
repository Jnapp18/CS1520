from google.appengine.ext import ndb

################## NDB Models ####################
# Account management table
class accountModel(ndb.Model):
  firstName = ndb.StringProperty()
  lastName = ndb.StringProperty()
  username = ndb.StringProperty()
  score = ndb.IntegerProperty(default=0)


# Lobby management table
class lobbyModel(ndb.Model):
  lobbyID = ndb.IntegerProperty()
  lobbyName = ndb.TextProperty()
  publicBool = ndb.BooleanProperty()
  ownerID = ndb.IntegerProperty()


# Lobby Access table
class lobbyAccessModel(ndb.Model):
  lobbyID = ndb.IntegerProperty()
  userID = ndb.IntegerProperty()


# Challenge management table
class challengeModel(ndb.Model):
  challengeID = ndb.IntegerProperty()
  ownerID = ndb.StringProperty()
  question = ndb.TextProperty()
  answer = ndb.TextProperty()
  attachments = ndb.BlobProperty
  score = ndb.IntegerProperty()
  name = ndb.StringProperty()


# Challenge Access table
class challengeAccessModel(ndb.Model):
  challengeID = ndb.IntegerProperty()
  lobbyID = ndb.IntegerProperty()


# progress tracking table
class progressTable(ndb.Model):
  userID = ndb.StringProperty()
  lobbyID = ndb.IntegerProperty()
  challengeID = ndb.StringProperty()
  ################## End NDB Models ####################
