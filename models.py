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
  lobbyName = ndb.TextProperty()
  ownerID = ndb.StringProperty()


# Lobby Access table
class lobbyAccessModel(ndb.Model):
  lobbyID = ndb.KeyProperty()
  userID = ndb.StringProperty()


# Challenge management table
class challengeModel(ndb.Model):
  ownerID = ndb.StringProperty()
  question = ndb.TextProperty()
  answer = ndb.TextProperty()
  score = ndb.IntegerProperty()
  name = ndb.StringProperty()
  blob_key = ndb.BlobKeyProperty()


# Challenge Access table
class challengeAccessModel(ndb.Model):
  challengeID = ndb.KeyProperty()
  lobbyID = ndb.KeyProperty()


# progress tracking table
class progressTable(ndb.Model):
  userID = ndb.StringProperty()
  lobbyID = ndb.IntegerProperty()
  challengeID = ndb.StringProperty()
  ################## End NDB Models ####################
