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
    
class Import(webapp.RequestHandler):  
    
  def storeFixtures(self, sheet, feed ):
    
    count =0
    
    for i, entry in enumerate( feed.entry ):  
        
        count = count +1
        
        f = Fixture()   
        f.identifier = count     
        f.date = entry.custom['date'].text
        f.homeTeam = entry.custom['home'].text.strip()
        f.awayTeam = entry.custom['away'].text.strip()
        
        score = entry.custom['score'].text
        
        if score:
            scores = score.split(':')
            f.homeScore = scores[0]
            f.awayScore = scores[1]
        else:
            f.homeScore = "empty"
            f.awayScore = "empty"
        

        f.put()
        
        #twitter.log( "%s imported fixtures" % users.get_current_user().nickname() )

        self.response.out.write( '    <fixture identifier= \"%s\", date=\"%s\" home=\"%s\" away=\"%s\" homescore=\"%s\" awayscore=\"%s\"/>\n' % ( f.identifier, f.date, f.homeTeam, f.awayTeam, f.homeScore, f.awayScore ) )
        
       
  def get(self):

    # Import a client to talk to Google Data API services. 
    client = gdata.spreadsheet.service.SpreadsheetsService()
    gdata.alt.appengine.run_on_appengine(client)

    feed_url = self.request.get('feed_url')

    session_token = None
    # Find the AuthSub token and upgrade it to a session token.
    auth_token = gdata.auth.extract_auth_sub_token_from_url(self.request.uri)
    if auth_token:
      # Upgrade the single-use AuthSub token to a multi-use session token.
      session_token = client.upgrade_to_session_token(auth_token)
    if session_token and users.get_current_user():
      client.token_store.add_token(session_token)
    elif session_token:
      client.current_token = session_token
    
    self.response.headers['Content-Type'] = 'text/plain'
    self.response.out.write('<?xml version="1.0"?>\n')
    self.fetch_feed( client, 'http://spreadsheets.google.com/feeds/spreadsheets/private/full' ) 

  def sheetName(self, url):
      
    sheet="BASICIMPORT"
    
    offset=0
  
    if url.find('?') > -1:
      sheet = url.split('?')[1]
      offset = url.split('?')[2]
      
      sheet = urllib.url2pathname( sheet )
     
    return sheet, offset

  def fetch_feed(self, client, feed_url):
    # Attempt to fetch the feed.
    if not feed_url:
      self.response.out.write(
          'No feed_url was specified for the app to fetch.<br/>')
      example_url = atom.url.Url('http', settings.HOST_NAME, path='/step3', 
          params={'feed_url':
              'http://docs.google.com/feeds/documents/private/full'}
          ).to_string()
      self.response.out.write('Here\'s an example query which will show the'
          ' XML for the feed listing your Google Documents <a '
          'href="%s">%s</a>' % (example_url, example_url))
      return
    try:
    
      feed = client.GetSpreadsheetsFeed()
      
      spreadsheet = "Standings"
      offset = self.sheetName( self.request.uri )[1]
        
      if spreadsheet == "BASICIMPORT": 
              
        if users.get_current_user():
          myUser = users.get_current_user();
          self.response.out.write( '<spreadsheets owner=\"%s\">\n'%myUser.email() )

          for i, entry in enumerate( feed.entry ):
            self.response.out.write( '   <spreadsheet name=\"%s\"/>\n' % entry.title.text )
        
          self.response.out.write( '</spreadsheets>')
      else:

        for i, entry in enumerate( feed.entry ):
        
            if( entry.title.text == spreadsheet ):
                id_parts = feed.entry[i].id.text.split('/')
                self.curr_key = id_parts[len(id_parts) - 1]
                feed = client.GetWorksheetsFeed(self.curr_key)
                id_parts = feed.entry[0].id.text.split('/')
                self.curr_wksht_id = id_parts[len(id_parts) - 1]
                feed = client.GetListFeed( self.curr_key, self.curr_wksht_id ) 
            
                self.response.out.write( '<fixtures>' )
                self.storeFixtures( spreadsheet, feed )
                self.response.out.write( '</fixtures>' )


    except gdata.service.RequestError, request_error:
      if request_error[0]['status'] == 401:
        next = atom.url.Url('http', settings.HOST_NAME, path='/', params={'feed_url': feed_url})
        auth_sub_url = client.GenerateAuthSubURL(next, feed_url, secure=False, session=True)
        self.response.out.write('<a href="%s">' % (auth_sub_url))
        self.response.out.write('Click here to authorize this application to view the feed</a>')
      else:
        self.response.out.write(
            'Something went wrong, here is the error object: %s ' % (str(request_error[0])))

def main():
  application = webapp.WSGIApplication([('/.*', Import),], debug=True)
  wsgiref.handlers.CGIHandler().run(application)

if __name__ == '__main__':
  main()
