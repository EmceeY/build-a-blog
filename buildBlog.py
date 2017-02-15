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

    def render_front(self, title="", art="", error="", ):
        arts = db.GqlQuery("SELECT * FROM Post "
                           "ORDER BY created DESC")
        self.render("base.html", title=title, art=art, error=error, arts=arts)


class Post(db.Model):
    title = db.StringProperty(required = True)
    art = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

    def render(self):
        self._render_test = self.content.replace('\n', '<br>')
        return render_str("main_page.html", p = self)

class New_Post(Handler):

    def get(self):
        t = jinja_env.get_template("post1.html")
        self.render(t)

    def post(self):
        title = self.request.get("title")
        art = self.request.get("art")

        if title and art:
            a = Post(title = title, art = art)
            a.put()
            self.redirect("/")
        else:
            error = "we need both a title and some content!"
            self.render_front(title, art, error)

class MainPage(Handler):
    def get(self):
        self.render_front()

class ViewPostHandler(Handler):
    def get(self, id):
        t = jinja_env.get_template("main_page.html")
        if id == None:
            self.response.write("There are no blog entries with that ID!")
        else:
            Post.get_by_id(int(id), parent=None)
            title = Post.title
            art = Post.art
            self.render(t, title=title, art=art)

        #else:
            #self.response.write("Sorry, there is no post with that ID")

app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/newpost', New_Post),
    webapp2.Route('/blog/<id:\d+>', ViewPostHandler),
], debug = True)
