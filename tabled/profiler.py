__author__ = 'anton.mcconville@gmail.com'

import wsgiref.handlers
import cgi
from google.appengine.ext import webapp
from google.appengine.api import users
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db

class Profile( db.Model ):
    account = db.StringProperty( multiline=True )
    imports = db.IntegerProperty()
    retrievals = db.IntegerProperty()
    spreadsheet = db.StringProperty( multiline=True )
    lastlookedat = db.StringProperty( multiline=True )

class ProfileList( webapp.RequestHandler ):

  def get(self):
      
    self.response.headers['Content-Type'] = 'text/plain'
    self.response.out.write('<?xml version="1.0"?>\n')    
    profiles = db.GqlQuery("SELECT * FROM Profile where account = :1", users.get_current_user().email())

    for p in profiles:
      self.response.out.write('<profile account=\"%s\" imports=\"%s\" sheet=\"%s\"/>\n' % ( p.account, p.imports, p.spreadsheet ) )
        
def main():
  application = webapp.WSGIApplication([('/.*', ProfileList),], debug=True)
  wsgiref.handlers.CGIHandler().run(application)

if __name__ == '__main__':
  main()
