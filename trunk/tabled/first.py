import cgi
import logging
import wsgiref.handlers
from google.appengine.ext import webapp

import os
from google.appengine.ext.webapp import template

class Fetcher(webapp.RequestHandler):

  def get(self):

    template_values ={}

    path = os.path.join(os.path.dirname(__file__), 'parent.html')
    self.response.out.write(template.render(path, template_values))

def main():
  application = webapp.WSGIApplication([('/.*', Fetcher),], debug=True)
  wsgiref.handlers.CGIHandler().run(application)

if __name__ == '__main__':
  main()
