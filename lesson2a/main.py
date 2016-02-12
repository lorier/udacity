#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import webapp2
import os

import jinja2

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

# inherits from Handler 
class MainPage(Handler):

	def get(self):
		# get the items from the url
		items = self.request.get_all("food")

		# pass them into the template
		self.render("shopping_list.html", items = items)

class FizzBuzzHandler(Handler):
	
	def get(self):
		n = self.request.get('n', 0)
		n=n and int(n)
		self.render('fizzbuzz.html', n = n)
			
# this is the router
app = webapp2.WSGIApplication([
	('/', MainPage),
	('/fizzbuzz', FizzBuzzHandler)
], debug=True)
