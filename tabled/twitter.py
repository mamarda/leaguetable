import wsgiref.handlers
import cgi
import datetime
import urllib
import base64

from google.appengine.ext import webapp
from google.appengine.api import urlfetch
    
def log( message ):
   login = "squadbuilder"
   password = "zaphod42"
   chime = message
   payload= {'status' : chime, 'source' : "TeamBuilder"}
   payload= urllib.urlencode(payload)
   base64string = base64.encodestring('%s:%s' % (login, password))[:-1]
   headers = {'Authorization': "Basic %s" % base64string}
   url = "http://twitter.com/statuses/update.xml"
   result = urlfetch.fetch( url, payload=payload, method=urlfetch.POST, headers=headers )
 
def main():
   application = webapp.WSGIApplication([('/.*', SendChime),], debug=True)
   wsgiref.handlers.CGIHandler().run(application)

if __name__ == '__main__':
  main()