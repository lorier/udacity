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

# use for escaping html chars
import cgi

form="""
<form style="line-height: 30px" method="post">
	<strong>Sign up:</strong>
	<br>
	<label>Name: <input type="text" name="username" value="%(username)s"></label><br>
	<label>Password: <input type="password" name="password" value="%(password)s"></label><br>
	<label>Verify Password: <input type="password" name="verify" value="%(verify)s"></label><br>
	<label>Email: <input type="text" name="email" value="%(email)s"></label>
	<br>
	<input type="submit">
</form>
"""
def valid_text(text):
	string = ""
	if text:
		for char in text:
			isCap = char.isupper()
			if char.isalpha():
				char = char.lower()
				index = chars.index(char)
				newIndex = (index+13) % len(chars)
				char = chars[newIndex]
				if isCap:
					char = char.capitalize()
				string = string + char
			elif char.isdigit() or char == " " or char == '"' or char == "'":
				string = string + char
			else:
				string = string + escape_html(char)
	return string

def escape_html(s):
    return cgi.escape(s, quote = True)

class MainHandler(webapp2.RequestHandler):
	def write_form(self, username="", password="", verify="", email=""):
		self.response.out.write(form % {"username": username, "password": password, "verify": verify, "email": email})

	def get(self):
		self.write_form()

	def post(self):
		user_username = self.request.get('username')
		user_password = self.request.get('password')
		user_verify = self.request.get('verify')
		user_email = self.request.get('email')

		username = valid_text(user_username)
		password = valid_text(user_password)
		verify = valid_text(user_verify)
		email = valid_text(user_email)

		self.write_form(text)

		if not (username and password and verify):
			self.write_form('sorry invalid stuff', user_username, user_password)
		else:
			self.redirect('/thanks')

class ThanksHandler(webapp2.RequestHandler):
	def get(self, username=""):
		name = self.request.get("username")
		self.response.out.write("Welcome, " + name)

# this is the router
app = webapp2.WSGIApplication([
	('/', MainHandler),
	('/thanks', ThanksHandler)
], debug=True)
