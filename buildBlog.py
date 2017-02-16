import os
import re
from string import letters
import webapp2
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
                                autoescape=True)

def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class MainPage(Handler):
    def get(self):
        posts = db.GqlQuery("select * from Post order by created DESC limit 5")
        self.render('front.html', posts = posts)

def blog_key(name = 'default'):
    return db.Key.from_path('blogs', name)

class Post(db.Model):
    title = db.StringProperty(required = True)
    content = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

    def render(self):
        self._render_text = self.content.replace('\n', '<br>')
        return render_str("post.html", a = self)

class New_Post(Handler):
    def get(self):
        t = jinja_env.get_template("submit.html")
        self.render(t)

    def post(self):
        title = self.request.get("title")
        content = self.request.get("content")

        if title and content:
            a = Post(parent = blog_key(), title = title, content = content)
            a.put()
            self.redirect('/blog/%s' % str(a.key().id()))
        else:
            error = "we need both a title and some content!"
            self.render("submit.html", title=title, content=content, error=error)

class ViewPostHandler(Handler):
    def get(self, id):
        key = db.Key.from_path('Post', int(id), parent=blog_key())
        post = db.get(key)

        if not post:
            self.error(404)
            return

        self.render("permalink.html", post = post)

        #t = jinja_env.get_template("main_page.html")
        #if id == None:
        #    self.response.write("There are no blog entries with that ID!")
        #else:
        #    Post.get_by_id(int(id), parent=None)
        #    title = Post.title
        #    content = Post.content
        #    self.render(t, title=title, content=content)

        #else:
            #self.response.write("Sorry, there is no post with that ID")

app = webapp2.WSGIApplication([
    ('/blog/?', MainPage),
    ('/blog/newpost', New_Post),
    webapp2.Route('/blog/<id:\d+>', ViewPostHandler),
], debug = True)
