import cgi
import logging
import wsgiref.handlers
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.api import urlfetch
import urllib # Used to unescape URL parameters.
import gdata.service
import gdata.alt.appengine
import gdata.auth
import atom
import atom.http_interface
import atom.token_store
import atom.url
import settings
import twitter
import profiler
import importer
import os
from google.appengine.ext.webapp import template

class Stuff(webapp.RequestHandler):

  def get(self):

    template_values ={}

    path = os.path.join(os.path.dirname(__file__), 'parent.html')
    self.response.out.write(template.render(path, template_values))

def main():
  def main():
    application = webapp.WSGIApplication([('/.*', Stuff),], debug=True)
    wsgiref.handlers.CGIHandler().run(application)

if __name__ == '__main__':
  main()
