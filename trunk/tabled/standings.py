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
import twitter
from time import sleep
from google.appengine.api import urlfetch
import fixture

class Standing(db.Model):
    teamName = db.StringProperty()
    homeGameCount = db.IntegerProperty()
    awayGameCount = db.IntegerProperty()
    homeWins = db.IntegerProperty()
    homeDraws = db.IntegerProperty()
    homeLosses = db.IntegerProperty()
    awayWins = db.IntegerProperty()
    awayDraws = db.IntegerProperty()
    awayLosses = db.IntegerProperty()
    points = db.IntegerProperty()
    goalsFor = db.IntegerProperty()
    goalsAgainst = db.IntegerProperty()
    
    def initialize(self):
        self.homeGameCount = 0
        self.awayGameCount = 0
        self.homeWins = 0
        self.homeDraws = 0
        self.homeLosses = 0
        self.awayWins = 0
        self.awayDraws = 0
        self.awayLosses = 0
        self.points = 0
        self.goalsFor = 0
        self.goalsAgainst = 0
    
class Results(webapp.RequestHandler):  
    
  def get(self):
      
      fixtures = db.GqlQuery("SELECT * FROM Fixture")
            
      

      teams = []

      newteam = True
      hometeam = False
      awayteam = False
 
      for fixture in fixtures:
          
          for team in teams:
              if( team.teamName == fixture.homeTeam ):
                  newteam = False
                  break;
                                
          if( newteam == True ):          
              newstanding = Standing()
              newstanding.teamName = fixture.homeTeam
              newstanding.initialize()
          else:
              newstanding = team
              teams.remove(team)
              newteam = True

          if( fixture.homeScore != "empty" ):
                                          
              if( int(fixture.homeScore) > int(fixture.awayScore) ):
                  newstanding.homeWins = newstanding.homeWins +1
                  newstanding.points = newstanding.points + 3
              elif( int(fixture.homeScore) == int(fixture.awayScore) ):
                  newstanding.homeDraws = newstanding.homeDraws +1
                  newstanding.points = newstanding.points + 1
              else:
                  newstanding.homeLosses = newstanding.homeLosses +1

              newstanding.goalsFor = newstanding.goalsFor + int(fixture.homeScore)
              newstanding.goalsAgainst = newstanding.goalsAgainst + int(fixture.awayScore)
          
          teams.append( newstanding )
          
      for fixture in fixtures:

          for team in teams:
                if( team.teamName == fixture.awayTeam ):
                    newstanding = team
                    teams.remove(team)
                    break;

          if( fixture.awayScore != "empty" ):
                                         
              if( int(fixture.homeScore) > int(fixture.awayScore) ):
                      newstanding.awayLosses = newstanding.awayLosses +1
              elif( int(fixture.homeScore) == int(fixture.awayScore) ):
                  newstanding.awayDraws = newstanding.awayDraws +1
                  newstanding.points = newstanding.points + 1
              else:
                  newstanding.awayWins = newstanding.awayWins +1
                  newstanding.points = newstanding.points + 3


              newstanding.goalsFor = newstanding.goalsFor + int(fixture.awayScore)
              newstanding.goalsAgainst = newstanding.goalsAgainst + int(fixture.homeScore)
             
          teams.append( newstanding )

          
      self.response.headers['Content-Type'] = 'text/json'
      self.response.out.write('{ identifier: \"standing", label: \"standing\",items:[ ')


      count = 0

      for team in teams:
          
          goalDifference = team.goalsFor - team.goalsAgainst
          
          wins = team.homeWins + team.awayWins
          
          draws = team.homeDraws + team.awayDraws
          
          losses = team.homeLosses + team.awayLosses
          
          played = wins + draws + losses

          count = count +1
          
          if count != 1:
              self.response.out.write(',')
              
          self.response.out.write('{ standing: \"%s\", team:\"%s\", points:%s, goalsfor:%s, goalsagainst:%s, difference:%s, wins:%s, draws:%s, losses:%s, played:%s}' % ( count, team.teamName, team.points, team.goalsFor, team.goalsAgainst, goalDifference, wins, draws, losses, played  ) )
      
      self.response.out.write(']}')
    

def main():
  application = webapp.WSGIApplication([('/.*', Results),], debug=True)
  wsgiref.handlers.CGIHandler().run(application)

if __name__ == '__main__':
  main()
