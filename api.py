import tweepy
import webbrowser
import keys
from datetime import datetime

tokens = keys.tokens

class TwitterAPI:

	def __init__(self, access_token="", access_token_secret=""):
		
		auth = tweepy.OAuthHandler(*tokens['APP'])
		if access_token == "":
			# get access token from the user and redirect to auth URL
			auth_url = auth.get_authorization_url()
			print 'Authorization URL: %s' % auth_url
			webbrowser.open(auth_url)
			 
			# ask user to verify the PIN generated in broswer
			verifier = raw_input('PIN: ').strip()
			token = auth.get_access_token(verifier)
			print 'ACCESS_KEY = "%s"' % token[0]
			print 'ACCESS_SECRET = "%s"' % token[1]
			access_token = token[0]
			access_token_secret = token[1]
		
		# authenticate and retrieve user name
		auth.set_access_token(access_token, access_token_secret)
		self.api = tweepy.API(auth)
		self.user = self.api.me().screen_name
		self.id = self.api.me().id
		file = open("cats.txt", "a+")
		file.write('%s|KEY = %s SECRET = %s\n' % (self.user, access_token, access_token_secret))
		file.close()
		print 'Ready to post to %s' % self.user
		
	def tweet(self, message, id=None):
		try:
			self.api.update_status(status=message[:140], in_reply_to_status_id=id)
			now = datetime.now()
			print '%s/%s/%s %s:%s:%s' % (now.month, now.day, now.year, now.hour, now.minute, now.second)
			print "Tweeting: %s" % message.encode('ascii', 'backslashreplace')
		except tweepy.TweepError:
			print "Couldn't send tweet"
		
	def getTweets(self, name=None, since=1):
		if name: name = name.replace("@", "")
		try:
			print "Searching for tweets..."
			return self.api.user_timeline(screen_name=name, since_id=since)
		except tweepy.TweepError:
			print "Couldn't retrieve tweets"
			return []
		
	def favorite(self, twt):
		try:
			twt.favorite()
		except tweepy.TweepError:
			print "Tweet already favorited!"
		
	def search(self, s, since=1):
		try:
			return self.api.search(q=s, since_id=since)
		except tweepy.TweepError:
			print "Couldn't search for %s" % s
			return []
		
	def rate_limit(self):
		return self.api.rate_limit_status()
		
	def getTrends(self, id=1):
		return self.api.trends_place(id)
		
	def trends(self):
		return self.api.trends_available()
		
	def follow(self, name):
		name = name.replace("@", "")
		try:
			if not self.isFollowing(name):
				self.api.create_friendship(name)
				print "Now following %s" % name
			else:
				print "You already follow %s" % name
		except	tweepy.TweepError:
			print "Error"
			
	def isFollowing(self, userA, userB=None):
		if userB: userB = userB.replace("@", "")
		userA = userA.replace("@", "")
		return self.api.show_friendship(source_screen_name=userB, target_screen_name=userA)[0].following
		
	def getUser(self, name):
		name = name.replace("@", "")
		try:
			return self.api.get_user(screen_name=name)
		except	tweepy.TweepError:
			print "%s is not a user" % name
			return None
			
	def getStatus(self, id):
		try:
			return self.api.get_status(id)
		except	tweepy.TweepError:
			print "Error finding status %s" % id
			return None
			
	def isRetweet(self, twt):
		return 'retweeted_status' in twt._json
			
	def getFollowers(self):
		try:
			return self.api.followers()
		except	tweepy.TweepError:
			print "Couldn't get followers"
			return []
	
	def getFollowing(self):
		try:
			return self.api.friends()
		except	tweepy.TweepError:
			print "Couldn't get following"
			return []
			
	def getDMs(self, since=1):
		try:
			print "Searching for DMs..."
			return self.api.direct_messages(since)
		except	tweepy.TweepError as e:
			print "Couldn't get DMs"
			print e
			return []
			
	def sendDM(self, name, text):
		name = name.replace("@", "")
		try:
			self.api.send_direct_message(screen_name=name, text=text[:140])
			print "DM sent to %s with text: %s" % (name, text.encode('ascii', 'backslashreplace'))
		except tweepy.TweepError as e:
			print "Couldn't slide in %s's DMs" % name
			print e
			
	def getMentions(self, since=1):
		try:
			print "Searching for mentions..."
			return self.api.mentions_timeline(since_id=since)
		except	tweepy.TweepError:
			print "Couldn't get mentions"
			return []
	
	def getTimeline(self, since=1):
		try:
			return self.api.home_timeline(since_id=since)
		except	tweepy.TweepError:
			print "Couldn't get home timeline for %s" % self.user
			return []

	def userMentions(self, twt):
		s = " "
		for i in twt.entities['user_mentions']:
			if i['id'] != self.id:
				s += "@%s " % i['screen_name']
		return s