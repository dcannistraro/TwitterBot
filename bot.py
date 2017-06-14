import time
import random
import threading
import re
import keys
from api import TwitterAPI

adjectives = keys.adjectives
verbs = keys.verbs
connect = keys.connect
rstop = keys.stop
exclaim = keys.exclaim
links = keys.links
tokens = keys.tokens
sentence = ""

def randWord(list, n=1):
	s = ""
	x = random.sample(list, n)
	for i in range(0, n):
		s += x[i]
		if i != n-1:
			s += " "
	return s

def getMessage(x):
	if x == 1:
		new = random.sample(adjectives, 3)
		new2 = random.sample(connect, 2)
		return randWord(exclaim)+", this tweet is "+new2[0]+" "+new[0]+". You are "+new2[1]+" "+new[1]+" and "+new[2]+"."
	elif x == 2:
		return randWord(exclaim)+', your use of the word "'+randWord(sentence.split())+'" is '+randWord(connect, 2)+' '+randWord(adjectives)+"."
	elif x == 3:
		return "This tweet was "+randWord(connect, 2)+" "+randWord(adjectives)+". It made me "+randWord(verbs)+"."
	elif x == 4:
		return "If I were "+randWord(adjectives)+", this tweet would be 10 times more "+randWord(adjectives)+"."
	elif x == 5:
		return "This tweet made me "+randWord(verbs)+" and "+randWord(verbs)+"."
	elif x == 6:
		return randWord(links)

