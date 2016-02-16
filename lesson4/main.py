import webapp2
import os
import jinja2
import cgi
import re
import hashlib #various hashing algorithms
import hmac #hash-based message authentication code - for generating secret keys


from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
								autoescape = True)
# use autoescape to opt into escaping variables. Saves you from security holes if you don't filter
# variables in your templates with '| safe' or '| escape'
SECRET = 'mysecret'

# superclass
def hash_str(s):
	return hmac.new(SECRET, s).hexdigest()

def make_secure_val(s):
	return str(s) + '|' + hash_str(s)

def check_secure_val(h):
	val = h.split('|')[0]
	if h == make_secure_val(val):
		return val


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

class Main(Handler):
	# def render_front(self, subject="", content="", created=""):
	# 	self.render("recentposts.html", subject=subject, content=content, created=created, entries=entries)

	def get(self):
		self.response.headers['Content-Type'] = 'text/plain'
		visits = 0
		visit_cookie_str = self.request.cookies.get('visits')
		if visit_cookie_str:
			cookie_val = check_secure_val(visit_cookie_str)
			if cookie_val:
				visits = int(cookie_val)

		visits += 1

		new_cookie_val = make_secure_val(str(visits))

		self.response.headers.add_header('Set-Cookie', 'visits=%s' % new_cookie_val)
		self.write("you've been here %s times!" % visits)

# class NewPostForm(Handler):
# 	def render_form(self, subject="", content="", error=""):
# 		self.render("newpost.html", subject=subject, content=content, error=error)

# 	def get(self):
# 		# pass them into the template
# 		self.render_form()

# 	def post(self):
# 		subject = self.request.get("subject")
# 		content = self.request.get("content")

# 		if(subject and content):
# 			e = Entry(subject = subject, content = content)
# 			e.put()
# 			post_id = str(e.key().id())

# 			#so we don't get the annoying reload message if we reload the page
# 			self.redirect('/blog/' + post_id)
# 		else:
# 			error = "please enter some values"
# 			self.render_form(subject, content, error=error)

# # inherits from Handler
# class BlogPage(Handler):
# 	def render_front(self, subject="", content="", created=""):
# 		entries = db.GqlQuery("SELECT * FROM Entry ORDER BY created DESC")
# 		# keyentry = entries.get_by_id(5205088045891584)
# 		self.render("recentposts.html", subject=subject, content=content, created=created, entries=entries)

# 	def get(self):
# 		# pass them into the template
# 		self.render_front()

# class Single(Handler):
# 	def render_single(self, post_id="", subject="", content="", created=""):
# 		post_id = int(post_id)
# 		# entries = db.GqlQuery("SELECT * FROM Entry ORDER BY created DESC")
# 		print "entry from single"
# 		entry = Entry.get_by_id(post_id)
# 		self.render("single.html", post_id=post_id, subject=subject, content=content, created=created, entry=entry)

# 	def get(self, post_id):
# 		self.render_single(post_id)

# this is the router
app = webapp2.WSGIApplication([
	('/', Main),
	# ('/blog/newpost', NewPostForm),
	# ('/blog/(\d+)', Single) #lr somehow pass the id of the blog post here

], debug=True)
