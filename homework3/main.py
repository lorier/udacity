import webapp2
import os
import jinja2
import cgi
import re

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
								autoescape = True)
# use autoescape to opt into escaping variables. Saves you from security holes if you don't filter
# variables in your templates with '| safe' or '| escape'

# superclass
class Handler(webapp2.RequestHandler):

	# create a shorthand for writing responses
	def write(self, *a, **kw):
		self.response.out.write(*a, **kw)

	# **params is the python syntax for extra parameters
	# 't.render' is a jinja function
	def render_str(self, template, **params):
		t = jinja_env.get_template(template)
		return t.render(params)

	def render(self, template, **kw):
		self.write(self.render_str(template,**kw))

class Entry(db.Model):
	subject = db.StringProperty(required = True)
	content = db.TextProperty(required = True)
	created = db.DateTimeProperty(auto_now_add = True)

class NewPostForm(Handler):
	def render_form(self, subject="", content="", error=""):
		self.render("newpost.html", subject=subject, content=content, error=error)

	def get(self):
		# pass them into the template
		self.render_form()

	def post(self):
		subject = self.request.get("subject")
		content = self.request.get("content")

		if(subject and content):
			e = Entry(subject = subject, content = content)
			e.put()
			post_id = str(e.key().id())

			#so we don't get the annoying reload message if we reload the page
			self.redirect('/blog/' + post_id)
		else:
			error = "please enter some values"
			self.render_form(subject, content, error=error)

# inherits from Handler
class BlogPage(Handler):
	def render_front(self, subject="", content="", created=""):
		entries = db.GqlQuery("SELECT * FROM Entry ORDER BY created DESC")
		# keyentry = entries.get_by_id(5205088045891584)
		self.render("recentposts.html", subject=subject, content=content, created=created, entries=entries)

	def get(self):
		# pass them into the template
		self.render_front()

class Single(Handler):
	def render_single(self, post_id="", subject="", content="", created=""):
		post_id = int(post_id)
		# entries = db.GqlQuery("SELECT * FROM Entry ORDER BY created DESC")
		print "entry from single"
		entry = Entry.get_by_id(post_id)
		self.render("single.html", post_id=post_id, subject=subject, content=content, created=created, entry=entry)

	def get(self, post_id):
		self.render_single(post_id)

# this is the router
app = webapp2.WSGIApplication([
	('/blog/', BlogPage),
	('/blog/newpost', NewPostForm),
	('/blog/(\d+)', Single) #lr somehow pass the id of the blog post here

], debug=True)
