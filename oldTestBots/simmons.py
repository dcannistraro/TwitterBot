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
	
	followers = []
	instances = {}
	admins = ["d_rack7", "matthamel2"]
	reps = []
	botlist = ["followbot", "replybot", "mentionbot", "dmbot", "stopbot"]
	matches = keys.matches
	replys = keys.stop
	rmatches = keys.rmatches

	def __init__(self, at="", ats=""):
		self.access_token = at
		self.access_token_secret = ats
		self.twitter = TwitterAPI(self.access_token, self.access_token_secret)
		self.user = self.twitter.api.me()
		self.reps.append(self.user.id)
		
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
			
	def stop(self, key):
		if key in self.instances and self.instances[key]:
			self.instances[key] = False
			print key, "queued to stop"
			return True
		else:
			print "Can't stop %s: Doesn't exist or already stopped" % key
			return False
	
	def currentInstances(self):
		l = []
		for k in self.instances:
			if self.instances[k]: l.append(k)
		return l
			
	def endInstance(self, instance):
		print "Stopping %s on %s" % (instance, self.user.screen_name)
		del self.instances[instance]

	def makeadmin(self, newAdmin):
		newAdmin = newAdmin.lower()
		if newAdmin not in self.admins:
			self.admins.append(newAdmin)
			print newAdmin, "is now an admin of %s" % self.user.screen_name
		else:
			print newAdmin, "is is already an admin of %s" % self.user.screen_name
	
	def followbot(self):
		self.instances['followbot'] = True
		print "Running FollowBot on %s" % self.user.screen_name
		flwrs = self.twitter.getFollowers()
		for i in flwrs:
			self.followers.append(i.id)
			if not i.following:
				i.follow()
				print "Now following %s" % i.screen_name
		time.sleep(60*30)
		while self.instances['followbot']:
			flwrs = self.twitter.getFollowers()
			if len(flwrs) > len(self.followers):
				for i in range(len(flwrs) - len(self.followers)):
					self.twitter.follow(flwrs[i].screen_name)
					self.followers.append(flwrs[i].id)
			time.sleep(60*30)
		self.endInstance('followbot')

	def dmbot(self):
		file = open("keywords.txt", "w")
		keywords = ["say", "tweet", "follow", "key", "reply", "start", "stop"]
		self.instances['dmbot'] = True
		print "Running DMBot on %s" % self.user.screen_name
		dms = self.twitter.getDMs()
		if dms: lastDM = dms[0].id
		else: lastDM = 1
		time.sleep(60)
		while self.instances['dmbot']:
			dms = self.twitter.getDMs(lastDM)
			if len(dms):
				lastDM = dms[len(dms)-1].id
				target = dms[len(dms)-1].sender.screen_name
				sentence = dms[len(dms)-1].text
				s = sentence.replace("@", "").split()
				print "Found DM: %s" % sentence.encode('ascii', 'backslashreplace')
				if s[0].lower() in keywords and len(s) > 1:
					if random.randint(1,5) == 1:
						self.twitter.sendDM(target, "fuck off lahey: %s is loafing around" % self.user.screen_name)
					elif re.match("say", s[0], re.I):
						self.twitter.sendDM(target, sentence[len(s[0]):])
					elif re.match("tweet", s[0], re.I):
						self.twitter.tweet(sentence[len(s[0]):])
						self.twitter.sendDM(target, "Tweet sent!")
					elif re.match("follow", s[0], re.I):
						u = self.twitter.getUser(s[1])
						if u and not u.following:
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
						file.write("kw: %s, phrase: %s\n" % (s[1], s[2:]))
						self.twitter.sendDM(target, "New phrase added for keyword %s!" % s[1][2:])
					elif re.match("reply", s[0], re.I) and target.lower() in self.admins:
						if s[1:] not in self.replys:
							replys.append(s[1:])
							file.write("reply: %s\n" % s[1:])
							self.twitter.sendDM(target, "New reply added: %s..." % s[1:][:20])
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
					self.twitter.sendDM(target, "Sorry, I didn't understand that")
			time.sleep(60)
		file.close()
		self.endInstance('dmbot')
					
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
			if len(twts):
				newTweet = twts[len(twts)-1]		
				lastid = newTweet.id
				print "Tweet found! lastid updated to "+str(lastid)
				s = newTweet.text
				
				if 'retweeted_status' not in newTweet._json and newTweet.in_reply_to_screen_name == None or newTweet.in_reply_to_screen_name == self.user.screen_name:
					message = "@"+target+" "
					
					if newTweet.in_reply_to_screen_name == self.user.screen_name:
						for word in self.rmatches:
							if re.search(word, s, re.I):
								message += random.sample(self.rmatches[word], 1)[0]
								break
						else:
							if random.randint(1,3) == 2: message += "Stop replying to me!"
							message += getMessage(random.randint(1,6))
					else:
						message += getMessage(random.randint(1,6))
					
					self.twitter.tweet(message, lastid)
				else:
					print "Tweet was retweet or reply"
			time.sleep(30)
		self.reps.remove(u.id)
		self.endInstance(key)
	
	def mentionbot(self):
		self.instances['mentionbot'] = True
		print "Running MentionBot on %s" % self.user.screen_name
		twts = self.twitter.search(self.user.screen_name)
		lastmentionid = twts[0].id
		time.sleep(60)
		while self.instances['mentionbot']:
			twts = self.twitter.getMentions(lastmentionid)
			if len(twts):
				newTweet = twts[len(twts)-1]		
				lastmentionid = newTweet.id
				print "Mention found! lastid updated to "+str(lastmentionid)
				sentence = newTweet.text
				if newTweet.author.id not in self.reps:
					message = "@"+newTweet.author.screen_name+" You are not welcome here. Please refrain from using my name."
					self.twitter.follow(newTweet.author.screen_name)
					self.twitter.tweet(message, tweetid)
				else:
					print "Already replying to user"
			time.sleep(60)
		self.endInstance('mentionbot')

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
			if len(twts):
				newTweet = twts[len(twts)-1]		
				lastid = newTweet.id
				print "Tweet found! lastid updated to "+str(lastid)
				s = newTweet.text
		
				if 'retweeted_status' not in newTweet._json and newTweet.in_reply_to_screen_name == None or newTweet.in_reply_to_screen_name == self.user.screen_name:
					message = "@"+target+" "
					
					if newTweet.in_reply_to_screen_name == self.user.screen_name:
						for word in self.rmatches:
							if re.search(word, s, re.I):
								message += random.sample(self.rmatches[word], 1)[0]
								break
						else:
							if random.randint(1,3) == 2: message += "Stop replying to me!"
							message += random.sample(self.replys, 1)[0]
					else:
						for word in self.matches:
							if re.search(word, s, re.I):
								message += random.sample(self.matches[word], 1)[0]
								break
						else:
							message += random.sample(self.replys, 1)[0]
					
					message += " #StopItJakeSimmons"
					self.twitter.tweet(message, lastid)
					self.twitter.tweet('Simmons tweeted and used the word "'+random.sample(s.split(), 1)[0]+'". You know what to do. #StopItJakeSimmons')
				else:
					print "Tweet was retweet or reply"
			time.sleep(30)
		self.reps.remove(u.id)
		self.endInstance(key)
		
if __name__ == "__main__":
	twitterBot = TwitterBot(*tokens['StopitSimmons'])
	# twitterBot.start('followbot')
	twitterBot.start('dmbot')
	twitterBot.start('stopbot-jakesimmonsrock')
	# twts = twitterBot.twitter.getTweets()
	
	# print dir(twts[0])
	# for i in twts[0]._json:
		# print i, "\t", twts[0]._json[i]
	print "Press enter to exit"
	
	exit = raw_input()
	