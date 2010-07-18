import cgi

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db

class Fixture(db.Model):
    round = db.IntegerProperty()
    date = db.DateProperty()
    homeTeam = db.StringProperty()
    awayTeam = db.StringProperty()
    homeScore = db.IntegerProperty()
    awayScore = db.IntegerProperty()

class Greeting(db.Model):
    author = db.UserProperty()
    content = db.StringProperty(multiline=True)
    date = db.DateTimeProperty(auto_now_add=True)

class MainPage(webapp.RequestHandler):
    def get(self):
        self.response.out.write('<html><body>')

	f = Fixture()

        f.round = 1
	f.homeTeam = "England"
	f.awayTeam = "Spain"
	f.homeScore = 2
	f.awayScore = 1

	f.put()

        fixtures = db.GqlQuery( "SELECT * FROM Fixture ORDER BY date DESC LIMIT 10" )

        for fixture in fixtures:
            if fixture.homeTeam:
                self.response.out.write('<b>%s</b>:\n' % fixture.homeTeam )


class Guestbook(webapp.RequestHandler):
    def post(self):
        greeting = Greeting()

        if users.get_current_user():
            greeting.author = users.get_current_user()

        greeting.content = self.request.get('content')
        greeting.put()
        self.redirect('/')

application = webapp.WSGIApplication(
                                     [('/', MainPage)],
                                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()

