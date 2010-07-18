import wsgiref.handlers
import cgi
import datetime
import urllib
import base64

from google.appengine.ext import webapp
from google.appengine.api import urlfetch

class SendChime(webapp.RequestHandler):
    
   def get(self):
     self.response.headers['Content-Type'] = 'text/plain'
     username = self.request.get("squadbuilder")
     login = "squadbuilder"
     password = ""
     chime = self.get_chime()
     payload= {'status' : chime, 'source' : "TeamBuilder"}
     payload= urllib.urlencode(payload)
     base64string = base64.encodestring('%s:%s' % (login, password))[:-1]
     headers = {'Authorization': "Basic %s" % base64string}
     url = "http://twitter.com/statuses/update.xml"
     result = urlfetch.fetch( url, payload=payload, method=urlfetch.POST, headers=headers )
     self.response.out.write( result.content )
 
   def get_chime(self):
     now = datetime.datetime.now()
     chime = "Tweeting again from Google App Engine"
     return chime
     
def main():
   application = webapp.WSGIApplication([('/.*', SendChime),], debug=True)
   wsgiref.handlers.CGIHandler().run(application)

if __name__ == '__main__':
  main()