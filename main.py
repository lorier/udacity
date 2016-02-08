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

import cgi

form="""
<form method="post">
	Enter some ROT13 test:
	<br>
	<textarea type="textarea" style="width: 500px" rows="20" name="text" value="%(text)s">%(text)s</textarea>
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


chars = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']

def escape_html(s):
    return cgi.escape(s, quote = True)

class MainHandler(webapp2.RequestHandler):
	def write_form(self, text=""):
		self.response.out.write(form % {"text": text})

	def get(self):
		self.write_form()

	def post(self):
		user_text = self.request.get('text')

		text = valid_text(user_text)

		self.write_form(text)


app = webapp2.WSGIApplication([
	('/', MainHandler)
], debug=True)
