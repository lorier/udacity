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

#import regular expressions
import re

#regular expression constants
USER_RE = re.compile("^[a-zA-Z0-9_-]{3,20}$")
PASSWORD_RE = re.compile("^.{3,20}$")
EMAIL_RE = re.compile("^[\S]+@[\S]+\.[\S]+$")

form="""
<form style="line-height: 30px" method="post">
	<strong>Sign up:</strong>
	<br>
	<label>Username: <input type="text" name="username" value="%(username)s"> <span style="color: red">%(name_error)s</span></label><br>
	<label>Password: <input type="password" name="password">  <span style="color: red">%(pass_error)s</span></label><br> 
	<label>Verify Password: <input type="password" name="verify">  <span style="color: red">%(verify_error)s</span></label><br> 
	<label>Email: <input type="text" name="email" value="%(email)s"> <span style="color: red">%(email_error)s</span></label> 
	<br>
	<input type="submit">
</form>
"""
def valid_name(text):
	if text:
		return USER_RE.match(text)

def valid_password(text):
	if text:
		return PASSWORD_RE.match(text)

def valid_verify(passorverify, passw, verify):
	if passorverify == "passw":
		isValid = PASSWORD_RE.match(passw)
		if not (isValid):
			return "Please enter a password."
		elif passw != verify:
			return "Passwords do not match. Enter matching password below"
		else:
			return ""

	elif passorverify == "verify":
		isValid = PASSWORD_RE.match(verify)
		if not (isValid):
			return "Please enter a matching password."
		elif passw != verify:
			return "Passwords do not match. Enter a valid password."
		else:
			return ""


def valid_email(email):
	if email:
		return EMAIL_RE.match(email)
		print email

def escape_html(s):
    return cgi.escape(s, quote = True)

class MainHandler(webapp2.RequestHandler):
	def write_form(self, name_error="", username="", pass_error="", verify_error="", email_error="", email=""):
		self.response.out.write(form % {
			"name_error": name_error,
			"username": username, 
			"pass_error": pass_error,
			"verify_error": verify_error,
			"email_error": email_error,
			"email": email})

	def get(self):
		self.write_form()

	def post(self):
		user_username = self.request.get('username')
		user_password = self.request.get('password')
		user_verify = self.request.get('verify')
		user_email = self.request.get('email')

		username = valid_name(user_username)
		password = valid_verify("passw", user_password, user_verify)
		verify = valid_verify("verify", user_password, user_verify)
		email = valid_email(user_email)
		print(email)

		user_error = "That's not a valid username." if not username else ""
		pass_error = password
		verify_error = verify
		email_error = "That's not a valid email address." if not email else ""


		if (not username) or (not user_password) or (not user_verify) or (not user_email):
			self.write_form(
				user_error, user_username,
				pass_error, 
				verify_error,
				email_error, user_email
				)
		else:
			self.redirect('/thanks?q=' +  username.group(0))

class ThanksHandler(webapp2.RequestHandler):
	def get(self):
		q = self.request.get("q")
		self.response.out.write("Welcome, " + q + "!")

# this is the router
app = webapp2.WSGIApplication([
	('/', MainHandler),
	('/thanks', ThanksHandler)
], debug=True)
