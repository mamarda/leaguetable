_author__ = 'anton.mcconville@gmail.com'

import wsgiref.handlers
import cgi
from google.appengine.ext import webapp
from google.appengine.api import users
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
import atom.url
import gdata.service
import gdata.alt.appengine
import gdata.spreadsheet.service

class Fixture(db.Model):
    round = db.IntegerProperty()
    date = db.DateProperty()
    homeTeam = db.StringProperty()
    awayTeam = db.StringProperty()
    homeScore = db.IntegerProperty()
    awayScore = db.IntegerProperty()