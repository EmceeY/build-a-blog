import os
import webapp2
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
                                autoescape=True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))


class Data(db.Model):
    title = db.StringProperty(required = True)
    art = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

class New_Post(Handler):

    def render_front(self, title="", art="", error="", ):
        arts = db.GqlQuery("SELECT * FROM Data "
                           "ORDER BY created DESC")
        self.render("base.html", title=title, art=art, error=error, arts=arts)

    def get(self):
        t = jinja_env.get_template("post.html")
        content = t.render()
        self.render_front(content)

    def post(self):
        title = self.request.get("title")
        art = self.request.get("art")

        if title and art:
            a = Data(title = title, art = art)
            a.put()
            self.redirect("/")
        else:
            error = "we need both a title and some artwork!"
            self.render_front(title, art, error)

class MainPage(Handler):
    def render_front(self, title="", art="", error="", ):
        arts = db.GqlQuery("SELECT * FROM Data "
                           "ORDER BY created DESC")
        self.render("base.html", title=title, art=art, error=error, arts=arts)

    def get(self):
        self.render_front()

class Posts(Handler):
    def render_front(self, title="", art="", error="", ):
        arts = db.GqlQuery("SELECT * FROM Data "
                           "ORDER BY created DESC")
        self.render("main_page.html", title=title, art=art, error=error, arts=arts)

class ViewPostHandler(webapp2.RequestHandler):
    def get(self, id):
        t = jinja_env.get_template('main_page.html')
        content = t.render(title, art)
        self.response.write(content)

app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/newpost', New_Post),
    webapp2.Route('/blog/<id:\d+>', ViewPostHandler),
], debug = True)
