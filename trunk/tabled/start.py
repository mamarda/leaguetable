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

class Fetcher(webapp.RequestHandler):

  def get(self):
    
    self.response.headers['Content-Type'] = 'text/html'

    self.response.out.write(""" <html>\n  <head>\n   <title>League Table</title>\n   <link rel=\"stylesheet\" type=\"text/css\" href="style.css"/>\n     </head>\n<body class="claro">""")
       
    self.response.out.write("""<div class ="bar" id="nav"><div class="gbar"><b>League Table</b></div>""")
    if users.get_current_user():
      myUser = users.get_current_user();
      self.response.out.write( '<div class="user"><b>%s</b>' % ( myUser.email() ) ) 
      self.response.out.write( ' | <a href="%s"> Sign out</a></div>' % (
          users.create_logout_url('http://%s/' % settings.HOST_NAME)))
    else:
      self.response.out.write('<div class="user"><a href="%s">Sign in</a></div>' % (
          users.create_login_url('http://%s/' % settings.HOST_NAME)))
    self.response.out.write('</div>')

    # Initialize a client to talk to Google Data API services.
    client = gdata.service.GDataService()
    gdata.alt.appengine.run_on_appengine(client)

    session_token = None
    # Find the AuthSub token and upgrade it to a session token.
    auth_token = gdata.auth.extract_auth_sub_token_from_url(self.request.uri)
    if auth_token:
      # Upgrade the single-use AuthSub token to a multi-use session token.
      session_token = client.upgrade_to_session_token(auth_token)
    if session_token and users.get_current_user():
      # If there is a current user, store the token in the datastore and
      # associate it with the current user. Since we told the client to
      # run_on_appengine, the add_token call will automatically store the
      # session token if there is a current_user.
      client.token_store.add_token(session_token)
    elif session_token:
      # Since there is no current user, we will put the session token
      # in a property of the client. We will not store the token in the
      # datastore, since we wouldn't know which user it belongs to.
      # Since a new client object is created with each get call, we don't
      # need to worry about the anonymous token being used by other users.
      client.current_token = session_token

    # Get the URL for the desired feed and get the display option.
    feed_url = self.request.get('feed_url')
    erase_tokens = self.request.get('erase_tokens')
    if erase_tokens:
      self.EraseStoredTokens()
    show_xml = self.request.get('xml')

    if show_xml:
      checked_string = 'checked'
    else:
      checked_string = ''
      
    if users.get_current_user():
     
      feed_url = self.request.get('feed_url')

      next = atom.url.Url('http', settings.HOST_NAME, params={'feed_url': feed_url})

      tokens = gdata.alt.appengine.load_auth_tokens()
      
      spreadsheets = False;
      contacts = False;
      
      for token_scope in tokens:
          logging.debug( 'TOKEN: %s' % token_scope )
          variable = token_scope.split("/")
          
          for v in variable:
              logging.debug( 'TOKEN: %s' % v )
          if variable[2] == "spreadsheets.google.com":
              spreadsheets = True;
      
      self.response.out.write( '<script language=\"javascript\" type=\"text/javascript\">' )
      if spreadsheets == False:
        self.response.out.write('document.location.href = \"%s"'%( self.GenerateScopeRequestLink(client, 'http://spreadsheets.google.com/feeds/' ) ) )
     
      self.response.out.write('</script>')
      
      newaccount = True;
      
      profiles = db.GqlQuery("SELECT * FROM Profile WHERE account = :1", users.get_current_user().email() )
      
      for p in profiles:
          newaccount = False;
          
      if newaccount == True:
          
          newprofile = profiler.Profile()         
          newprofile.account = users.get_current_user().email()        
          newprofile.put()
          
          # twitter.log( "Created a new account for %s" % users.get_current_user().nickname() )

      template_values ={}

      path = os.path.join(os.path.dirname(__file__), 'index.html')
      self.response.out.write(template.render(path, template_values))
        
      #self.response.out.write( '<div id="myContent"><p>Alternative content</p></div></body></html>')

      #if users.get_current_user():
       # twitter.log( "%s logged into leaguetable." % users.get_current_user().nickname() )

    else:
      self.response.out.write("""<div id="wrap"> """ )
      if not feed_url:
        self.writeContent()
      else:
        self.FetchFeed(client, feed_url, show_xml)
      #self.response.out.write('</div>')
    
  def GenerateScopeRequestLink(self, client, scope):
    return client.GenerateAuthSubURL('http://%s/' % (
            settings.HOST_NAME,),
        scope, secure=False, session=True)

  def writeContent(self):
    self.response.out.write("""<div style="text-align: center; "><div style="margin-bottom: 0px; margin-left: auto; margin-right: auto; margin-top: 0px; overflow: hidden; position: relative; word-wrap: break-word;  background: rgb(255, 255, 255); text-align: left; width: 700px; " id="body_content"><div style="margin-left: 0px; position: relative; width: 700px; z-index: 5; " id="body_layer"><div style="height: 0px; line-height: 0px; "></div><div style="height: 304px; width: 405px;  height: 304px; left: -19px; position: absolute; top: 73px; width: 405px; z-index: 1; ">
            <img src="/files/images/redball.jpg" alt="" style="border: none;" /></div><div id="id1" style="height: 327px; left: 200px; position: absolute; top: 70px; width: 286px; z-index: 1;"><div>
                <p style="padding-bottom: 0pt; padding-top: 0pt;"><b>Welcome to League Table</b></p>
                <p>This application makes a league table from soccer results.</p>
                <p>It allows coaches to update a score and instantly
                see the league standings update. </p>
                <p><form action="%s" method="post"><input type="submit" value="Sign in" name="signIn"/></form></p></div></div><div style="height: 250px; line-height: 250px;"></div></div><div style="height: 150px; margin-left: 0px; position: relative; width: 400px; z-index: 15; " id="footer_layer"><div style="height: 0px; line-height: 0px; float: right; "><img src="files/images/gae.gif" alt="" style="border: none;" /></div></div></div></div>"""%users.create_login_url('http://%s/' % settings.HOST_NAME) ) 

  def GenerateFeedRequestLink(self, feed_url):
    return atom.url.Url('http', settings.HOST_NAME, path='/', 
        params={'feed_url':feed_url}).to_string()

  def FetchFeed(self, client, feed_url, show_xml=False):
    # Attempt to fetch the feed.
    try:
      if show_xml:
        response = client.Get(feed_url, converter=str)
        response = response.decode('UTF-8')
        self.response.out.write(cgi.escape(response))
      else:
        response = client.Get(feed_url)
        if isinstance(response, atom.Feed):
          self.RenderFeed(response)
        elif isinstance(response, atom.Entry):
          self.RenderEntry(response)
        else:
          self.response.out.write(cgi.escape(response.read()))
    except gdata.service.RequestError, request_error:
      # If fetching fails, then tell the user that they need to login to
      # authorize this app by logging in at the following URL.
      if request_error[0]['status'] == 401:
        # Get the URL of the current page so that our AuthSub request will
        # send the user back to here.
        next = self.request.uri
        auth_sub_url = client.GenerateAuthSubURL(next, feed_url,
            secure=False, session=True)
        self.response.out.write('<a href="%s">' % (auth_sub_url))
        self.response.out.write(
            'Click here to authorize this application to view the feed</a>')
      else:
        self.response.out.write(
            'Something else went wrong, here is the error object: %s ' % (
                str(request_error[0])))

  def RenderFeed(self, feed):
    self.response.out.write('<h2>Feed Title: %s</h2>' % (
        feed.title.text.decode('UTF-8')))
    for link in feed.link:
      self.RenderLink(link)
    for entry in feed.entry:
      self.RenderEntry(entry)

  def RenderEntry(self, entry):
    self.response.out.write('<h3>Entry Title: %s</h3>' % (
        entry.title.text.decode('UTF-8')))
    if entry.content and entry.content.text:
      self.response.out.write('<p>Content: %s</p>' % (
          entry.content.text.decode('UTF-8')))
    elif entry.summary and entry.summary.text:
      self.response.out.write('<p>Summary: %s</p>' % (
          entry.summary.text.decode('UTF-8')))
    for link in entry.link:
      self.RenderLink(link)

  def RenderLink(self, link):
    if link.rel == 'alternate' and link.type == 'text/html':
      self.response.out.write(
          'Link: <a href="%s">alternate HTML</a><br/>' % link.href)
    elif link.type == 'application/atom+xml':
      self.response.out.write(
          'Link: <a href="/?feed_url=%s">Fetch %s link (%s)</a><br/>' % (
              urllib.quote_plus(link.href), link.rel, link.type))
    else:
      self.response.out.write(
          'Link: <a href="%s">%s link (%s)</a><br/>' % (link.href, link.rel,
              link.type))
    
  def DisplayAuthorizedUrls(self):
    self.response.out.write('<h4>Stored Authorization Tokens</h4><ul>')
    tokens = gdata.alt.appengine.load_auth_tokens()
    for token_scope in tokens:
      #self.response.out.write('<li><a href="/?feed_url=%s">%s*</a></li>' % (
      self.response.out.write("%s" % ( str(token_scope)))
    self.response.out.write(
        '</ul>To erase your stored tokens, <a href="%s">click here</a>' % (
            atom.url.Url('http', settings.HOST_NAME, path='/', 
                params={'erase_tokens':'true'}).to_string()))

  def EraseStoredTokens(self):
    gdata.alt.appengine.save_auth_tokens({})


class Acker(webapp.RequestHandler):
  """Simulates an HTML page to prove ownership of this domain for AuthSub 
  registration."""

  def get(self):
    self.response.headers['Content-Type'] = 'text/plain'
    self.response.out.write('This file present for AuthSub registration.')


def main():
  application = webapp.WSGIApplication([('/', Fetcher), 
      ('/google72db3d6838b4c438.html', Acker)], 
      debug=True)
  wsgiref.handlers.CGIHandler().run(application)

if __name__ == '__main__':
  main()
