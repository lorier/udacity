import webapp2
import os
import jinja2
import urllib2
from xml.dom import minidom
import time

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
								autoescape = True)
# use autoescape to opt into escaping variables. Saves you from security holes if you don't filter
# variables in your templates with '| safe' or '| escape'

IP_URL = "http://ip-api.com/xml/"
GMAPS_URL = "http://maps.googleapis.com/maps/api/staticmap?size=380x263&"

TEMP_IP = "73.225.76.73"
def gmaps_img(points):
	#The method join() returns a string in which the string elements
	#of sequence have been joined by str separator.
	#str.join(sequence)
	markers = '&'.join('markers=%s,%s' % (p.lat, p.lon) for p in points)
	return GMAPS_URL + markers

def get_coords():
	ip = TEMP_IP

	url = IP_URL + ip
	content = None
	try:
		content = urllib2.urlopen(url).read()
	except URLError:
		return
	if content:
		d = minidom.parseString(content)
		print d
		status = d.getElementsByTagName('status')[0].childNodes[0].nodeValue
		print content
		if status == 'success':
			lonNode = d.getElementsByTagName('lon')[0]
			latNode = d.getElementsByTagName('lat')[0]
			if lonNode and latNode and lonNode.childNodes[0].nodeValue and latNode.childNodes[0].nodeValue:
				lon = lonNode.childNodes[0].nodeValue
				lat = latNode.childNodes[0].nodeValue
				return db.GeoPt(lat, lon)

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
	coords = db.GeoPtProperty()

def complex_computation(a, b):
    time.sleep(.5)
    return a + b

# inherits from Handler
cache = {}
def cached_computation(a, b):
	print 'cached comp run'
	if cache:
		print 'cache exists'
		if cache['one'] == a and cache['two'] == b:
			return cache.one + cache.two
		else:
			cache['one'] = a
			cache['two'] = b
			print 'cache does not exist'
			return complex_computation(a,b)
			#print cache

	#start_time = time.time()
	#print "the first computation took %f seconds" % (time.time() - start_time)
	#
class MainPage(Handler):
	print cached_computation(5, 3)
	def render_front(self, title="", art="", error=""):
		arts = db.GqlQuery("SELECT * FROM Art ORDER BY created DESC")

		#prevent the running of multiple queries on the DB.
		#The arts query results is a cursor, this converts it to a list.
		arts = list(arts)

		# find which art has coords - this long way of getting the coords didn't work - caused an error
		# points = []
		# for a in arts:
		# 	if arts.coords:
		# 		points.append(a.coords)


		#this is a shorthad for the loop above:
		points = filter(None, (a.coords for a in arts))

		#if we have coords, make an image url
		img_map = None
		if points:
			img_map = gmaps_img(points)
		#display image url
		#
		self.render("front.html", title=title, art=art, error=error, arts=arts, img_map=img_map)

	def get(self):

		# self.write(repr(get_coords()))
		self.write(get_coords())
		# self.write(repr(get_coords(self.request.remote_addr)))

		# pass them into the template
		self.render_front()

	def post(self):
		title = self.request.get("title")
		art = self.request.get("art")

		if(title and art):
			a = Art(title = title, art = art)
			coords = get_coords()
			self.write(coords)
			if coords:
				a.coords = coords
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
