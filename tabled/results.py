__author__ = 'anton.mcconville@gmail.com'

import logging
import wsgiref.handlers
import cgi
import urllib
import time
from google.appengine.ext import webapp
from google.appengine.api import users
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from datetime import date
import atom.url
import gdata.service
import gdata.alt.appengine
import settings
import gdata.spreadsheet.service
import twitter
from time import sleep
from google.appengine.api import urlfetch

class Fixture(db.Model):
    identifier = db.IntegerProperty()
    date = db.StringProperty()
    homeTeam = db.StringProperty()
    awayTeam = db.StringProperty()
    homeScore = db.StringProperty()
    awayScore = db.StringProperty()
    
class Results(webapp.RequestHandler):  
    
  def post(self):
    
    identifier = self.request.body.split( 'id:' )[1]
    
    identifier = int(identifier.split(',')[0])
    
    homescore = self.request.body.split( 'homescore:' )[1]
    
    homescore = homescore.split(',')[0]
    
    awayscore = self.request.body.split( 'awayscore:' )[1]
    
    awayscore = awayscore.split('}')[0]
    
    logging.info( 'HIT %s' % identifier )
    
    fixtures = db.GqlQuery("SELECT * FROM Fixture")
       
    for fixture in fixtures:
        if fixture.identifier == identifier:
            logging.info( 'MATCH %s', identifier )
            fixture.homeScore = homescore
            fixture.awayScore = awayscore
            fixture.put()
            
            twitter.log( "%s added a result for fixture %s: %s %s - %s %s." % ( users.get_current_user().nickname(), fixture.identifier, fixture.homeTeam, fixture.homeScore, fixture.awayTeam, fixture.awayScore  ) )
            
            logging.debug( "%s added a result for fixture %s: %s %s - %s %s." % ( users.get_current_user().nickname(), fixture.identifier, fixture.homeTeam, fixture.homeScore, fixture.awayTeam, fixture.awayScore  )  )
            
            break;
    
    
  def get(self):
      
    fixtures = db.GqlQuery("SELECT * FROM Fixture")
      
    teams = []

    newteam = True
    hometeam = False
    awayteam = False
    
    self.response.headers['Content-Type'] = 'text/json'
    self.response.out.write('{ identifier: \"fixture", label: \"fixture\",items:[ ')
 
    count = 0
    
    week = 1
 
    for fixture in fixtures:
       count = count +1 
        
       week = week + ( count / 4 ) 
       
       hometeam = fixture.homeTeam #.split("[")[0]
       awayteam = fixture.awayTeam #.split("[")[0]
       
       homescore = fixture.homeScore
       awayscore = fixture.awayScore
       
       if homescore == "empty":
           homescore = '-'
           
       if awayscore == "empty":
           awayscore = '-'
        
       if count != 1:
           self.response.out.write(',')
            
       self.response.out.write('{ fixture:%s, week:\"%s\", date:\"%s\", hometeam:\"%s\", awayteam:\"%s\", homescore:"%s", awayscore:"%s" }' % ( fixture.identifier, week, fixture.date, hometeam, awayteam, homescore, awayscore ) )
      
    self.response.out.write(']}')
    

def main():
  application = webapp.WSGIApplication([('/.*', Results),], debug=True)
  wsgiref.handlers.CGIHandler().run(application)

if __name__ == '__main__':
  main()
