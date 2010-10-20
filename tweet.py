#!/usr/bin/env python
"""
tweet.py - Phenny Twitter Module
created for TU Hamburg-Harburg Unix-AG
#unix-ag on freenode

"""

import tweepy, pickle, os

class tweet_conf:
	def __init__(self):
		self.ACCESS_KEY = ''
		self.ACCESS_SECRET = ''
		self.WHO = 0
		self.UPDATE_PREFIX = '[IRC]'
		#to use this module, please create a new twitter app and fill in the values below
		self.CONSUMER_KEY = ''
		self.CONSUMER_SECRET = ''

def twitpin(phenny, input):
	"""Give Oauth-pin to phenny - only for admins in privmsg"""
	if input.sender.startswith('#'): return #only in privmsg
	if not input.admin: return #only admins can do that
	pin = input.group(1).strip()

	phenny.tweet_auth.get_access_token(pin)
	phenny.tweet_config.ACCESS_KEY = phenny.tweet_auth.access_token.key
	if len(phenny.tweet_config.ACCESS_KEY) > 1:
		phenny.msg(input.nick, "got access token!")
	phenny.tweet_config.ACCESS_SECRET = phenny.tweet_auth.access_token.secret
	#save config now
	f = open(phenny.tweet_filename,'w')
	pickle.dump(phenny.tweet_config, f)
	f.close()
twitpin.rule = r'\.pin (.+)'
twitpin.priority = 'high'


def killauth(phenny, input):
	"""remove auth credentials"""
	if input.sender.startswith('#'): return #only in privmsg
	if not input.admin: return #only admins can do that
	
	phenny.tweet_config.ACCESS_KEY = ""
	phenny.tweet_config.ACCESS_SECRET = ""
	#save config now
	f = open(phenny.tweet_filename,'w')
	pickle.dump(phenny.tweet_config, f)
	f.close()
	phenny.say("ok, auth removed")
killauth.rule = r'\.killauth'
killauth.priority = 'high'

def whoauth(phenny, input):
	"""set who may tweet"""
	if not input.admin: return #only admins can do that

	mode = input.group(1).strip()
	if mode == "all":
		phenny.tweet_config.WHO = 1
		phenny.say("Everyone may tweet now!")
	else:
		phenny.tweet_config.WHO = 0
		phenny.say("Only admins my tweet now!")
	#save config now
	f = open(phenny.tweet_filename,'w')
	pickle.dump(phenny.tweet_config, f)
	f.close()
whoauth.rule = r'\.who (.+)'
whoauth.priority = 'low'



def twitauthurl(phenny, input):
	"""Get OAuth Url"""
	if input.sender.startswith('#'): return #only in privmsg
	if not input.admin: return #only admins can do that

	auth_url = phenny.tweet_auth.get_authorization_url()
	phenny.say("Please auth me at " + auth_url+ " . (pin via .pin) debug: AK is "+ phenny.tweet_config.ACCESS_KEY)
twitauthurl.command = ['authurl']
twitauthurl.rule = r'\.authurl'
twitauthurl.priority = 'high'

def tweet(phenny, input):
	"""Tweet a tweet on Twitter"""
	#print "enter tweet()..."
	#only admin or WHO = 1
	if phenny.tweet_config.WHO == 0 and not input.admin:
		phenny.say("sorry, admins only.")
	
	text = input.group(1)

	if len(text) > (140-len(input.nick) - len(phenny.tweet_config.UPDATE_PREFIX) -3):
		phenny.say(input.nick + ", you're much too chatty today...")
		return

	if len(phenny.tweet_config.ACCESS_KEY) < 1:
		phenny.say("Sorry, can't do that yet. Tell my master to auth me first.")

	else: 
		phenny.tweet_auth.set_access_token(phenny.tweet_config.ACCESS_KEY, phenny.tweet_config.ACCESS_SECRET)
		api = tweepy.API(phenny.tweet_auth)
		status = api.update_status(phenny.tweet_config.UPDATE_PREFIX + "<" +input.nick + "> "+ text)
		#print "updated status..."
	
tweet.rule = r'\.tweet (.+)'
tweet.priority = 'medium'

def setup(self):
	fn = "tweet.conf"
	self.tweet_filename = os.path.join(os.path.expanduser('~/.phenny/'), fn)
	if not os.path.exists(self.tweet_filename):
		newconf = tweet_conf()
		try: 
			f = open(self.tweet_filename, 'wb')
			pickle.dump(newconf, f)
		except OSError: pass
		else:
			f.close()
	f = open(self.tweet_filename, 'rb')
	try: 	
		self.tweet_config = pickle.load(f)
	except pickle.UnpickleError:
		os.remove(self.tweet_filename)
		#print "Unpickle error! Unlinking config file!"
		phenny.say("An error occured while reading the config file - please check")

	self.tweet_auth = tweepy.OAuthHandler(self.tweet_config.CONSUMER_KEY, self.tweet_config.CONSUMER_SECRET)
	#print "ok, tweet setup done"


if __name__ == '__main__': 
   print __doc__.strip()
