import webapp2
import os
import jinja2
import cgi
import re
import random
import string
import hashlib #various hashing algorithms
import hmac #hash-based message authentication code - for generating secret keys

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
								autoescape = True)
# use autoescape to opt into escaping variables. Saves you from security holes if you don't filter
# variables in your templates with '| safe' or '| escape'
#


#####
##### Password Validation
#####

#regular expression constants
USER_RE = re.compile("^[a-zA-Z0-9_-]{3,20}$")
PASSWORD_RE = re.compile("^.{3,20}$")
EMAIL_RE = re.compile("^[\S]+@[\S]+\.[\S]+$")
COOKIE_RE = re.compile(r'.+=;\s*Path=/')


def valid_name(text):
	return USER_RE.match(text)

def valid_password(passw):
	return PASSWORD_RE.match(passw)

def valid_verify(passw, verify):
	if (passw and verify):
		if (verify == passw):
			return True
		else:
			return False

def valid_email(email):
	if email == "":
		return True
	else:
		return EMAIL_RE.match(email)

def escape_html(s):
	return cgi.escape(s, quote = True)

class Handler(webapp2.RequestHandler):

	# create a shorthand for writing responses
	# *a indicates a tuple
	# **kw indicates a dictionary
	#  - when used in a function definition, it takes all the params passed and puts them into a tuple/dict
	#  - when used in a function call, it breaks those data structures apart.
	def write(self, *a, **kw):
		self.response.out.write(*a, **kw)

	# **params is the python syntax for extra parameters
	# 't.render' is a jinja function
	def render_str(self, template, **params):
		t = jinja_env.get_template(template)
		return t.render(params)

	def render(self, template, **kw):
		self.write(self.render_str(template,**kw))

class SignupHandler(Handler):
	def render_form(self, name_error="", username="", pass_error="", verify_error="", email_error="", email=""):
		self.render("signup.html",
			name_error=name_error,
			username=username,
			pass_error=pass_error,
			verify_error=verify_error,
			email_error=email_error,
			email=email)

	def get(self):
		self.render_form()

	def post(self):
		#get data from the forms
		user_username = self.request.get('username')
		user_password = self.request.get('password')
		user_verify = self.request.get('verify')
		user_email = self.request.get('email')

		#test the data and get data (true) or None
		username = valid_name(user_username)
		password = valid_password(user_password)
		verify = valid_verify(user_password, user_verify)
		email = valid_email(user_email)

		#if test gives us None, assing an error string. If test gives us good data, assign an empty string
		user_cookie_str = self.request.cookies.get('name')
		name_error = ""

		if not username:
			name_error = "That's not a valid username."
		if user_cookie_str:
			# print "username: " + username
			# print "get user: " + get_user(user_cookie_str)
			if user_username == get_user(user_cookie_str):
				name_error = "You've already signed up"

		# name_error = "That's not a valid username." if not username else ""
		pass_error = "That's not a valid password." if not password else ""
		verify_error = "Passwords do not match." if not verify else ""
		email_error = "That's not a valid email address." if not email else ""

		#if there are any errors, write them
		if (name_error or pass_error or verify_error or email_error):
			self.render_form(
				name_error, user_username,
				pass_error,
				verify_error,
				email_error, user_email
				)
		#else, redirect to a welcome screen along with the regex sanitized username
		else:
			#encode cookie
			self.response.headers['Content-Type'] = 'text/plain'

			user_id = str(make_pw_hash(user_username, user_password))

			# self.response.headers.add_header('Set-Cookie', 'visits=%s' % new_cookie_val)
			self.response.headers.add_header('Set-Cookie', 'name=%s; Path=/' % user_id)
			self.redirect('/welcome')

class LoginHandler(Handler):
	def render_form(self, invalid_login=""):
		self.render("login.html", invalid_login=invalid_login)

	def get(self):
		self.render_form()

	def post(self):
		#get data from the forms
		user_username = self.request.get('username')
		user_password = self.request.get('password')

		#if test gives us None, assing an error string. If test gives us good data, assign an empty string
		user_cookie_str = self.request.cookies.get('name')

		invalid_login = ""
		if user_cookie_str:
			if not valid_pw(user_username, user_password, user_cookie_str):
				invalid_login = "Invalid Login"

		if (invalid_login):
		#if there are any errors, write them
			self.render_form(invalid_login)
		#else, redirect to a welcome screen along with the regex sanitized username
		else:
			self.redirect('/welcome')

class LogoutHandler(Handler):
	def get(self):
		user_cookie_str = self.request.cookies.get('name')
		if user_cookie_str:
			self.response.delete_cookie('name')
			print valid_cookie(user_cookie_str)
			self.redirect('/signup')

class WelcomeHandler(Handler):
	def get(self):
		#decode cookie
		user_cookie_str = self.request.cookies.get('name')
		if user_cookie_str:
			user = get_user(user_cookie_str)
			if user:
				msg = "Welcome, %s!" % user
			else:
				msg = "Whoops, something went wrong"
			self.render("welcome.html", msg=msg)
		else:
			self.redirect('/signup')

#####
##### Hashing Functions
#####

SECRET = 'mysecret'

def make_salt():
	return ''.join(random.choice(string.letters) for x in xrange(5))

def hash_str(s):
	return hmac.new(SECRET, s).hexdigest()

# def make_secure_val(s):
# 	return str(s) + '|' + hash_str(s)

# def check_secure_val(h):
# 	val = h.split('|')[0]
# 	s = h.split('|')[2]
# 	print "val " + val
# 	print "s " + s
# 	if s == make_secure_val(val):
# 		return val

def make_pw_hash(name, pw, salt = None):
	if not salt:
		salt = make_salt()
	h = hashlib.sha256(name + pw + salt).hexdigest()
	return '%s|%s|%s' % (name, salt, h)

def valid_pw(name, pw, h):
	# get the salt from the hash
	salt = h.split('|')[1]
	# combine the salt with the submitted name and pw
	# if the existing cookie hash matches the hash derived from the new User/Password, then
	# return the hash value
	if h == make_pw_hash(name, pw, salt):
		return h

def get_user(cookie):
	return cookie.split('|')[0]

def valid_cookie(cookie):
	return cookie and COOKIE_RE.match(cookie)


#####
##### Blog Pages
#####

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
			self.redirect('/' + post_id)
		else:
			error = "please enter some values"
			self.render_form(subject, content, error=error)

# inherits from Handler
class BlogPage(Handler):
	def render_front(self):
		entries = db.GqlQuery("SELECT * FROM Entry ORDER BY created DESC")
		# keyentry = entries.get_by_id(5205088045891584)
		# entry = Entry.get(_by_id(post_id))
		self.render("recentposts.html", entries=entries)

	def get(self):
		# pass them into the template
		self.render_front()

class Single(Handler):
	def render_single(self, post_id):
		post_id = int(post_id)
		# entries = db.GqlQuery("SELECT * FROM Entry ORDER BY created DESC")
		entry = Entry.get_by_id(post_id)
		self.render("single.html", entry=entry)

	def get(self, post_id):
		self.render_single(post_id)

# this is the router
app = webapp2.WSGIApplication([
	('/', BlogPage),
	('/signup', SignupHandler),
	('/login', LoginHandler),
	('/logout', LogoutHandler),
	('/welcome', WelcomeHandler),
	('/newpost', NewPostForm),
	('/(\d+)', Single) #lr somehow pass the id of the blog post here

], debug=True)