class TwitterBot:
	
	#list of followers
	followers = []
	
	# dictionary of bot instances
	instances = {}
	
	# admin users, for admin dms
	admins = ["d_rack7", "matthamel2"]
	
	# list of people being replied to (ignored in mentions)
	reps = []
	botlist = ["followbot", "replybot", "mentionbot", "dmbot", "stopbot"]
	matches = keys.matches
	replys = keys.stop
	rmatches = keys.rmatches

	# initialize TwitterBot
	def __init__(self, at="", ats=""):
		self.access_token = at
		self.access_token_secret = ats
		self.twitter = TwitterAPI(self.access_token, self.access_token_secret)
		self.user = self.twitter.api.me()
		self.reps.append(self.user.id)
		
	# start instance of bot
	def start(self, key):
		print "Attempting to start %s..." % key
		newInstance = None
		if key not in self.instances or not self.instances[key]:
			key = key.split('-')
			if key[0] in self.botlist:
				newInstance = threading.Thread(target=getattr(self, key[0]), args=tuple(key[1:]))
				newInstance.daemon = True
				newInstance.start()
			else:
				print key[0], "is invalid"
		else:
			print "Can't start %s: Already running" % key
		time.sleep(1)
		return newInstance
		
	# stop a currently running instance
	def stop(self, key):
		if key in self.instances and self.instances[key]:
			self.instances[key] = False
			print key, "queued to stop"
			return True
		else:
			print "Can't stop %s: Doesn't exist or already stopped" % key
			return False
	
	# follow user
	def follow(self, user):
		if not user.following and not user.follow_request_sent:
			user.follow()
			print "Now following %s" % user.screen_name
	
	# get all running instances as list
	def currentInstances(self):
		l = []
		for k in self.instances:
			if self.instances[k]: l.append(k)
		return l
	
	# delete instance key from the dict
	def endInstance(self, instance):
		print "Stopping %s on %s" % (instance, self.user.screen_name)
		del self.instances[instance]

	# add a user to the admin list
	def makeadmin(self, newAdmin):
		newAdmin = newAdmin.lower()
		if newAdmin not in self.admins:
			self.admins.append(newAdmin)
			print newAdmin, "is now an admin of %s" % self.user.screen_name
		else:
			print newAdmin, "is is already an admin of %s" % self.user.screen_name
	
	# follow all people that follow you
	def followbot(self):
		self.instances['followbot'] = True
		print "Running FollowBot on %s" % self.user.screen_name
		flwrs = self.twitter.getFollowers()
		for i in flwrs:
			self.followers.append(i.id)
			if not i.following and not i.follow_request_sent:
				i.follow()
				print "Now following %s" % i.screen_name
		time.sleep(60*30)
		while self.instances['followbot']:
			flwrs = self.twitter.getFollowers()
			for i in flwrs:
				if i.following or i.follow_request_sent: break
				self.followers.append(i.id)
				self.follow(i)
			time.sleep(60*30)
		self.endInstance('followbot')

	# reply to dms
	def dmbot(self):
		file = open("keywords.txt", "a+")
		keywords = ["say", "tweet", "follow", "key", "rkey", "reply", "start", "stop"]
		self.instances['dmbot'] = True
		print "Running DMBot on %s" % self.user.screen_name
		dms = self.twitter.getDMs()
		if dms: lastDM = dms[0].id
		else: lastDM = 1
		time.sleep(60)
		while self.instances['dmbot']:
			dms = self.twitter.getDMs(lastDM)
			for i in range(len(dms)-1, -1, -1): #backwards iterator
				lastDM = dms[i].id
				target = dms[i].sender.screen_name
				sentence = dms[i].text
				s = sentence.replace("@", "").split()
				print "Found DM: %s" % sentence.encode('ascii', 'backslashreplace')
				if s[0].lower() in keywords and len(s) > 1:
					if random.randint(1,5) == 1:
						self.twitter.sendDM(target, "fuck off lahey: %s is loafing around" % self.user.screen_name)
					elif re.match("say", s[0], re.I):
						self.twitter.sendDM(target, sentence[4:])
					elif re.match("tweet", s[0], re.I):
						self.twitter.tweet(sentence[6:])
						self.twitter.sendDM(target, "Tweet sent!")
					elif re.match("follow", s[0], re.I):
						u = self.twitter.getUser(s[1])
						if u and not u.following and not u.follow_request_sent:
							u.follow()
							self.twitter.sendDM(target, "Followed user!")
						else:
							self.twitter.sendDM(target, "Couldn't follow user!")
					elif re.match("key", s[0], re.I) and target.lower() in self.admins and len(s) > 2:
						s[1] = r"\b%s" % s[1].lower()
						if s[1] not in self.matches:
							self.matches[s[1]] = [s[2:]]
						else:
							self.matches[s[1]].append(s[2:])
						file.write("kw: %s, phrase: %s\n" % (s[1].encode('ascii', 'backslashreplace'), " ".join(s[2:]).encode('ascii', 'backslashreplace')))
						self.twitter.sendDM(target, "New phrase added for keyword %s!" % s[1][2:])
					elif re.match("rkey", s[0], re.I) and target.lower() in self.admins and len(s) > 2:
						s[1] = r"\b%s" % s[1].lower()
						if s[1] not in self.rmatches:
							self.rmatches[s[1]] = [s[2:]]
						else:
							self.rmatches[s[1]].append(s[2:])
						file.write("rep kw: %s, phrase: %s\n" % (s[1].encode('ascii', 'backslashreplace'), " ".join(s[2:]).encode('ascii', 'backslashreplace')))
						self.twitter.sendDM(target, "New reply phrase added for keyword %s!" % s[1][2:])
					elif re.match("reply", s[0], re.I) and target.lower() in self.admins:
						if s[1:] not in self.replys:
							self.replys.append(s[1:])
							file.write("reply: %s\n" % " ".join(s[1:]).encode('ascii', 'backslashreplace'))
							self.twitter.sendDM(target, "New reply added: %s..." % " ".join(s[1:])[:20])
						else:
							self.twitter.sendDM(target, "Reply already in database")
					elif re.match("start", s[0], re.I) and target.lower() in self.admins:
						self.start(s[1].lower())
						if self.instances[s[1].lower()]:
							self.twitter.sendDM(target, "Started %s successfully!" % s[1])
						else:
							self.twitter.sendDM(target, "Couldn't start %s!" % s[1])
					elif re.match("stop", s[0], re.I) and target.lower() in self.admins:
						if self.stop(s[1].lower()):
							self.twitter.sendDM(target, "Stopped %s successfully!" % s[1])
						else:
							self.twitter.sendDM(target, "Instance doesn't exist")
					elif re.match("admin", s[0], re.I) and target.lower() in self.admins:
						self.makeadmin(s[1].replace("@", ""))
						self.twitter.sendDM(target, "%s is now an admin!" % s[1])
					else:
						self.twitter.sendDM(target, "You don't have permission to do that")
				else:
					for word in self.rmatches:
						if re.search(word, sentence, re.I):
							message = random.sample(self.rmatches[word], 1)[0]
							break
					else:
						message = "Sorry, I didn't understand that"
					self.twitter.sendDM(target, message)
			time.sleep(60)
		file.close()
		self.endInstance('dmbot')
	
	# auto reply to user tweets
	def replybot(self, target):
		u = self.twitter.getUser(target)
		if not u:
			print target, "doesn't exist!"
			return
		self.reps.append(u.id)
		key = "replybot-"+target
		self.instances[key] = True
		print "Running %s on %s" % (key, self.user.screen_name)
		twts = self.twitter.getTweets(target)
		lastid = twts[0].id
		time.sleep(30)
		while self.instances[key]:
			twts = self.twitter.getTweets(target, lastid)
			for i in range(len(twts)-1, -1, -1): #backwards iterator
				newTweet = twts[i]
				if not newTweet.favorited: self.twitter.favorite(newTweet)
				lastid = newTweet.id
				print "Tweet found! lastid updated to "+str(lastid)
				s = newTweet.text
				
				if 'retweeted_status' not in newTweet._json and (newTweet.in_reply_to_screen_name == None or newTweet.in_reply_to_screen_name == self.user.screen_name):
					message = "@"+target+self.twitter.userMentions(newTweet)
					
					if newTweet.in_reply_to_screen_name == self.user.screen_name:
						for word in self.rmatches:
							if re.search(word, s, re.I):
								message += random.sample(self.rmatches[word], 1)[0]
								break
						else:
							if random.randint(1,3) == 2: message += "Stop replying to me!"
							else: message += getMessage(random.randint(1,6))
					else:
						message += getMessage(random.randint(1,6))
					
					self.twitter.tweet(message, lastid)
				else:
					print "Tweet was retweet or reply"
			time.sleep(30)
		self.reps.remove(u.id)
		self.endInstance(key)
	
	# auto reply to tweets you are mentioned in
	def mentionbot(self):
		self.instances['mentionbot'] = True
		print "Running MentionBot on %s" % self.user.screen_name
		twts = self.twitter.getMentions()
		if twts: lastmentionid = twts[0].id
		else: lastmentionid = 1
		time.sleep(60)
		while self.instances['mentionbot']:
			twts = self.twitter.getMentions(lastmentionid)
			for i in range(len(twts)-1, -1, -1): #backwards iterator
				newTweet = twts[i]
				if not newTweet.favorited: self.twitter.favorite(newTweet)
				lastmentionid = newTweet.id
				print "Mention found! lastid updated to "+str(lastmentionid)
				sentence = newTweet.text
				if newTweet.user.id not in self.reps:
					message = "@"+newTweet.user.screen_name+self.twitter.userMentions(newTweet)
					
					for word in self.rmatches:
						if re.search(word, sentence, re.I):
							message += random.sample(self.rmatches[word], 1)[0]
							break
					else:
						if random.randint(1,3) == 2: message += "Don't tweet at me!"
						else: message += getMessage(random.randint(1,6))
					if not newTweet.user.following and not newTweet.user.follow_request_sent: self.follow(newTweet.user)
					self.twitter.tweet(message, lastmentionid)
				else:
					print "Already replying to user"
			time.sleep(60)
		self.endInstance('mentionbot')

	# stop it simmons bot
	def stopbot(self, target):
		u = self.twitter.getUser(target)
		if not u:
			print target, "doesn't exist!"
			return
		self.reps.append(u.id)
		key = "stopbot-"+target
		self.instances[key] = True
		print "Running %s on %s" % (key, self.user.screen_name)
		twts = self.twitter.getTweets(target)
		lastid = twts[0].id
		time.sleep(30)
		while self.instances[key]:
			twts = self.twitter.getTweets(target, lastid)
			for i in range(len(twts)-1, -1, -1): #backwards iterator
				newTweet = twts[i]		
				lastid = newTweet.id
				print "Tweet found! lastid updated to "+str(lastid)
				s = newTweet.text
		
				if 'retweeted_status' not in newTweet._json and (newTweet.in_reply_to_screen_name == None or newTweet.in_reply_to_screen_name == self.user.screen_name):
					message = ".@"+target+self.twitter.userMentions(newTweet)
					matchedword = ""
					if newTweet.in_reply_to_screen_name == self.user.screen_name:
						for word in self.rmatches:
							if re.search(word, s, re.I):
								message += random.sample(self.rmatches[word], 1)[0]
								matchedword = re.search(word, s, re.I).group()
								break
						else:
							if random.randint(1,3) == 2: message += "Stop replying to me!"
							else: message += random.sample(self.replys, 1)[0]
					else:
						for word in self.matches:
							if re.search(word, s, re.I):
								message += random.sample(self.matches[word], 1)[0]
								matchedword = re.search(word, s, re.I).group()
								break
						else:
							message += random.sample(self.replys, 1)[0]
					
					message += " #StopItJakeSimmons"
					if matchedword == "": matchedword = random.sample(s.split(), 1)[0]
					self.twitter.tweet(message, lastid)
					self.twitter.tweet('Simmons tweeted and used the word "'+matchedword+'". You know what to do. #StopItJakeSimmons')
				else:
					print "Tweet was retweet or reply"
			time.sleep(30)
		self.reps.remove(u.id)
		self.endInstance(key)

# main
if __name__ == "__main__":
	twitterBot = TwitterBot(*tokens['I_am_cool5'])
	# twitterBot.start('followbot')
	#twitterBot.start('dmbot')
	twitterBot.start('mentionbot')
	# twitterBot.start('stopbot-jakesimmonsrock')
	
	# print dir(twts[0])
	# for i in twts[0]._json:
		# print i, "\t", twts[0]._json[i]
	print "Press enter to exit"
	
	exit = raw_input()
	