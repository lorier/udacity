import webapp2
import os
import jinja2

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

class Art(db.Model):
	title = db.StringProperty(required = True)
	art = db.TextProperty(required = True)
	created = db.DateTimeProperty(auto_now_add = True)


# inherits from Handler
class MainPage(Handler):
	def render_front(self, title="", art="", error=""):
		arts = db.GqlQuery("SELECT * FROM Art ORDER BY created DESC")

		self.render("front.html", title=title, art=art, error=error, arts=arts)

	def get(self):
		# pass them into the template
		self.render_front()

	def post(self):
		title = self.request.get("title")
		art = self.request.get("art")

		if(title and art):
			a = Art(title = title, art = art)
			a.put()

			#so we don't get the annoying reload message if we reload the page
			self.redirect('/')
		else:
			error = "please enter some values"
			self.render_front(title, art, error=error)

# this is the router
app = webapp2.WSGIApplication([
	('/', MainPage)
], debug=True)
